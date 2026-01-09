"""Easy Feedback Plugin - Vereinfachte Pipeline für den Unterrichtseinsatz."""

from pathlib import Path
from typing import Dict, Any, Optional, List

from app.plugins.base.plugin_interface import MusicToolPlugin


class EasyFeedbackPlugin(MusicToolPlugin):
    """Plugin für vereinfachtes Audio-Feedback.
    
    Linearer Workflow:
    1. Audio hochladen oder aufnehmen (Referenz + Schüler)
    2. Sprache & Personalisierung einstellen
    3. Feedback generieren (mit optionalem MIDI-Download)
    """
    
    def __init__(self):
        """Initialisiert das Plugin."""
        self._name = "easy-feedback"
        self._display_name = "Easy Feedback"
        self._version = "1.0.0"
        self._description = "Vereinfachte Audio-Feedback-Pipeline für den Unterrichtseinsatz"
        self.config = {}
        self.app_context = None
        self.service = None
        self.blueprint = None
    
    @property
    def name(self) -> str:
        """Eindeutiger interner Name des Tools."""
        return self._name
    
    @property
    def version(self) -> str:
        """Versionsnummer des Tools."""
        return self._version
    
    @property
    def display_name(self) -> str:
        """Anzeigename für UI."""
        return self._display_name
    
    @property
    def description(self) -> str:
        """Kurzbeschreibung des Tools."""
        return self._description
    
    def get_frontend_routes(self) -> List[str]:
        """Gibt Frontend-Route-Pfade für dieses Tool zurück."""
        return [
            "/easy-feedback",
            "/easy-feedback/start",
            "/easy-feedback/upload",
            "/easy-feedback/record",
            "/easy-feedback/settings",
            "/easy-feedback/result"
        ]
    
    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """Initialisiert das Plugin mit dem App-Kontext.
        
        Args:
            app_context: Dictionary mit shared services
            
        Returns:
            True wenn erfolgreich initialisiert
        """
        self.app_context = app_context
        
        # Hole Konfiguration
        self.config = app_context.get('plugin_config', {})
        
        # Initialisiere Service
        from .easy_feedback_service import EasyFeedbackService
        
        self.service = EasyFeedbackService(
            session_service=app_context.get('session_service'),
            storage_service=app_context.get('storage_service'),
            audio_service=app_context.get('audio_service'),
            plugin_config=self.config
        )
        
        print(f"✅ {self.display_name} Plugin v{self.version} initialisiert")
        return True
    
    def get_blueprint(self):
        """Gibt das Flask Blueprint für das Plugin zurück.
        
        Returns:
            Flask Blueprint mit allen Routes
        """
        if self.blueprint is None:
            from .easy_feedback_routes import create_blueprint
            self.blueprint = create_blueprint(self.service, self.config)
        return self.blueprint
    
    def register_routes(self, app) -> None:
        """Registriert Plugin-Routes in der Flask-App.
        
        Args:
            app: Flask-App Instanz
        """
        blueprint = self.get_blueprint()
        app.register_blueprint(blueprint)
        print(f"📍 {self.display_name} Routes registriert: /api/easy-feedback/*")
    
    def get_info(self) -> Dict[str, Any]:
        """Gibt Plugin-Informationen zurück.
        
        Returns:
            Dictionary mit Plugin-Metadaten
        """
        return {
            "name": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "description": self.config.get('description', ''),
            "icon": self.config.get('icon', '🎓'),
            "settings": self.config.get('settings', {})
        }
