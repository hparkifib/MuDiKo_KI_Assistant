"""Audio Feedback Plugin - Analysiert Audiodateien und generiert KI-Feedback."""

from flask import Blueprint
from app.plugins.base.plugin_interface import MusicToolPlugin
from .audio_feedback_service import AudioFeedbackService
from .audio_feedback_routes import create_routes

class AudioFeedbackPlugin(MusicToolPlugin):
    """Audio Feedback Analyse Tool.
    
    Vergleicht Schüler- und Referenzaufnahmen und generiert
    intelligentes, KI-gestütztes Feedback.
    """
    
    @property
    def name(self) -> str:
        return "audio-feedback"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def display_name(self) -> str:
        return "Audio-Vergleich"
    
    @property
    def description(self) -> str:
        return "Vergleiche deine Aufnahme mit einer Vorspiel-Aufnahme"
    
    def initialize(self, app_context):
        """Initialisiert das Tool mit shared services.
        
        Args:
            app_context: Dictionary mit Services und Config
        """
        self.session_service = app_context['session_service']
        self.storage_service = app_context['storage_service']
        self.audio_service = app_context['audio_service']
        self.app_config = app_context['config']  # Flask App Config
        self.plugin_config = app_context.get('plugin_config', {})  # Plugin Config aus config.yaml
        
        # Erstelle Tool-spezifischen Service mit Plugin-Config
        self.feedback_service = AudioFeedbackService(
            self.audio_service,
            self.storage_service,
            plugin_config=self.plugin_config  # Plugin-Config weitergeben
        )
        
        # Log welche Report-Variante verwendet wird
        report_variant = self.plugin_config.get('settings', {}).get('report_variant', 'detailed')
        print(f"🎵 Audio Feedback Plugin initialisiert (Report: {report_variant})")
    
    def get_blueprint(self) -> Blueprint:
        """Erstellt Blueprint mit allen Routes.
        
        Returns:
            Blueprint: Flask Blueprint mit API-Endpoints
        """
        return create_routes(
            self.feedback_service,
            self.session_service,
            self.storage_service,
            self.audio_service
        )
    
    def get_frontend_routes(self):
        """Gibt Frontend-Routes zurück.
        
        Returns:
            List[str]: Liste der Frontend-Pfade
        """
        return [
            '/tools/audio-feedback/upload',
            '/tools/audio-feedback/recordings',
            '/tools/audio-feedback/language',
            '/tools/audio-feedback/instruments',
            '/tools/audio-feedback/personalization',
            '/tools/audio-feedback/prompt'
        ]
    
    def get_icon(self):
        """Gibt Icon-Pfad zurück.
        
        Returns:
            str: Pfad zum Icon
        """
        return '/icons/audio-feedback.svg'
    
    def cleanup(self):
        """Cleanup beim Shutdown."""
        # Cleanup für alle Session-Pipelines
        if hasattr(self, 'feedback_service'):
            self.feedback_service.pipelines.clear()

