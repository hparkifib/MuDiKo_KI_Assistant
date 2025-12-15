# 🚀 Quick Start: Refactoring Guide

Dieser Guide zeigt die **ersten konkreten Schritte** zur Umsetzung des Architektur-Optimierungsplans.

---

## 📁 Schritt 1: Neue Ordnerstruktur anlegen

```powershell
# Im Backend/app Ordner
cd Backend\app

# Core-Ordner
mkdir core
New-Item -Path "core\__init__.py" -ItemType File
New-Item -Path "core\app_factory.py" -ItemType File
New-Item -Path "core\config.py" -ItemType File
New-Item -Path "core\exceptions.py" -ItemType File

# Shared-Ordner
mkdir shared
mkdir shared\services
mkdir shared\models
mkdir shared\utils
New-Item -Path "shared\__init__.py" -ItemType File
New-Item -Path "shared\services\__init__.py" -ItemType File
New-Item -Path "shared\services\session_service.py" -ItemType File
New-Item -Path "shared\services\storage_service.py" -ItemType File
New-Item -Path "shared\services\audio_service.py" -ItemType File
New-Item -Path "shared\models\__init__.py" -ItemType File
New-Item -Path "shared\models\session.py" -ItemType File
New-Item -Path "shared\utils\__init__.py" -ItemType File

# Plugin-Ordner
mkdir plugins
mkdir plugins\base
mkdir plugins\audio_feedback
New-Item -Path "plugins\__init__.py" -ItemType File
New-Item -Path "plugins\base\__init__.py" -ItemType File
New-Item -Path "plugins\base\plugin_interface.py" -ItemType File
New-Item -Path "plugins\base\plugin_manager.py" -ItemType File
New-Item -Path "plugins\audio_feedback\__init__.py" -ItemType File
New-Item -Path "plugins\audio_feedback\plugin.py" -ItemType File
New-Item -Path "plugins\audio_feedback\config.yaml" -ItemType File
```

---

## 📝 Schritt 2: Basis-Klassen implementieren

### 2.1 Session Model

```python
# shared/models/session.py
from datetime import datetime, timedelta
from pathlib import Path
import shutil
from typing import Optional

class Session:
    """Repräsentiert eine User-Session mit Lebenszyklus."""
    
    def __init__(self, session_id: str, base_path: Path, ttl_seconds: int):
        self.session_id = session_id
        self.base_path = base_path
        self.ttl_seconds = ttl_seconds
        self.created_at = datetime.now()
        self.last_access = datetime.now()
        self.data = {}  # Optionale Session-Daten
        
        # Erstelle Session-Ordner
        self.path = base_path / session_id
        self.path.mkdir(parents=True, exist_ok=True)
    
    def touch(self):
        """Aktualisiert den letzten Zugriffszeitpunkt."""
        self.last_access = datetime.now()
    
    def is_expired(self) -> bool:
        """Prüft ob die Session abgelaufen ist."""
        expires_at = self.last_access + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expires_at
    
    def cleanup(self):
        """Löscht alle Session-Daten."""
        if self.path.exists():
            shutil.rmtree(self.path, ignore_errors=True)
    
    def get_file_path(self, filename: str) -> Path:
        """Gibt den Pfad zu einer Datei in der Session zurück."""
        return self.path / filename
    
    def __repr__(self):
        return f"Session(id={self.session_id}, expired={self.is_expired()})"
```

### 2.2 Custom Exceptions

```python
# core/exceptions.py
class MuDiKoException(Exception):
    """Basis-Exception für alle Custom Exceptions."""
    pass

class SessionNotFoundException(MuDiKoException):
    """Session wurde nicht gefunden."""
    pass

class SessionExpiredException(MuDiKoException):
    """Session ist abgelaufen."""
    pass

class InvalidFileFormatException(MuDiKoException):
    """Ungültiges Dateiformat."""
    pass

class PluginNotFoundException(MuDiKoException):
    """Plugin wurde nicht gefunden."""
    pass

class PluginInitializationException(MuDiKoException):
    """Fehler beim Initialisieren eines Plugins."""
    pass
```

### 2.3 Session Service

