"""Easy Feedback Service - Orchestriert die vereinfachte Feedback-Pipeline."""

from pathlib import Path
from typing import Dict, Any, Optional
import logging
import mimetypes

from app.shared.libs.midi_analyzer import MidiAnalyzer
from app.shared.libs.midi_analyzer.formatters import TextFormatter
from app.shared.services.prompt_builder import BasePromptBuilder
from app.plugins.mp3_to_midi_feedback.mp3_to_midi_converter import Mp3ToMidiConverter
from app.plugins.mp3_to_midi_feedback.conversion_optimizer import ConversionParameterOptimizer


class EasyFeedbackService(BasePromptBuilder):
    """Service für vereinfachtes Audio-Feedback.
    
    Vereint die Logik aus mp3_to_midi_feedback und midi_comparison
    für einen linearen, benutzerfreundlichen Workflow.
    """
    
    def __init__(
        self,
        session_service,
        storage_service,
        audio_service,
        plugin_config: Optional[Dict] = None
    ):
        """Initialisiert den Service.
        
        Args:
            session_service: SessionService für Session-Management
            storage_service: StorageService für Datei-Verwaltung
            audio_service: AudioService für Audio-Verarbeitung
            plugin_config: Plugin-Konfiguration
        """
        # Template-Pfad
        template_dir = Path(__file__).parent / "templates"
        super().__init__(template_dir)
        
        self.session_service = session_service
        self.storage_service = storage_service
        self.audio_service = audio_service
        self.plugin_config = plugin_config or {}
        self.settings = self.plugin_config.get('settings', {})
        
        # MIDI Analyzer und Formatter
        self.analyzer = MidiAnalyzer()
        self.text_formatter = TextFormatter()
        
        # MP3-to-MIDI Converter (für Audio-Dateien)
        self.converter = Mp3ToMidiConverter(plugin_config)
        self.optimizer = ConversionParameterOptimizer(audio_service)
        
        self._load_plugin_templates()
        
        logging.info("✅ EasyFeedbackService initialisiert")
    
    def _load_plugin_templates(self):
        """Lädt Plugin-spezifische Templates."""
        self.system_prompt_template = self.loader.load_template("system_prompt.txt")
    
    def detect_file_type(self, filename: str) -> str:
        """Erkennt den Dateityp anhand der Endung.
        
        Args:
            filename: Dateiname
            
        Returns:
            'midi' oder 'audio'
        """
        ext = Path(filename).suffix.lower()
        midi_extensions = ['.mid', '.midi']
        
        if ext in midi_extensions:
            return 'midi'
        return 'audio'
    
    def process_upload(
        self,
        session_id: str,
        role: str,
        file_data: bytes,
        filename: str
    ) -> Dict[str, Any]:
        """Verarbeitet einen Upload (Referenz oder Schüler).
        
        Args:
            session_id: Session-ID
            role: 'referenz' oder 'schueler'
            file_data: Datei-Bytes
            filename: Original-Dateiname
            
        Returns:
            Dict mit Upload-Status und Datei-Infos
        """
        # Erkenne Dateityp
        file_type = self.detect_file_type(filename)
        ext = Path(filename).suffix.lower()
        
        # Speichere Datei direkt mit Bytes
        session_dir = self.storage_service.get_session_directory(session_id)
        stored_filename = f"{role}{ext}"
        file_path = session_dir / stored_filename
        
        # Schreibe Bytes direkt in Datei
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Speichere Info in Session
        session = self.session_service.get_session(session_id)
        files_info = session.get_data('files_info') or {}
        files_info[role] = {
            'filename': stored_filename,
            'original_name': filename,
            'type': file_type,
            'path': str(file_path)
        }
        session.set_data('files_info', files_info)
        
        logging.info(f"📁 {role} gespeichert: {stored_filename} ({file_type})")
        
        return {
            'success': True,
            'role': role,
            'filename': stored_filename,
            'type': file_type
        }
    
    def process_recording(
        self,
        session_id: str,
        role: str,
        audio_data: bytes,
        mime_type: str = 'audio/webm'
    ) -> Dict[str, Any]:
        """Verarbeitet eine Browser-Aufnahme.
        
        Args:
            session_id: Session-ID
            role: 'referenz' oder 'schueler'
            audio_data: Audio-Bytes (Base64-dekodiert)
            mime_type: MIME-Typ der Aufnahme
            
        Returns:
            Dict mit Upload-Status
        """
        # Bestimme Dateiendung
        ext_map = {
            'audio/webm': '.webm',
            'audio/ogg': '.ogg',
            'audio/wav': '.wav',
            'audio/mpeg': '.mp3',
            'audio/mp3': '.mp3'
        }
        ext = ext_map.get(mime_type, '.webm')
        filename = f"{role}_recording{ext}"
        
        return self.process_upload(session_id, role, audio_data, filename)
    
    def convert_if_needed(self, session_id: str) -> Dict[str, Any]:
        """Konvertiert Audio-Dateien zu MIDI falls nötig.
        
        Args:
            session_id: Session-ID
            
        Returns:
            Dict mit Konversions-Status
        """
        session = self.session_service.get_session(session_id)
        files_info = session.get_data('files_info') or {}
        session_dir = self.storage_service.get_session_directory(session_id)
        
        # Prüfe welche Dateien konvertiert werden müssen
        needs_conversion = {}
        for role in ['referenz', 'schueler']:
            if role not in files_info:
                return {
                    'success': False,
                    'error': f'Keine {role}-Datei vorhanden'
                }
            
            if files_info[role]['type'] == 'audio':
                needs_conversion[role] = session_dir / files_info[role]['filename']
        
        # Wenn keine Konversion nötig, einfach MIDI-Pfade setzen
        if not needs_conversion:
            midi_files = {}
            for role in ['referenz', 'schueler']:
                midi_files[role] = str(session_dir / files_info[role]['filename'])
            session.set_data('midi_files', midi_files)
            return {
                'success': True,
                'converted': [],
                'message': 'Beide Dateien sind bereits MIDI'
            }
        
        # Erstelle MIDI-Verzeichnis
        midi_dir = session_dir / "midi"
        midi_dir.mkdir(exist_ok=True)
        
        # Berechne Parameter aus Referenz (falls Referenz konvertiert wird)
        ref_path = needs_conversion.get('referenz')
        if not ref_path:
            # Referenz ist MIDI, nimm Schüler für Parameter
            ref_path = needs_conversion.get('schueler')
        
        try:
            optimized_params = self.optimizer.optimize(ref_path)
        except Exception as e:
            logging.error(f"❌ Parameter-Optimierung fehlgeschlagen: {e}")
            # Fallback: Standard-Parameter
            optimized_params = {}
        
        # Konvertiere benötigte Dateien
        results = self.converter.batch_convert(
            needs_conversion,
            midi_dir,
            optimized_params
        )
        
        # Speichere MIDI-Pfade
        midi_files = {}
        for role in ['referenz', 'schueler']:
            if role in results and results[role].get('success'):
                midi_files[role] = results[role]['midi_path']
            elif files_info[role]['type'] == 'midi':
                midi_files[role] = str(session_dir / files_info[role]['filename'])
        
        session.set_data('midi_files', midi_files)
        
        return {
            'success': True,
            'converted': list(needs_conversion.keys()),
            'results': results
        }
    
    def compare_midi_files(self, session_id: str) -> Dict[str, Any]:
        """Vergleicht die MIDI-Dateien der Session.
        
        Args:
            session_id: Session-ID
            
        Returns:
            Dict mit Vergleichsergebnis
        """
        session = self.session_service.get_session(session_id)
        midi_files = session.get_data('midi_files')
        
        if not midi_files or 'referenz' not in midi_files or 'schueler' not in midi_files:
            return {
                'success': False,
                'error': 'MIDI-Dateien nicht vorhanden. Bitte erst konvertieren.'
            }
        
        # Vergleiche MIDI-Dateien
        comparison_result = self.analyzer.compare_files(
            midi_files['referenz'],
            midi_files['schueler']
        )
        
        # Formatiere als Text
        raw_text = self.text_formatter.format_comparison(comparison_result)
        
        # Bereinige und formatiere Output (gleiche Logik wie MidiComparisonService)
        text_output = self._format_comparison_text(raw_text, comparison_result)
        
        # Speichere in Session
        session.set_data('comparison_text', text_output)
        
        return {
            'success': True,
            'comparison_text': text_output,
            'summary': {
                'reference_notes': comparison_result.file1_analysis.total_notes,
                'student_notes': comparison_result.file2_analysis.total_notes
            }
        }
    
    def _format_comparison_text(self, raw_text: str, comparison_result) -> str:
        """Formatiert den Vergleichstext für LLM-Konsum.
        
        Args:
            raw_text: Roher Vergleichstext
            comparison_result: MIDI-Vergleichsergebnis
            
        Returns:
            Bereinigter Text
        """
        try:
            sections = []
            lines = raw_text.splitlines()
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                if (line.lower().startswith('### spur') or 
                    line.lower().startswith('### track') or 
                    line.lower().startswith('spur') or 
                    line.lower().startswith('track')):
                    
                    header = [lines[i]]
                    j = i + 1
                    while j < len(lines):
                        nxt = lines[j].strip()
                        if '|' in nxt:
                            break
                        if nxt and not nxt.startswith('#'):
                            header.append(lines[j])
                        j += 1
                    
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
            
            file1 = comparison_result.file1_analysis.filename
            file2 = comparison_result.file2_analysis.filename
            for sec in sections:
                sec['table'] = [
                    ln.replace(file1, 'Referenz')
                      .replace(file2, 'Schüler*in')
                      .replace('Vergleich', 'Schüler*in')
                    for ln in sec['table']
                ]
            
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
                cleaned = []
                for line in raw_text.splitlines():
                    lower = line.strip().lower()
                    if (lower.startswith('pfad:') or
                        lower.startswith('speicherort:') or
                        lower.startswith('path:') or
                        lower.startswith('file path:') or
                        ('/uploads/' in lower) or
                        ('\\uploads\\' in lower) or
                        lower.startswith('{') or lower.endswith('}')):
                        continue
                    cleaned.append(line)
                body_lines = cleaned
            
            return "\n".join(body_lines).strip()
            
        except Exception:
            return raw_text
    
    def generate_feedback_prompt(
        self,
        session_id: str,
        language: str = "Deutsch",
        personalization: str = "",
        use_simple_language: bool = False
    ) -> Dict[str, Any]:
        """Generiert den Feedback-Prompt.
        
        Args:
            session_id: Session-ID
            language: Sprache des Feedbacks
            personalization: Personalisierungstext
            use_simple_language: Einfache Sprache verwenden
            
        Returns:
            Dict mit System-Prompt und User-Prompt (Vergleichstext)
        """
        session = self.session_service.get_session(session_id)
        comparison_text = session.get_data('comparison_text')
        
        if not comparison_text:
            return {
                'success': False,
                'error': 'Kein Vergleichstext vorhanden. Bitte erst vergleichen.'
            }
        
        # System-Prompt aus Template
        simple_language_note = self.build_simple_language_section(use_simple_language)
        personalization_section = self.build_personalization_section(personalization)
        
        system_prompt = self.loader.format_template(
            self.system_prompt_template,
            language=language,
            simple_language_note=simple_language_note,
            personalization_section=personalization_section
        )
        
        return {
            'success': True,
            'system_prompt': system_prompt,
            'user_prompt': comparison_text
        }
    
    def get_midi_download_path(self, session_id: str, role: str) -> Optional[str]:
        """Gibt den Pfad zur MIDI-Datei für Download zurück.
        
        Args:
            session_id: Session-ID
            role: 'referenz' oder 'schueler'
            
        Returns:
            Dateipfad oder None
        """
        session = self.session_service.get_session(session_id)
        midi_files = session.get_data('midi_files')
        
        if midi_files and role in midi_files:
            return midi_files[role]
        return None
