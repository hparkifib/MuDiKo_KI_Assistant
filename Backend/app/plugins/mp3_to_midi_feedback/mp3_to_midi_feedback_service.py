"""MP3-to-MIDI Feedback Service - Orchestriert den gesamten Workflow."""

from pathlib import Path
from typing import Dict, Optional
import logging

from .mp3_to_midi_converter import Mp3ToMidiConverter


class Mp3ToMidiFeedbackService:
    """Service für MP3-to-MIDI Feedback Pipeline.
    
    Orchestriert:
    - Phase 1: MP3 zu MIDI Konversion via Basic Pitch
    - Phase 2: Taktbasierte Segmentierung (TODO)
    - Phase 3: MIDI-Comparison pro Segment (TODO)
    - Report-Generierung (TODO)
    """
    
    def __init__(self, session_service, storage_service, audio_service, plugin_config: Optional[Dict] = None):
        """Initialisiert den Service.
        
        Args:
            session_service: SessionService für Session-Management
            storage_service: StorageService für Datei-Verwaltung
            audio_service: AudioService für Audio-Verarbeitung
            plugin_config: Plugin-Konfiguration
        """
        self.session_service = session_service
        self.storage_service = storage_service
        self.audio_service = audio_service
        self.plugin_config = plugin_config or {}
        
        # Initialisiere Converter
        self.converter = Mp3ToMidiConverter(plugin_config)
        
        logging.info("🎹 Mp3ToMidiFeedbackService initialisiert")
    
    def convert_mp3_to_midi(self, session_id: str, preset_id: Optional[str] = None) -> Dict:
        """Konvertiert beide MP3-Dateien (Referenz + Schüler) zu MIDI.
        
        Phase 1 Implementation: Nur Konversion, keine Analyse.
        
        Args:
            session_id: Session-ID
            preset_id: Optional - ID des zu verwendenden Presets (z.B. 'klavier', 'gesang')
            
        Returns:
            Dict mit:
                - referenz: Konversions-Result für Referenz
                - schueler: Konversions-Result für Schüler
                - summary: Zusammenfassung
                - preset_used: Verwendetes Preset (falls angegeben)
                
        Raises:
            SessionNotFoundException: Session nicht gefunden
            FileNotFoundError: Audio-Dateien nicht gefunden
        """
        logging.info(f"🎵 Starte MP3-to-MIDI Konversion für Session {session_id}")
        
        # Lade Preset-Parameter falls angegeben
        preset_params = None
        preset_info = None
        if preset_id:
            try:
                from app.plugins.mp3_to_midi_feedback.presets import preset_manager
                preset = preset_manager.load_preset(preset_id)
                preset_params = preset.get('parameters', {})
                preset_info = {
                    'id': preset.get('id'),
                    'name': preset.get('name'),
                    'icon': preset.get('icon')
                }
                logging.info(f"🎼 Verwende Preset: {preset.get('name')} {preset.get('icon')}")
            except Exception as e:
                logging.warning(f"⚠️ Konnte Preset '{preset_id}' nicht laden: {e}. Verwende Defaults.")
        
        # Hole Session
        session = self.session_service.get_session(session_id)
        
        # Hole Audio-Dateien
        session_dir = self.storage_service.get_session_directory(session_id)
        
        # Finde Referenz- und Schüler-Dateien
        audio_files = {}
        for role in ['referenz', 'schueler']:
            # Suche nach Audio-Datei: {role}.mp3, {role}.wav oder {role}.mp4
            for ext in ['mp3', 'wav', 'mp4']:
                file_path = session_dir / f"{role}.{ext}"
                if file_path.exists():
                    audio_files[role] = file_path
                    break
            
            if role not in audio_files:
                raise FileNotFoundError(
                    f"Keine {role}-Datei gefunden in Session {session_id}"
                )
        
        # Erstelle Output-Verzeichnis für MIDIs
        midi_dir = session_dir / "midi"
        midi_dir.mkdir(exist_ok=True)
        
        # Konvertiere beide Dateien mit Preset-Parametern
        logging.info(f"📁 Konvertiere Dateien: {list(audio_files.keys())}")
        results = self.converter.batch_convert(audio_files, midi_dir, preset_params)
        
        # Speichere MIDI-Pfade in Session
        session.set_data('midi_files', {
            role: result.get('midi_path')
            for role, result in results.items()
            if result.get('success')
        })
        
        # Erstelle Summary
        summary = {
            "total_files": len(results),
            "successful": sum(1 for r in results.values() if r.get('success')),
            "failed": sum(1 for r in results.values() if not r.get('success')),
            "total_notes": sum(r.get('note_count', 0) for r in results.values()),
            "avg_confidence": {
                role: result.get('avg_confidence', 0.0)
                for role, result in results.items()
            },
            "warnings": [
                w for result in results.values()
                for w in result.get('warnings', [])
            ]
        }
        
        logging.info(
            f"✅ Konversion abgeschlossen: "
            f"{summary['successful']}/{summary['total_files']} erfolgreich"
        )
        
        result = {
            "referenz": results.get("referenz", {}),
            "schueler": results.get("schueler", {}),
            "summary": summary
        }
        
        # Füge Preset-Info hinzu falls verwendet
        if preset_info:
            result["preset_used"] = preset_info
        
        return result
    
    def analyze_and_compare(self, session_id: str) -> Dict:
        """Analysiert und vergleicht MIDIs taktbasiert.
        
        TODO: Phase 2 & 3 Implementation
        - Takt-Struktur extrahieren
        - Audio segmentieren
        - MIDI-Comparison pro Segment
        - Report generieren
        
        Args:
            session_id: Session-ID
            
        Returns:
            Dict mit Analyse-Ergebnissen
        """
        raise NotImplementedError("Phase 2 & 3: Noch nicht implementiert")
    
    def generate_report(self, session_id: str) -> str:
        """Generiert strukturierten Report.
        
        TODO: Phase 3 Implementation
        
        Args:
            session_id: Session-ID
            
        Returns:
            Markdown-formatierter Report
        """
        raise NotImplementedError("Phase 3: Noch nicht implementiert")