```python
# shared/services/session_service.py
from typing import Optional, Dict
from pathlib import Path
import threading
import time
from ..models.session import Session
from ...core.exceptions import SessionNotFoundException, SessionExpiredException
import uuid

class SessionService:
    """Verwaltet User-Sessions thread-safe."""
    
    def __init__(self, base_path: str, ttl_seconds: int = 3600, gc_interval: int = 900):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self.gc_interval = gc_interval
        
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()
        
        # Starte Garbage Collector
        self._start_gc()
    
    def create_session(self) -> Session:
        """Erstellt eine neue Session.
        
        Returns:
            Session: Neu erstellte Session-Instanz
        """
        session_id = uuid.uuid4().hex
        session = Session(session_id, self.base_path, self.ttl_seconds)
        
        with self._lock:
            self._sessions[session_id] = session
        
        return session
    
    def get_session(self, session_id: str, touch: bool = True) -> Session:
        """Holt eine Session und validiert sie.
        
        Args:
            session_id: Die Session-ID
            touch: Ob last_access aktualisiert werden soll
            
        Returns:
            Session: Die gefundene Session
            
        Raises:
            SessionNotFoundException: Wenn Session nicht existiert
            SessionExpiredException: Wenn Session abgelaufen ist
        """
        with self._lock:
            session = self._sessions.get(session_id)
        
        if not session:
            raise SessionNotFoundException(f"Session {session_id} nicht gefunden")
        
        if session.is_expired():
            self.end_session(session_id)
            raise SessionExpiredException(f"Session {session_id} ist abgelaufen")
        
        if touch:
            session.touch()
        
        return session
    
    def end_session(self, session_id: str) -> bool:
        """Beendet eine Session und räumt auf.
        
        Args:
            session_id: Die zu beendende Session-ID
            
        Returns:
            bool: True wenn erfolgreich, False wenn Session nicht existierte
        """
        with self._lock:
            session = self._sessions.pop(session_id, None)
        
        if session:
            session.cleanup()
            return True
        return False
    
    def cleanup_expired(self):
        """Entfernt alle abgelaufenen Sessions."""
        with self._lock:
            expired_ids = [
                sid for sid, sess in self._sessions.items() 
                if sess.is_expired()
            ]
        
        for sid in expired_ids:
            self.end_session(sid)
        
        return len(expired_ids)
    
    def get_session_count(self) -> int:
        """Gibt die Anzahl aktiver Sessions zurück."""
        with self._lock:
            return len(self._sessions)
    
    def _start_gc(self):
        """Startet den Garbage Collector Thread."""
        def gc_loop():
            while True:
                time.sleep(self.gc_interval)
                try:
                    cleaned = self.cleanup_expired()
                    if cleaned > 0:
                        print(f"🗑️ {cleaned} abgelaufene Session(s) entfernt")
                except Exception as e:
                    print(f"❌ GC Fehler: {e}")
        
        gc_thread = threading.Thread(target=gc_loop, daemon=True)
        gc_thread.start()
```

### 2.4 Storage Service

