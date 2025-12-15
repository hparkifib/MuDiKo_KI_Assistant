"""Audio Feedback Service - Geschäftslogik für Audio-Analyse und Feedback-Generierung."""

from pathlib import Path
from typing import Dict, List, Any, Tuple
import os

from .audio_feedback_pipeline import AudioFeedbackPipeline

class AudioFeedbackService:
    """Service für Audio Feedback Analyse und Prompt-Generierung."""
    
    def __init__(self, audio_service, storage_service, plugin_config: Dict[str, Any] = None):
        """Initialisiert den Audio Feedback Service.
        
        Args:
            audio_service: AudioService instance für Audio-Operationen
            storage_service: StorageService instance für Dateizugriff
            plugin_config: Plugin-Konfiguration aus config.yaml
        """
        self.audio_service = audio_service
        self.storage_service = storage_service
        self.pipelines = {}  # Cache für Pipelines pro Session
        
        # Report-Generator Config aus Plugin-Config
        self.plugin_config = plugin_config or {}
        settings = self.plugin_config.get('settings', {})
        self.report_variant = settings.get('report_variant', 'detailed')
        self.report_config = settings.get('report_config', {})
    
    def get_pipeline(self, session_id: str, session_path: str) -> AudioFeedbackPipeline:
        """Holt oder erstellt eine Pipeline für eine Session.
        
        Args:
            session_id: Session-ID
            session_path: Pfad zum Session-Ordner
            
        Returns:
            AudioFeedbackPipeline: Pipeline-Instanz
        """
        if session_id not in self.pipelines:
            self.pipelines[session_id] = AudioFeedbackPipeline(
                upload_folder=session_path,
                target_sr=22050,
                target_length=60,
                report_variant=self.report_variant,
                report_config=self.report_config
            )
        return self.pipelines[session_id]
    
    def analyze_recordings(
        self,
        session_id: str,
        session_path: str,
        referenz_segments: List[str],
        schueler_segments: List[str],
        language: str = "english",
        referenz_instrument: str = "keine Angabe",
        schueler_instrument: str = "keine Angabe",
        personal_message: str = "",
        prompt_type: str = "contextual",
        use_simple_language: bool = False
    ) -> Dict[str, Any]:
        """Führt vollständige Audio-Analyse durch.
        
        Args:
            session_id: Session-ID
            session_path: Pfad zum Session-Ordner
            referenz_segments: Liste der Referenz-Segment-Dateinamen
            schueler_segments: Liste der Schüler-Segment-Dateinamen
            language: Sprache für Feedback
            referenz_instrument: Instrument der Referenz
            schueler_instrument: Instrument des Schülers
            personal_message: Persönliche Nachricht
            prompt_type: Art des Prompts
            use_simple_language: Einfache Sprache verwenden
            
        Returns:
            Dict: Analyse-Ergebnisse mit system_prompt und analysis_data
        """
        # Hole Pipeline für diese Session
        pipeline = self.get_pipeline(session_id, session_path)
        
        # Führe Analyse durch
        result = pipeline.analyze_and_generate_feedback(
            referenz_segments,
            schueler_segments,
            language,
            referenz_instrument,
            schueler_instrument,
            personal_message,
            prompt_type,
            use_simple_language
        )
        
        return result
    
    def cleanup_session(self, session_id: str):
        """Entfernt Pipeline-Cache für eine Session.
        
        Args:
            session_id: Session-ID
        """
        if session_id in self.pipelines:
            del self.pipelines[session_id]
    
    def get_language_name(self, language_code: str, custom_language: str = "") -> str:
        """Konvertiert Sprach-Code in Anzeigename.
        
        Args:
            language_code: Sprach-Code (z.B. 'deutsch', 'english')
            custom_language: Benutzerdefinierte Sprache
            
        Returns:
            str: Anzeigename der Sprache
        """
        if language_code == "custom" and custom_language:
            return custom_language
        
        language_map = {
            "deutsch": "Deutsch",
            "english": "Englisch",
            "español": "Spanisch",
            "français": "Französisch",
            "italiano": "Italienisch",
            "türkçe": "Türkisch"
        }
        return language_map.get(language_code, "English")
