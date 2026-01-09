"""MP3-to-MIDI Converter Service - Orchestriert die MIDI-Konversion."""

from pathlib import Path
from typing import Dict, Optional
import logging

from .mp3_to_midi_converter import Mp3ToMidiConverter
from .conversion_optimizer import ConversionParameterOptimizer
from app.core.exceptions import AudioAnalysisError


class Mp3ToMidiFeedbackService:
    """Service für MP3-to-MIDI Konversion.
    
    Konvertiert MP3/WAV-Aufnahmen mit Spotify's Basic Pitch zu MIDI-Dateien.
    Parameter werden automatisch aus der Audio-Analyse berechnet.
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
        
        # Initialisiere Parameter-Optimizer
        self.optimizer = ConversionParameterOptimizer(audio_service)
        
        logging.info("🎹 Mp3ToMidiFeedbackService initialisiert")
    
    def convert_mp3_to_midi(self, session_id: str) -> Dict:
        """Konvertiert beide MP3-Dateien (Referenz + Schüler) zu MIDI.
        
        Parameter werden automatisch aus der Audio-Analyse der Referenz berechnet.
        
        Args:
            session_id: Session-ID
            
        Returns:
            Dict mit:
                - referenz: Konversions-Result für Referenz
                - schueler: Konversions-Result für Schüler
                - summary: Zusammenfassung
                
        Raises:
            SessionNotFoundException: Session nicht gefunden
            FileNotFoundError: Audio-Dateien nicht gefunden
            AudioAnalysisError: Audio-Analyse fehlgeschlagen
        """
        logging.info(f"🎵 Starte MP3-to-MIDI Konversion für Session {session_id}")
        
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
        
        # Berechne optimale Parameter aus Referenz-Audio-Analyse
        referenz_path = audio_files.get('referenz')
        try:
            optimized_params = self.optimizer.optimize(referenz_path)
            logging.info("🔧 Parameter aus Audio-Analyse berechnet")
        except AudioAnalysisError as e:
            # Analyse fehlgeschlagen = Problem mit der Audio-Datei
            logging.error(f"❌ Audio-Analyse fehlgeschlagen: {e}")
            raise
        
        # Konvertiere beide Dateien mit optimierten Parametern
        logging.info(f"📁 Konvertiere Dateien: {list(audio_files.keys())}")
        results = self.converter.batch_convert(audio_files, midi_dir, optimized_params)
        
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
        
        return {
            "referenz": results.get("referenz", {}),
            "schueler": results.get("schueler", {}),
            "summary": summary
        }