```python
# shared/services/storage_service.py
from pathlib import Path
from typing import List, Optional, BinaryIO
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from ...core.exceptions import InvalidFileFormatException

class StorageService:
    """Verwaltet Dateispeicherung und -zugriff."""
    
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'midi', 'mid'}
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file: FileStorage, session_id: str, 
                  filename: Optional[str] = None, 
                  role: Optional[str] = None) -> Path:
        """Speichert eine hochgeladene Datei.
        
        Args:
            file: Flask FileStorage-Objekt
            session_id: Session-ID für Speicherort
            filename: Optionaler Zieldateiname
            role: Optionale Rolle (z.B. 'referenz', 'schueler')
            
        Returns:
            Path: Pfad zur gespeicherten Datei
            
        Raises:
            InvalidFileFormatException: Bei ungültigem Dateiformat
        """
        # Validiere Dateiformat
        if not self._is_allowed_file(file.filename):
            raise InvalidFileFormatException(
                f"Dateiformat nicht erlaubt: {file.filename}"
            )
        
        # Bestimme Zieldateinamen
        if role:
            # Bei Rolle: standardisierter Name (z.B. 'referenz.mp3')
            ext = self._get_extension(file.filename)
            target_filename = f"{role}.{ext}"
        elif filename:
            target_filename = secure_filename(filename)
        else:
            target_filename = secure_filename(file.filename)
        
        # Erstelle Session-Ordner
        session_dir = self.base_path / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Speichere Datei
        file_path = session_dir / target_filename
        file.save(str(file_path))
        
        return file_path
    
    def get_file_path(self, session_id: str, filename: str) -> Optional[Path]:
        """Gibt den Pfad zu einer Datei zurück.
        
        Args:
            session_id: Session-ID
            filename: Dateiname
            
        Returns:
            Optional[Path]: Pfad zur Datei oder None wenn nicht vorhanden
        """
        file_path = self.base_path / session_id / filename
        return file_path if file_path.exists() else None
    
    def list_files(self, session_id: str, pattern: str = "*") -> List[str]:
        """Listet alle Dateien in einer Session.
        
        Args:
            session_id: Session-ID
            pattern: Glob-Pattern für Filterung (z.B. "*.mp3")
            
        Returns:
            List[str]: Liste der Dateinamen
        """
        session_dir = self.base_path / session_id
        if not session_dir.exists():
            return []
        
        return [f.name for f in session_dir.glob(pattern) if f.is_file()]
    
    def delete_file(self, session_id: str, filename: str) -> bool:
        """Löscht eine einzelne Datei.
        
        Args:
            session_id: Session-ID
            filename: Zu löschende Datei
            
        Returns:
            bool: True wenn erfolgreich gelöscht
        """
        file_path = self.base_path / session_id / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def delete_all_files(self, session_id: str):
        """Löscht alle Dateien einer Session.
        
        Args:
            session_id: Session-ID
        """
        session_dir = self.base_path / session_id
        if session_dir.exists():
            for file_path in session_dir.iterdir():
                if file_path.is_file():
                    try:
                        file_path.unlink()
                    except Exception:
                        pass
    
    def _is_allowed_file(self, filename: str) -> bool:
        """Prüft ob Dateiformat erlaubt ist."""
        return '.' in filename and \
               self._get_extension(filename) in self.ALLOWED_EXTENSIONS
    
    def _get_extension(self, filename: str) -> str:
        """Extrahiert die Dateierweiterung."""
        return filename.rsplit('.', 1)[1].lower()
```

---

## 🔧 Schritt 3: Config System

### 3.1 Config Klasse

```python
# core/config.py
import os
from pathlib import Path
import yaml

class Config:
    """Basis-Konfiguration."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '104857600'))  # 100 MB
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000')
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_FOLDER = BASE_DIR / "Uploads"
    PLUGINS_DIR = BASE_DIR / "plugins"
    CONFIG_DIR = BASE_DIR.parent.parent / "config"
    
    # Session
    SESSION_TTL_SECONDS = int(os.getenv('SESSION_TTL_SECONDS', '3600'))
    SESSION_GC_INTERVAL = int(os.getenv('GC_INTERVAL_SECONDS', '900'))
    
    # Audio Processing
    AUDIO_TARGET_SR = 22050
    AUDIO_TARGET_LENGTH = 60
    AUDIO_SEGMENT_LENGTH = 8
    
    @classmethod
    def load_plugin_config(cls, plugin_name: str) -> dict:
        """Lädt die Konfiguration für ein Plugin."""
        config_file = cls.PLUGINS_DIR / plugin_name / "config.yaml"
        if config_file.exists():
            with open(config_file) as f:
                return yaml.safe_load(f)
        return {}

class DevelopmentConfig(Config):
    """Entwicklungs-Konfiguration."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Produktions-Konfiguration."""
    DEBUG = False
    TESTING = False
    
    # In Produktion: Strengere Einstellungen
    SESSION_TTL_SECONDS = 1800  # 30 Minuten

class TestingConfig(Config):
    """Test-Konfiguration."""
    TESTING = True
    DEBUG = True

def get_config():
    """Gibt die Config basierend auf Environment zurück."""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
```

### 3.2 Audio Feedback Plugin Config

