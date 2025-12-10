# MIDI Comparison Plugin - Plugin Implementation

from flask import Blueprint
from app.plugins.base.plugin_interface import MusicToolPlugin
from .service import MidiComparisonService
from .routes import create_routes

class MidiComparisonPlugin(MusicToolPlugin):
    """MIDI Comparison Analyse Tool.
    
    Vergleicht zwei MIDI-Dateien und erstellt eine tabellarische
    Notengegenüberstellung für LLM-basiertes Feedback.
    """
    
    @property
    def name(self) -> str:
        return "midi-comparison"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def display_name(self) -> str:
        return "MIDI Comparison Analyzer"
    
    @property
    def description(self) -> str:
        return "Vergleicht MIDI-Dateien und erstellt tabellarische Notenanalyse"
    
    def initialize(self, app_context):
        """Initialisiert das Tool mit shared services.
        
        Args:
            app_context: Dictionary mit Services und Config
        """
        self.session_service = app_context['session_service']
        self.storage_service = app_context['storage_service']
        self.app_config = app_context['config']
        self.plugin_config = app_context.get('plugin_config', {})
        
        # Erstelle Tool-spezifischen Service
        self.midi_service = MidiComparisonService(
            self.storage_service,
            plugin_config=self.plugin_config
        )
        
        print(f"🎹 MIDI Comparison Plugin initialisiert")
    
    def register_routes(self, base_path: str = "/api/tools") -> Blueprint:
        """Registriert API-Routen.
        
        Args:
            base_path: Basis-Pfad für Tool-Routen
            
        Returns:
            Flask Blueprint mit allen Routen
        """
        return create_routes(
            self.midi_service,
            self.session_service,
            self.storage_service
        )
    
    def get_blueprint(self) -> Blueprint:
        """Gibt Flask Blueprint mit allen Routes zurück.
        
        Returns:
            Blueprint: Flask Blueprint mit Tool-spezifischen Endpoints
        """
        return self.register_routes()
    
    def get_frontend_routes(self) -> list:
        """Gibt Frontend-Route-Pfade für dieses Tool zurück.
        
        Returns:
            List[str]: Liste der Frontend-Pfade
        """
        return self.plugin_config.get('frontend_routes', [])
    
    def cleanup(self):
        """Räumt Ressourcen auf (bei App-Shutdown)."""
        print(f"🧹 MIDI Comparison Plugin wird heruntergefahren...")
