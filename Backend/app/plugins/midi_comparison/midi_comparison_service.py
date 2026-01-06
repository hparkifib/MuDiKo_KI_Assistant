"""MIDI Comparison Service - Geschäftslogik für MIDI-Vergleich und Feedback-Generierung."""

from pathlib import Path
from typing import Dict, Any

from app.shared.libs.midi_analyzer import MidiAnalyzer
from app.shared.libs.midi_analyzer.formatters import TextFormatter
from app.shared.services.prompt_builder import BasePromptBuilder


class MidiComparisonService(BasePromptBuilder):
    """Service für MIDI-Analyse und -Vergleich."""
    
    def __init__(self, storage_service, plugin_config: Dict[str, Any] = None):
        """Initialisiert den MIDI Comparison Service.
        
        Args:
            storage_service: StorageService für Dateiverwaltung
            plugin_config: Plugin-spezifische Konfiguration
        """
        # Template-Pfad
        template_dir = Path(__file__).parent / "templates"
        super().__init__(template_dir)
        
        self.storage_service = storage_service
        self.config = plugin_config or {}
        self.settings = self.config.get('settings', {})
        
        # MIDI Analyzer und Formatter initialisieren
        self.analyzer = MidiAnalyzer()
        self.text_formatter = TextFormatter()
        
        self._load_plugin_templates()
        
        print(f"✅ MIDI Comparison Service initialisiert")
    
    def _load_plugin_templates(self):
        """Lädt Plugin-spezifische Templates."""
        self.system_prompt_template = self.loader.load_template("system_prompt.txt")
    
    def compare_midi_files(
        self,
        session_id: str,
        reference_filename: str,
        student_filename: str
    ) -> Dict[str, Any]:
        """Vergleicht zwei MIDI-Dateien.
        
        Args:
            session_id: Session-ID
            reference_filename: Dateiname der Referenz-MIDI
            student_filename: Dateiname der Schüler-MIDI
            
        Returns:
            Dictionary mit Vergleichsergebnis
        """
        # Dateipfade ermitteln
        ref_path = self.storage_service.get_file_path(session_id, reference_filename)
        student_path = self.storage_service.get_file_path(session_id, student_filename)
        
        # Dateien mit MIDI Analyzer vergleichen
        comparison_result = self.analyzer.compare_files(str(ref_path), str(student_path))
        
        # Formatiere Ergebnis als Text (für LLM) mit TextFormatter
        raw_text = self.text_formatter.format_comparison(comparison_result)

        # Baue einen minimalen Output: nur die Tabelle.
        # Keine Fehleranzahl mehr - das LLM analysiert selbst.
        try:
            header_lines = []

            # Extrahiere mehrere Tabellen (pro Spur) inkl. Spur-Header
            sections = []
            lines = raw_text.splitlines()
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                # Spur-Header erkennen (Markdown-Header: "### Spur N: ...") oder generisch "Spur"/"Track"
                if (line.lower().startswith('### spur') or line.lower().startswith('### track') or line.lower().startswith('spur') or line.lower().startswith('track')):
                    # Sammle Headerzeilen bis zur ersten Tabellenzeile
                    header = [lines[i]]
                    j = i + 1
                    while j < len(lines):
                        nxt = lines[j].strip()
                        if '|' in nxt:
                            break
                        if nxt and not nxt.startswith('#'):
                            header.append(lines[j])
                        j += 1

                    # Sammle die Tabelle
                    table = []
                    while j < len(lines):
                        row = lines[j]
                        rs = row.strip()
                        if not rs:
                            break
                        if '|' in rs or (set(rs) <= set('-: ')):
                            table.append(row)
                            j += 1
                        else:
                            break

                    if table:
                        sections.append({'header': header, 'table': table})
                    i = j
                    continue
                i += 1

            # Wenn keine Abschnitte erkannt wurden, versuche Einzeltabelle
            if not sections:
                table_lines = []
                in_table = False
                for line in lines:
                    ls = line.strip()
                    if '|' in ls:
                        in_table = True
                        table_lines.append(line)
                    elif in_table and (set(ls) <= set('-: ')):
                        table_lines.append(line)
                    elif in_table:
                        break
                if table_lines:
                    sections.append({'header': [], 'table': table_lines})

            # Ersetze Dateinamen und Spaltenlabel je Tabelle
            file1 = comparison_result.file1_analysis.filename
            file2 = comparison_result.file2_analysis.filename
            for sec in sections:
                sec['table'] = [
                    ln.replace(file1, 'Referenz')
                      .replace(file2, 'Schüler*in')
                      .replace('Vergleich', 'Schüler*in')
                    for ln in sec['table']
                ]

            # Zusammensetzen: Header + je Spur Überschrift + Tabelle
            body_lines = []
            for sec in sections:
                if sec['header']:
                    body_lines.append(sec['header'][0])
                    for h in sec['header'][1:]:
                        if 'instrument' in h.lower():
                            body_lines.append(h)
                body_lines.extend(sec['table'])
                body_lines.append("")

            if not body_lines:
                # Fallback: bereinigter Originaltext ohne Pfade/JSON
                cleaned = []
                for line in raw_text.splitlines():
                    lower = line.strip().lower()
                    if (
                        lower.startswith('pfad:') or
                        lower.startswith('speicherort:') or
                        lower.startswith('path:') or
                        lower.startswith('file path:') or
                        ('/uploads/' in lower) or
                        ('\\uploads\\' in lower) or
                        lower.startswith('{') or lower.endswith('}')
                    ):
                        continue
                    cleaned.append(line)
                body_lines = cleaned

            text_output = "\n".join(header_lines + [""] + body_lines).strip()
        except Exception:
            # Bei Fehler: Originaltext liefern
            text_output = raw_text
        
        return {
            "success": True,
            "comparison_text": text_output,
            "summary": {
                "reference_notes": comparison_result.file1_analysis.total_notes,
                "student_notes": comparison_result.file2_analysis.total_notes,
                "sync_applied": getattr(comparison_result.summary, 'sync_applied', False) if comparison_result.summary else False,
                # Einheitliche, LLM-freundliche Labels statt Dateinamen
                "file1": "Referenz",
                "file2": "Schüler*in"
            }
        }
    
    def generate_feedback_prompt(
        self,
        comparison_text: str,
        language: str = "Deutsch",
        personalization: str = "",
        use_simple_language: bool = False
    ) -> str:
        """Generiert System-Prompt für LLM-Feedback aus Template.
        
        Args:
            comparison_text: Tabellarischer MIDI-Vergleich (wird NICHT im Prompt verwendet)
            language: Sprache des Feedbacks
            personalization: Personalisierungstext
            use_simple_language: Einfache Sprache verwenden
            
        Returns:
            System-Prompt für LLM (nur Aufgabenbeschreibung)
        """
        # Einfache Sprache Hinweis (shared)
        simple_language_note = self.build_simple_language_section(use_simple_language)
        
        # Personalisierung
        personalization_section = self.build_personalization_section(
            personalization
        )
        
        # Template mit Variablen füllen
        prompt = self.loader.format_template(
            self.system_prompt_template,
            language=language,
            simple_language_note=simple_language_note,
            personalization_section=personalization_section
        )
        
        return prompt
