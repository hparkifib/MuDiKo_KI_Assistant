# Prompt Generator - Generiert System-Prompts für LLM-Feedback
# 
# REFACTORED: Diese Klasse ist jetzt nur noch für System-Prompts zuständig.
# Die Report-Generierung wurde in separate Generator-Klassen ausgelagert.
#
# Verantwortlichkeit: Erstellt pädagogische Aufgabenstellungen für das LLM
# Siehe: detailed_report_generator.py, technical_report_generator.py, etc.

from typing import Dict, Any, List
from .report_config import ReportConfig
from .detailed_report_generator import DetailedReportGenerator
from .technical_report_generator import TechnicalReportGenerator
from .selective_report_generator import SelectiveReportGenerator

class PromptGenerator:
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
        self.report_variant = report_variant
        self.report_config = report_config or ReportConfig.detailed_report()
        self.report_generator = self._create_report_generator()
    
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
        """Erstellt pädagogisch optimierten System-Prompt.
        
        Args:
            language: Sprache für Feedback
            referenz_instrument: Instrument der Referenz
            schueler_instrument: Instrument des Schülers
            personal_message: Persönliche Nachricht
            use_simple_language: Einfache Sprache verwenden
            
        Returns:
            System-Prompt String
        """
        
        personal_section = f"\n{personal_message}\n" if personal_message else ""
        
        simple_language_note = ""
        if use_simple_language:
            simple_language_note = (
                "\nWichtiger Hinweis: Verwende besonders einfache, klare und kurze Sätze, "
                "damit das Feedback für Schüler mit Sprachbarrieren oder Lernschwierigkeiten "
                "leicht verständlich ist.\n"
            )
        
        prompt = f"""Hintergrund: Im Folgenden erhältst du eine Musik-Analyse-Report zu zwei Aufnahmen.
Die Referenzaufnahme wurde von einer Lehrkraft mit {referenz_instrument} eingespielt und dient als Vorbild.
Die Schüleraufnahme wurde mit {schueler_instrument} aufgenommen und soll die Referenz nachahmen.

Aufgabe: Gib dem Schüler konstruktives, motivierendes Feedback zu seiner musikalischen Leistung.

Sprache: {language}
Zielgruppe: Schüler der Sekundarstufe 1 (Alter: 12-16 Jahre)
{simple_language_note}{personal_section}
Anweisungen:
- Fokussiere auf musikalische Aspekte, nicht auf technische Messwerte
- Verwende eine freundliche, ermutigende Sprache
- Strukturiere das Feedback nach: Lob → Fehleranalyse → Verbesserungsvorschläge
- Bei mehreren Segmenten: Gib sowohl Segment-spezifisches als auch Gesamt-Feedback
- Halte es kurz: Maximal 1-3 Sätze pro Segment
- Beachte: Segmente könnten zeitlich versetzt sein (z.B. nach Fehlern oder Neustart)
- Die Aufnahmen können unterschiedlich lang sein (Stille am Ende ignorieren)

Struktur des Feedbacks:
1. **Begrüßung**: Stelle dich als Musik-KI-Assistent vor
2. **Lob**: Hebe konkrete Stärken hervor (ehrlich, nicht übertrieben)
3. **Fehleranalyse**: Erkläre Unterschiede zur Referenz verständlich
4. **Verbesserungsvorschläge**: Gib konkrete, umsetzbare Übungstipps

Nun folgt der Musik-Analyse-Report:
"""
        return prompt.strip()
