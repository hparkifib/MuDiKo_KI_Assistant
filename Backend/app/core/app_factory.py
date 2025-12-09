# App Factory - Erstellt und konfiguriert die Flask App

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path

from app.core.config import get_config
from app.shared.services.session_service import SessionService
from app.shared.services.storage_service import StorageService
from app.shared.services.audio_service import AudioService
from app.plugins.base.plugin_manager import PluginManager
from app.core.exceptions import SessionNotFoundException, SessionExpiredException

def create_app(config_name: str = None):
    """Factory Function zur App-Erstellung.
    
    Args:
        config_name: Optional - Name der Config-Klasse
        
    Returns:
        Flask: Konfigurierte Flask App
    """
    
    # Flask App erstellen
    app = Flask(__name__)
    
    # Config laden
    config_class = get_config()
    app.config.from_object(config_class)
    
    print(f"🚀 MuDiKo KI Assistant startet...")
    print(f"📝 Environment: {config_class.__name__}")
    
    # CORS konfigurieren
    origins = [o.strip() for o in app.config['CORS_ORIGINS'].split(',')]
    CORS(app, origins=origins)
    print(f"🌐 CORS konfiguriert: {', '.join(origins)}")
    
    # Shared Services initialisieren
    print(f"🔧 Initialisiere Services...")
    
    session_service = SessionService(
        base_path=str(app.config['UPLOAD_FOLDER']),
        ttl_seconds=app.config['SESSION_TTL_SECONDS'],
        gc_interval=app.config['SESSION_GC_INTERVAL']
    )
    
    storage_service = StorageService(
        base_path=str(app.config['UPLOAD_FOLDER'])
    )
    
    audio_service = AudioService(
        target_sr=app.config['AUDIO_TARGET_SR']
    )
    
    print(f"✅ Services initialisiert")
    
    # App Context für Plugins
    app_context = {
        'session_service': session_service,
        'storage_service': storage_service,
        'audio_service': audio_service,
        'config': config_class
    }
    
    # Plugin Manager erstellen und Plugins laden
    print(f"🔌 Lade Plugins...")
    plugin_manager = PluginManager(
        plugins_dir=app.config['PLUGINS_DIR'],
        app_context=app_context
    )
    plugin_manager.discover_and_load_plugins()
    plugin_manager.register_blueprints(app)
    
    # Store in app für späteren Zugriff
    app.plugin_manager = plugin_manager
    app.session_service = session_service
    app.storage_service = storage_service
    
    # Core API Routes registrieren
    register_core_routes(app, session_service, storage_service, plugin_manager)
    
    print(f"✅ MuDiKo KI Assistant bereit!")
    
    return app

def register_core_routes(app, session_service, storage_service, plugin_manager):
    """Registriert Core-API-Routes.
    
    Args:
        app: Flask app
        session_service: SessionService instance
        storage_service: StorageService instance
        plugin_manager: PluginManager instance
    """
    
    @app.route("/api/health")
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "ok",
            "message": "MuDiKo API is running",
            "plugins": len(plugin_manager.get_enabled_plugins()),
            "active_sessions": session_service.get_session_count()
        })
    
    @app.route("/api/tools")
    def list_tools():
        """Gibt alle verfügbaren Tools zurück."""
        return jsonify({
            "success": True,
            "tools": plugin_manager.get_plugins_info()
        })
    
    @app.route("/api/session/start", methods=["POST"])
    def session_start():
        """Startet eine neue Session."""
        try:
            session = session_service.create_session()
            return jsonify({
                "success": True,
                "sessionId": session.session_id,
                "ttl": session.ttl_seconds
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route("/api/session/end", methods=["POST"])
    def session_end():
        """Beendet eine Session."""
        data = request.json or {}
        session_id = data.get("sessionId")
        
        if not session_id:
            return jsonify({
                "success": False, 
                "error": "sessionId fehlt"
            }), 400
        
        success = session_service.end_session(session_id)
        return jsonify({"success": success})
    
    @app.route('/api/audio/<filename>')
    def serve_audio(filename):
        """Serviert Audio-Dateien (mit Session-Check)."""
        session_id = request.headers.get("X-Session-ID") or request.args.get("sessionId")
        
        if not session_id:
            return jsonify({
                "success": False, 
                "error": "sessionId fehlt"
            }), 400
        
        try:
            # Validiere Session
            session = session_service.get_session(session_id)
            
            # Prüfe ob Datei existiert
            file_path = storage_service.get_file_path(session_id, filename)
            if not file_path:
                # Prüfe auch im segments Unterordner
                file_path = storage_service.get_file_path(session_id, f"segments/{filename}")
            
            if not file_path:
                return jsonify({
                    "success": False, 
                    "error": "Datei nicht gefunden"
                }), 404
            
            # Serviere Datei
            return send_from_directory(file_path.parent, file_path.name)
            
        except (SessionNotFoundException, SessionExpiredException) as e:
            return jsonify({
                "success": False, 
                "error": str(e)
            }), 401
        except Exception as e:
            return jsonify({
                "success": False, 
                "error": str(e)
            }), 500
    
    # Error Handler
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "error": "Endpoint nicht gefunden"
        }), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "success": False,
            "error": "Interner Server-Fehler"
        }), 500
