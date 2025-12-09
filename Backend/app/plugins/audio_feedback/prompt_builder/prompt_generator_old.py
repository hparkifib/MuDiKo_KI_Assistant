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
        return generator_class(self.report_config.config if hasattr(self.report_config, 'config') else self.report_config.__dict__)
    
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
        """Erstellt pädagogisch optimierten System-Prompt."""
        
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
    
    def _format_pedagogical_report(
        self, 
        segment_results: List[Dict[str, Any]], 
        include_context: bool
    ) -> str:
        """Formatiert einen pädagogisch wertvollen Analyse-Report."""
        lines = ["\n" + "="*70]
        lines.append("MUSIK-ANALYSE-REPORT")
        lines.append("="*70 + "\n")
        
        for idx, segment in enumerate(segment_results, 1):
            lines.append(f"\n{'─'*70}")
            lines.append(f"Segment {idx}  |  Zeit: {segment['schueler_start']:.1f}s - {segment['schueler_end']:.1f}s")
            lines.append('─'*70 + "\n")
            
            analysis = segment.get('analysis', {})
            
            # Gruppiere Features nach Kategorien für bessere Struktur
            tempo_features = self._extract_category_features(analysis, ['tempo', 'onset_count', 'rhythm'])
            pitch_features = self._extract_category_features(analysis, ['pitch', 'key', 'chord', 'vibrato'])
            dynamics_features = self._extract_category_features(analysis, ['rms', 'dynamic', 'silence', 'attack'])
            timbre_features = self._extract_category_features(analysis, ['centroid', 'bandwidth', 'timbre', 'mfcc'])
            comparison_features = self._extract_comparison_features(analysis)
            
            # Formatiere jede Kategorie semantisch
            if tempo_features:
                lines.append("┌─ TEMPO & RHYTHMUS")
                lines.extend(self._format_features_with_context(tempo_features, include_context))
                lines.append("")
            
            if pitch_features:
                lines.append("┌─ TONHÖHE & HARMONIE")
                lines.extend(self._format_features_with_context(pitch_features, include_context))
                lines.append("")
            
            if dynamics_features:
                lines.append("┌─ LAUTSTÄRKE & AUSDRUCK")
                lines.extend(self._format_features_with_context(dynamics_features, include_context))
                lines.append("")
            
            if timbre_features:
                lines.append("┌─ KLANGFARBE")
                lines.extend(self._format_features_with_context(timbre_features, include_context))
                lines.append("")
            
            if comparison_features:
                lines.append("┌─ VERGLEICH REFERENZ ↔ SCHÜLER")
                lines.extend(self._format_comparison_with_interpretation(comparison_features, include_context))
                lines.append("")
        
        lines.append("="*70)
        return "\n".join(lines)
    
    def _extract_category_features(self, analysis: Dict[str, Any], keywords: List[str]) -> Dict[str, Any]:
        """Extrahiert Features einer Kategorie."""
        return {
            key: value for key, value in analysis.items()
            if any(keyword in key.lower() for keyword in keywords)
        }
    
    def _extract_comparison_features(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiert Vergleichs-Metriken."""
        comparison_keys = ['distance', 'similarity', 'correlation']
        return {
            key: value for key, value in analysis.items()
            if any(comp_key in key.lower() for comp_key in comparison_keys)
        }
    
    def _format_features_with_context(self, features: Dict[str, Any], include_context: bool) -> List[str]:
        """Formatiert Features mit pädagogischem Kontext - Referenz und Schüler nebeneinander."""
        lines = []
        
        # Sammle Referenz- und Schüler-Werte zusammen
        paired_features = {}
        standalone_features = {}
        
        for key, value in features.items():
            if key.startswith('referenz_'):
                clean_key = key.replace('referenz_', '')
                if clean_key not in paired_features:
                    paired_features[clean_key] = {}
                paired_features[clean_key]['referenz'] = value
            elif key.startswith('schueler_'):
                clean_key = key.replace('schueler_', '')
                if clean_key not in paired_features:
                    paired_features[clean_key] = {}
                paired_features[clean_key]['schueler'] = value
            else:
                standalone_features[key] = value
        
        # Formatiere gepaarte Features (Referenz + Schüler nebeneinander)
        for feature_name, values in paired_features.items():
            display_name = self.feature_contexts.get(feature_name, feature_name)
            ref_val = values.get('referenz', 'N/A')
            sch_val = values.get('schueler', 'N/A')
            
            # Formatiere mit klarem Abstand und Tabs
            ref_formatted = self._format_value(ref_val)
            sch_formatted = self._format_value(sch_val)
            
            lines.append(f"│  {display_name}:")
            lines.append(f"│      Referenz:\t{ref_formatted}")
            lines.append(f"│      Schüler:\t\t{sch_formatted}")
            lines.append("│")
        
        # Formatiere standalone Features
        for key, value in standalone_features.items():
            display_name = self.feature_contexts.get(key, key)
            formatted_val = self._format_value(value)
            lines.append(f"│  {display_name}:\t{formatted_val}")
            lines.append("│")
        
        return lines
    
    def _format_comparison_with_interpretation(self, features: Dict[str, Any], include_context: bool) -> List[str]:
        """Formatiert Vergleichsmetriken mit Interpretation."""
        lines = []
        for key, value in features.items():
            if value is None:
                continue
            
            display_name = self.feature_contexts.get(key, key)
            interpretation = self._interpret_metric(key, value)
            formatted_val = self._format_value(value)
            
            lines.append(f"│  {display_name}:")
            lines.append(f"│      Wert:\t\t{formatted_val}")
            if interpretation:
                lines.append(f"│      Bewertung:\t{interpretation}")
            lines.append("│")
        
        return lines
    
    def _interpret_metric(self, metric_name: str, value: float) -> str:
        """Interpretiert Vergleichsmetriken pädagogisch."""
        if 'distance' in metric_name.lower():
            if value < 5:
                return "Sehr ähnlich ✓"
            elif value < 15:
                return "Ähnlich, kleine Unterschiede"
            else:
                return "Deutliche Unterschiede"
        
        elif 'similarity' in metric_name.lower() or 'correlation' in metric_name.lower():
            if value > 0.8:
                return "Sehr gut übereinstimmend ✓"
            elif value > 0.5:
                return "Teilweise übereinstimmend"
            elif value > 0:
                return "Geringe Übereinstimmung"
            else:
                return "Wenig Übereinstimmung"
        
        return ""
    
    def _format_value(self, value: Any) -> str:
        """Formatiert Werte lesbar."""
        if isinstance(value, float):
            return f"{value:.2f}"
        elif isinstance(value, dict):
            return ", ".join([f"{k}={self._format_value(v)}" for k, v in value.items()])
        else:
            return str(value)