```yaml
# plugins/audio_feedback/config.yaml
enabled: true
class: AudioFeedbackPlugin
display_name: Audio Feedback Analyzer
description: Vergleicht Musikaufnahmen und gibt intelligentes Feedback
version: 1.0.0
icon: /icons/audio-feedback.svg

# Frontend Routes
frontend_routes:
  - /tools/audio-feedback/upload
  - /tools/audio-feedback/recordings
  - /tools/audio-feedback/language
  - /tools/audio-feedback/instruments
  - /tools/audio-feedback/personalization
  - /tools/audio-feedback/prompt

# Tool-spezifische Einstellungen
settings:
  max_file_size_mb: 100
  allowed_formats:
    - mp3
    - wav
    - mp4
  
  # Audio Processing
  segment_length_sec: 8
  default_sample_rate: 22050
  target_length_sec: 60
  
  # Analyse Features
  analysis_features:
    - tempo
    - pitch
    - dynamics
    - loudness
    - spectral_centroid
    - onset_count
    - rhythm_stability
    - spectral_bandwidth
    - spectral_rolloff
    - silences
    - zero_crossing_rate
    - mfcc
    - chroma_key
    - chord_histogram
    - attack_time
    - vibrato
    - timbre_consistency
    - polyphony
  
  # Vergleichs-Metriken
  comparison_metrics:
    - mfcc_distance
    - chroma_similarity
    - rms_correlation
    - dtw_distance
    - energy_envelope_correlation
    - pitch_contour_correlation
  
  # Feedback Optionen
  feedback:
    default_language: english
    supported_languages:
      - deutsch
      - english
      - español
      - français
      - italiano
      - türkçe
    prompt_types:
      - contextual
      - data_only
```

---

## 🔌 Schritt 4: Plugin Interface

```python
# plugins/base/plugin_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from flask import Blueprint

class MusicToolPlugin(ABC):
    """Abstract Base Class für alle Musik-Tool-Plugins.
    
    Jedes Tool-Plugin muss diese Schnittstelle implementieren.
    Dies ermöglicht einheitliche Integration in das Core-System.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Eindeutiger interner Name des Tools (URL-safe).
        
        Beispiel: 'audio-feedback', 'midi-tool'
        """
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Versionsnummer des Tools (Semantic Versioning).
        
        Beispiel: '1.0.0'
        """
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Anzeigename für UI.
        
        Beispiel: 'Audio Feedback Analyzer'
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Kurzbeschreibung des Tools."""
        pass
    
    @abstractmethod
    def initialize(self, app_context: Dict[str, Any]):
        """Initialisiert das Plugin mit App-Kontext.
        
        Args:
            app_context: Dictionary mit shared services:
                - 'session_service': SessionService instance
                - 'storage_service': StorageService instance
                - 'audio_service': AudioService instance (optional)
                - 'config': Config instance
        """
        pass
    
    @abstractmethod
    def get_blueprint(self) -> Blueprint:
        """Gibt Flask Blueprint mit allen Routes zurück.
        
        Returns:
            Blueprint: Flask Blueprint mit Tool-spezifischen Endpoints
        """
        pass
    
    @abstractmethod
    def get_frontend_routes(self) -> List[str]:
        """Gibt Frontend-Route-Pfade für dieses Tool zurück.
        
        Returns:
            List[str]: Liste der Frontend-Pfade
            
        Beispiel:
            ['/tools/audio-feedback/upload', '/tools/audio-feedback/analyze']
        """
        pass
    
    def get_dependencies(self) -> List[str]:
        """Gibt Plugin-Abhängigkeiten zurück (optional).
        
        Returns:
            List[str]: Liste von Plugin-Namen die benötigt werden
        """
        return []
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Gibt Config-Schema für Tool-spezifische Settings zurück (optional).
        
        Returns:
            Dict: JSON-Schema für Validierung
        """
        return {}
    
    def get_icon(self) -> Optional[str]:
        """Gibt Icon-Pfad für Tool zurück (optional).
        
        Returns:
            Optional[str]: Pfad zum Icon oder None
        """
        return None
    
    def health_check(self) -> Dict[str, Any]:
        """Prüft den Status des Plugins (optional).
        
        Returns:
            Dict: Status-Information
        """
        return {
            'status': 'ok',
            'name': self.name,
            'version': self.version
        }
    
    def cleanup(self):
        """Cleanup beim Shutdown (optional)."""
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', version='{self.version}')>"
```

