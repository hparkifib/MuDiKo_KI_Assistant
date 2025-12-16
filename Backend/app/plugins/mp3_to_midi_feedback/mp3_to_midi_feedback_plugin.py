"""MP3-to-MIDI Feedback Plugin - Konvertiert MP3 zu MIDI und analysiert taktbasiert."""

from flask import Blueprint
from app.plugins.base.plugin_interface import MusicToolPlugin
from .mp3_to_midi_feedback_service import Mp3ToMidiFeedbackService
from .mp3_to_midi_feedback_routes import create_routes


class Mp3ToMidiFeedbackPlugin(MusicToolPlugin):
    """MP3-to-MIDI Feedback Analyse Tool.
    
    Konvertiert MP3-Aufnahmen via Basic Pitch zu MIDI und vergleicht
    sie taktbasiert für präzises, notenbasiertes Feedback.
    """
    
    @property
    def name(self) -> str:
        return "mp3-to-midi-feedback"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def display_name(self) -> str:
        return "MP3-to-MIDI Feedback Analyzer"
    
    @property
    def description(self) -> str:
        return "Konvertiert MP3-Aufnahmen zu MIDI und vergleicht sie taktbasiert"
    
    def initialize(self, app_context):
        """Initialisiert das Tool mit shared services.
        
        Args:
            app_context: Dictionary mit Services und Config
        """
        self.session_service = app_context['session_service']
        self.storage_service = app_context['storage_service']
        self.audio_service = app_context['audio_service']
        self.app_config = app_context['config']
        self.plugin_config = app_context.get('plugin_config', {})
        
        # Erstelle Tool-spezifischen Service
        self.feedback_service = Mp3ToMidiFeedbackService(
            self.session_service,
            self.storage_service,
            self.audio_service,
            plugin_config=self.plugin_config
        )
        
        print(f"🎹 MP3-to-MIDI Feedback Plugin initialisiert (v{self.version})")
    
    def get_blueprint(self) -> Blueprint:
        """Erstellt Blueprint mit allen Routes.
        
        Returns:
            Blueprint: Flask Blueprint mit API-Endpoints
        """
        return create_routes(
            self.name,
            self.session_service,
            self.storage_service,
            self.feedback_service,
            self.plugin_config
        )
    
    def get_frontend_routes(self):
        """Gibt Frontend-Route-Pfade zurück.
        
        Returns:
            List[str]: Liste der Frontend-Pfade
        """
        return self.plugin_config.get('frontend_routes', [])
    
    def cleanup(self):
        """Cleanup beim Herunterfahren."""
        print(f"🎹 MP3-to-MIDI Feedback Plugin cleanup")
