"""MP3-to-MIDI Converter Routes - API Endpoints."""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from app.core.exceptions import SessionNotFoundException, SessionExpiredException, InvalidFileFormatException


def create_routes(plugin_name, session_service, storage_service, feedback_service, plugin_config) -> Blueprint:
    """Erstellt Blueprint mit allen Routes für MP3-to-MIDI Converter.
    
    Args:
        plugin_name: Name des Plugins
        session_service: SessionService instance
        storage_service: StorageService instance
        feedback_service: Mp3ToMidiFeedbackService instance
        plugin_config: Plugin-Konfiguration
        
    Returns:
        Blueprint: Flask Blueprint mit allen Endpoints
    """
    
    bp = Blueprint('mp3_to_midi_feedback', __name__)
    
    # Hole Settings aus Config
    settings = plugin_config.get('settings', {})
    max_file_size_mb = settings.get('max_file_size_mb', 100)
    allowed_formats = settings.get('allowed_formats', ['mp3', 'wav', 'mp4'])
    
    @bp.route('/upload', methods=['POST'])
    def upload_audio():
        """Upload von Referenz- und Schüler-MP3-Aufnahmen.
        
        Form-Data:
            referenz: Referenz-Audio-Datei
            schueler: Schüler-Audio-Datei
            
        Headers:
            X-Session-ID: Session-ID (optional, wird automatisch erstellt)
            
        Returns:
            JSON Response mit Upload-Status und Session-ID
        """
        # Session-ID holen oder erstellen
        session_id = request.headers.get("X-Session-ID") or request.args.get("sessionId")
        if not session_id:
            session = session_service.create_session()
            session_id = session.session_id
        else:
            try:
                session = session_service.get_session(session_id)
            except (SessionNotFoundException, SessionExpiredException):
                session = session_service.create_session()
                session_id = session.session_id
        
        try:
            # Lösche vorherige Dateien
            storage_service.delete_all_files(session_id)
            
            files = request.files
            
            # Validierung: Beide Dateien müssen vorhanden sein
            if "referenz" not in files or "schueler" not in files:
                return jsonify({
                    "error": "Bitte beide Audiodateien hochladen (Referenz und Schüler).",
                    "success": False
                }), 400
            
            referenz_file = files["referenz"]
            schueler_file = files["schueler"]
            
            # Validierung: Dateien dürfen nicht leer sein
            if referenz_file.filename == '' or schueler_file.filename == '':
                return jsonify({
                    "error": "Eine oder beide Dateien sind leer.",
                    "success": False
                }), 400
            
            # Speichere Original-Dateinamen in Session
            session.set_data('original_filenames', {
                "referenz": referenz_file.filename,
                "schueler": schueler_file.filename
            })
            
            # Speichere Dateien mit Rollen
            referenz_file.filename = secure_filename(referenz_file.filename)
            schueler_file.filename = secure_filename(schueler_file.filename)
            
            referenz_path = storage_service.save_file(referenz_file, session_id, role="referenz")
            schueler_path = storage_service.save_file(schueler_file, session_id, role="schueler")
            
            # Erstelle File-Map
            file_map = {
                "referenz": referenz_path.name,
                "schueler": schueler_path.name
            }
            
            original_filenames = session.get_data('original_filenames', {})
            
            return jsonify({
                "success": True,
                "message": "Dateien erfolgreich hochgeladen",
                "sessionId": session_id,
                "files": {
                    "referenz": {
                        "stored_name": file_map["referenz"],
                        "original_name": original_filenames.get("referenz", "")
                    },
                    "schueler": {
                        "stored_name": file_map["schueler"],
                        "original_name": original_filenames.get("schueler", "")
                    }
                }
            }), 200
            
        except InvalidFileFormatException as e:
            return jsonify({
                "error": str(e),
                "success": False
            }), 400
        except Exception as e:
            return jsonify({
                "error": f"Upload fehlgeschlagen: {str(e)}",
                "success": False
            }), 500
    
    @bp.route('/convert', methods=['POST'])
    def convert():
        """Konvertiert beide MP3s zu MIDI via Basic Pitch.
        
        JSON Body:
            sessionId: Session-ID
            presetId: Optional - ID des zu verwendenden Presets (z.B. 'klavier')
            
        Returns:
            JSON Response mit Konversions-Status
        """
        try:
            data = request.get_json()
            session_id = data.get("sessionId")
            preset_id = data.get("presetId")  # Optional
            
            if not session_id:
                return jsonify({
                    "error": "Keine Session-ID angegeben",
                    "success": False
                }), 400
            
            # Validiere Session
            try:
                session = session_service.get_session(session_id)
            except (SessionNotFoundException, SessionExpiredException) as e:
                return jsonify({
                    "error": str(e),
                    "success": False
                }), 404
            
            # Rufe Service für Konversion auf (mit optional Preset)
            result = feedback_service.convert_mp3_to_midi(session_id, preset_id)
            
            return jsonify({
                "success": True,
                "message": "MP3-Dateien erfolgreich zu MIDI konvertiert",
                "sessionId": session_id,
                "result": result
            }), 200
            
        except Exception as e:
            return jsonify({
                "error": f"Konversion fehlgeschlagen: {str(e)}",
                "success": False
            }), 500
    
    @bp.route('/presets', methods=['GET'])
    def get_presets():
        """Gibt alle verfügbaren Conversion-Presets zurück.
        
        Returns:
            JSON Response mit Liste aller Presets
        """
        try:
            from app.plugins.mp3_to_midi_feedback.presets import list_presets
            
            presets = list_presets()
            
            return jsonify({
                "success": True,
                "presets": presets
            }), 200
            
        except Exception as e:
            return jsonify({
                "error": f"Fehler beim Laden der Presets: {str(e)}",
                "success": False
            }), 500
    
    @bp.route('/preset/<preset_id>', methods=['GET'])
    def get_preset(preset_id):
        """Gibt ein einzelnes Preset mit allen Details zurück.
        
        Args:
            preset_id: ID des Presets (z.B. 'klavier', 'gesang')
            
        Returns:
            JSON Response mit Preset-Details
        """
        try:
            from app.plugins.mp3_to_midi_feedback.presets import get_preset as load_preset
            
            preset = load_preset(preset_id)
            
            return jsonify({
                "success": True,
                "preset": preset
            }), 200
            
        except FileNotFoundError:
            return jsonify({
                "error": f"Preset '{preset_id}' nicht gefunden",
                "success": False
            }), 404
        except Exception as e:
            return jsonify({
                "error": f"Fehler beim Laden des Presets: {str(e)}",
                "success": False
            }), 500
    
    @bp.route('/session/cleanup', methods=['POST'])
    def cleanup_session():
        """Löscht Session und alle zugehörigen Dateien.
        
        JSON Body:
            sessionId: Session-ID
            
        Returns:
            JSON Response mit Cleanup-Status
        """
        try:
            data = request.get_json()
            session_id = data.get("sessionId")
            
            if not session_id:
                return jsonify({
                    "error": "Keine Session-ID angegeben",
                    "success": False
                }), 400
            
            # Lösche alle Dateien
            storage_service.delete_all_files(session_id)
            
            # Lösche Session
            session_service.delete_session(session_id)
            
            return jsonify({
                "success": True,
                "message": "Session erfolgreich gelöscht"
            }), 200
            
        except Exception as e:
            return jsonify({
                "error": f"Cleanup fehlgeschlagen: {str(e)}",
                "success": False
            }), 500
    
    return bp