---

## 📦 Schritt 5: Plugin Manager

```python
# plugins/base/plugin_manager.py
import importlib
from typing import Dict, List, Optional
from pathlib import Path
import yaml

from .plugin_interface import MusicToolPlugin
from ...core.exceptions import PluginNotFoundException, PluginInitializationException

class PluginManager:
    """Verwaltet alle Tool-Plugins."""
    
    def __init__(self, plugins_dir: Path, app_context: Dict):
        self.plugins_dir = plugins_dir
        self.app_context = app_context
        self._plugins: Dict[str, MusicToolPlugin] = {}
        self._enabled_plugins: List[str] = []
    
    def discover_and_load_plugins(self):
        """Findet und lädt alle verfügbaren Plugins."""
        if not self.plugins_dir.exists():
            print(f"⚠️ Plugin-Verzeichnis nicht gefunden: {self.plugins_dir}")
            return
        
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                if item.name != 'base':  # Skip base module
                    self._load_plugin(item)
        
        print(f"✅ {len(self._plugins)} Plugin(s) geladen: {', '.join(self._plugins.keys())}")
    
    def _load_plugin(self, plugin_dir: Path):
        """Lädt ein einzelnes Plugin."""
        config_file = plugin_dir / 'config.yaml'
        
        # Config muss existieren
        if not config_file.exists():
            print(f"⚠️ Plugin {plugin_dir.name}: config.yaml nicht gefunden")
            return
        
        try:
            # Lade Config
            with open(config_file) as f:
                config = yaml.safe_load(f)
            
            # Plugin nur laden wenn aktiviert
            if not config.get('enabled', True):
                print(f"⏭️ Plugin {plugin_dir.name}: deaktiviert")
                return
            
            # Importiere Plugin-Modul
            plugin_module = plugin_dir.name
            module = importlib.import_module(f'plugins.{plugin_module}.plugin')
            
            # Hol Plugin-Klasse
            plugin_class_name = config.get('class')
            if not plugin_class_name:
                print(f"❌ Plugin {plugin_module}: 'class' fehlt in config.yaml")
                return
            
            plugin_class = getattr(module, plugin_class_name)
            plugin_instance = plugin_class()
            
            # Initialisiere Plugin
            plugin_instance.initialize(self.app_context)
            
            # Registriere Plugin
            self._plugins[plugin_instance.name] = plugin_instance
            self._enabled_plugins.append(plugin_instance.name)
            
            print(f"✅ Plugin geladen: {plugin_instance.display_name} v{plugin_instance.version}")
        
        except Exception as e:
            print(f"❌ Fehler beim Laden von {plugin_dir.name}: {e}")
            raise PluginInitializationException(f"Plugin {plugin_dir.name} konnte nicht geladen werden: {e}")
    
    def get_plugin(self, name: str) -> MusicToolPlugin:
        """Gibt ein Plugin nach Name zurück.
        
        Args:
            name: Interner Plugin-Name
            
        Returns:
            MusicToolPlugin: Plugin-Instanz
            
        Raises:
            PluginNotFoundException: Wenn Plugin nicht existiert
        """
        plugin = self._plugins.get(name)
        if not plugin:
            raise PluginNotFoundException(f"Plugin '{name}' nicht gefunden")
        return plugin
    
    def get_all_plugins(self) -> List[MusicToolPlugin]:
        """Gibt alle geladenen Plugins zurück."""
        return list(self._plugins.values())
    
    def get_enabled_plugins(self) -> List[str]:
        """Gibt Liste der aktivierten Plugin-Namen zurück."""
        return self._enabled_plugins.copy()
    
    def register_blueprints(self, app):
        """Registriert alle Plugin-Blueprints bei Flask.
        
        Args:
            app: Flask app instance
        """
        for plugin in self._plugins.values():
            try:
                blueprint = plugin.get_blueprint()
                url_prefix = f'/api/tools/{plugin.name}'
                app.register_blueprint(blueprint, url_prefix=url_prefix)
                print(f"✅ Blueprint registriert: {url_prefix}")
            except Exception as e:
                print(f"❌ Fehler bei Blueprint-Registrierung für {plugin.name}: {e}")
    
    def get_plugins_info(self) -> List[Dict]:
        """Gibt Info über alle Plugins für API zurück."""
        return [
            {
                'name': plugin.name,
                'display_name': plugin.display_name,
                'description': plugin.description,
                'version': plugin.version,
                'icon': plugin.get_icon(),
                'frontend_routes': plugin.get_frontend_routes()
            }
            for plugin in self._plugins.values()
        ]
    
    def cleanup_all(self):
        """Cleanup für alle Plugins beim Shutdown."""
        for plugin in self._plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                print(f"⚠️ Cleanup-Fehler für {plugin.name}: {e}")
```

