# Prompt Generator - Generiert System-Prompts für LLM-Feedback
# 
# REFACTORED: Diese Klasse ist jetzt nur noch für System-Prompts zuständig.
# Die Report-Generierung wurde in separate Generator-Klassen ausgelagert.
#
# Verantwortlichkeit: Erstellt pädagogische Aufgabenstellungen für das LLM
# Siehe: detailed_report_generator.py, technical_report_generator.py, etc.

from typing import Dict, Any, List
from pathlib import Path
from .report_config import ReportConfig
from .detailed_report_generator import DetailedReportGenerator
from .technical_report_generator import TechnicalReportGenerator
from .selective_report_generator import SelectiveReportGenerator
from app.shared.services.prompt_builder import BasePromptBuilder

class PromptGenerator(BasePromptBuilder):
    """Generator für pädagogische System-Prompts (LLM-Aufgabenstellung).
    
    Diese Klasse erstellt nur noch den System-Prompt, der dem LLM
    die Aufgabe und den Kontext erklärt. Die Analyse-Reports werden
    von spezialisierten Report-Generatoren erstellt.
    """
    
    def __init__(self, report_variant: str = 'detailed', report_config: ReportConfig = None):
        """Initialisiert den Prompt Generator.
        
        Args:
            report_variant: Report-Variante ('detailed', 'technical', 'selective')
            report_config: Optionale Config für Report-Generator
        """
        # Template-Pfad
        template_dir = Path(__file__).parent.parent / "templates"
        super().__init__(template_dir)
        
        self.report_variant = report_variant
        self.report_config = report_config or ReportConfig.detailed_report()
        self.report_generator = self._create_report_generator()
        
        self._load_plugin_templates()
    
    def _load_plugin_templates(self):
        """Lädt Plugin-spezifische Templates."""
        self.system_prompt_template = self.loader.load_template("system_prompt.txt")
    
    def _create_report_generator(self):
        """Erstellt den passenden Report-Generator basierend auf Variante.
        
        Returns:
            Report-Generator Instanz
        """
        generators = {
            'detailed': DetailedReportGenerator,
            'technical': TechnicalReportGenerator,
            'selective': SelectiveReportGenerator
        }
        
        generator_class = generators.get(self.report_variant, DetailedReportGenerator)
        return generator_class(self.report_config.__dict__)
    
    def generate_feedback_prompt(
        self,
        segment_results: List[Dict[str, Any]],
        language: str,
        referenz_instrument: str,
        schueler_instrument: str,
        personal_message: str = "",
        prompt_type: str = "contextual",
        use_simple_language: bool = False
    ) -> Dict[str, Any]:
        """Generiert Feedback-Prompt mit System-Prompt und Analyse-Report.
        
        Args:
            segment_results: Liste der Segment-Analyse-Ergebnisse
            language: Sprache für Feedback
            referenz_instrument: Instrument der Referenz
            schueler_instrument: Instrument des Schülers
            personal_message: Persönliche Nachricht
            prompt_type: Art des Prompts ('contextual' oder 'data_only')
            use_simple_language: Einfache Sprache verwenden
            
        Returns:
            Dict mit system_prompt und analysis_data
        """
        # System-Prompt: Aufgabe für das LLM
        system_prompt = self._build_pedagogical_system_prompt(
            language,
            referenz_instrument,
            schueler_instrument,
            personal_message,
            use_simple_language
        )
        
        # Analyse-Report: Daten vom Report-Generator
        analysis_data_str = self.report_generator.generate_report(segment_results)
        
        return {
            "system_prompt": system_prompt,
            "analysis_data": analysis_data_str,
            "report_variant": self.report_variant
        }
    
    def _build_pedagogical_system_prompt(
        self,
        language: str,
        referenz_instrument: str,
        schueler_instrument: str,
        personal_message: str,
        use_simple_language: bool
    ) -> str:
        """Erstellt pädagogisch optimierten System-Prompt aus Template.
        
        Args:
            language: Sprache für Feedback
            referenz_instrument: Instrument der Referenz
            schueler_instrument: Instrument des Schülers
            personal_message: Persönliche Nachricht
            use_simple_language: Einfache Sprache verwenden
            
        Returns:
            System-Prompt String
        """
        # Einfache Sprache Hinweis (shared)
        simple_language_note = self.build_simple_language_section(use_simple_language)
        
        # Personalisierung
        personalization_section = self.build_personalization_section(
            personal_message
        )
        
        # Template mit Variablen füllen
        prompt = self.loader.format_template(
            self.system_prompt_template,
            referenz_instrument=referenz_instrument,
            schueler_instrument=schueler_instrument,
            language=language,
            simple_language_note=simple_language_note,
            personalization_section=personalization_section
        )
        
        return prompt.strip()