---

## 🚀 Schritt 6: Neue main.py (minimal)

```python
# app/main.py (NEU - minimale Version)
from flask import Flask
from flask_cors import CORS
from core.config import get_config
from core.app_factory import create_app

# Erstelle App mit Factory Pattern
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

```python
# core/app_factory.py
from flask import Flask, jsonify
from flask_cors import CORS
from pathlib import Path

from .config import get_config
from ..shared.services.session_service import SessionService
from ..shared.services.storage_service import StorageService
from ..shared.services.audio_service import AudioService
from ..plugins.base.plugin_manager import PluginManager

def create_app(config_name: str = None):
    """Factory Function zur App-Erstellung."""
    
    # Flask App erstellen
    app = Flask(__name__)
    
    # Config laden
    config_class = get_config()
    app.config.from_object(config_class)
    
    # CORS konfigurieren
    origins = [o.strip() for o in app.config['CORS_ORIGINS'].split(',')]
    CORS(app, origins=origins)
    
    # Shared Services initialisieren
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
    
    # App Context für Plugins
    app_context = {
        'session_service': session_service,
        'storage_service': storage_service,
        'audio_service': audio_service,
        'config': config_class
    }
    
    # Plugin Manager erstellen und Plugins laden
    plugin_manager = PluginManager(
        plugins_dir=app.config['PLUGINS_DIR'],
        app_context=app_context
    )
    plugin_manager.discover_and_load_plugins()
    plugin_manager.register_blueprints(app)
    
    # Store in app für späteren Zugriff
    app.plugin_manager = plugin_manager
    app.session_service = session_service
    
    # Core API Routes registrieren
    register_core_routes(app, session_service, plugin_manager)
    
    return app

def register_core_routes(app, session_service, plugin_manager):
    """Registriert Core-API-Routes."""
    
    @app.route("/api/health")
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "MuDiKo API is running",
            "plugins": len(plugin_manager.get_enabled_plugins())
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
        session = session_service.create_session()
        return jsonify({
            "success": True,
            "sessionId": session.session_id,
            "ttl": session.ttl_seconds
        })
    
    @app.route("/api/session/end", methods=["POST"])
    def session_end():
        from flask import request
        data = request.json or {}
        session_id = data.get("sessionId")
        
        if not session_id:
            return jsonify({"success": False, "error": "sessionId fehlt"}), 400
        
        success = session_service.end_session(session_id)
        return jsonify({"success": success})
```

---

## ✅ Nächste Schritte

1. **Testen Sie die neue Struktur:**
   ```powershell
   cd Backend
   python -m app.main
   ```

2. **Migrieren Sie AudioManager und AudioFeedbackPipeline:**
   - `AudioManager` → wird Teil von `StorageService` und `AudioService`
   - `AudioFeedbackPipeline` → wird `AudioFeedbackService` im Plugin

3. **Erstellen Sie das erste Plugin:**
   - Implementieren Sie `AudioFeedbackPlugin`
   - Testen Sie mit `/api/tools` ob es erkannt wird

4. **Frontend anpassen:**
   - Tool-Auswahl Homepage erstellen
   - Hooks für Session und Upload

---

## 📊 Erfolgs-Metriken

Nach der Refactoring:
- ✅ `main.py` < 50 Zeilen (statt 412)
- ✅ Neue Services < 200 Zeilen pro Datei
- ✅ Plugin hinzufügen ohne Core-Code zu ändern
- ✅ Alle Tests grün

Viel Erfolg! 🚀
