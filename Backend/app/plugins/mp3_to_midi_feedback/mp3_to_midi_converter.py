"""MP3-to-MIDI Converter - Basic Pitch Integration."""

import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Optional
import logging

try:
    from basic_pitch.inference import predict
    from basic_pitch import ICASSP_2022_MODEL_PATH
    BASIC_PITCH_AVAILABLE = True
except ImportError:
    BASIC_PITCH_AVAILABLE = False
    logging.warning("Basic Pitch nicht installiert. MP3-to-MIDI Konversion nicht verfügbar.")


class Mp3ToMidiConverter:
    """Konvertiert Audio-Dateien zu MIDI via Spotify's Basic Pitch.
    
    Basic Pitch ist ein ML-Modell für polyphonic pitch tracking und note transcription.
    Es extrahiert Noten aus Audio und gibt Confidence-Scores pro Note zurück.
    """
    
    def __init__(self, plugin_config: Optional[Dict] = None):
        """Initialisiert den Converter.
        
        Args:
            plugin_config: Plugin-Konfiguration mit conversion settings
        """
        if not BASIC_PITCH_AVAILABLE:
            raise ImportError(
                "Basic Pitch ist nicht installiert. "
                "Installiere mit: pip install basic-pitch"
            )
        
        self.plugin_config = plugin_config or {}
        self.settings = self.plugin_config.get('settings', {}).get('conversion', {})
        
        # Hole Settings
        self.timeout_seconds = self.settings.get('timeout_seconds', 120)
        self.min_confidence = self.settings.get('min_confidence', 0.6)
        self.fallback_on_low_confidence = self.settings.get('fallback_on_low_confidence', 'warning')
        
        logging.info(f"🎹 Mp3ToMidiConverter initialisiert (min_confidence={self.min_confidence})")
    
    def convert(self, audio_path: Path, output_path: Path, preset_params: Optional[Dict] = None) -> Dict:
        """Konvertiert Audio-Datei zu MIDI.
        
        Args:
            audio_path: Pfad zur Audio-Datei (MP3/WAV)
            output_path: Pfad für Output-MIDI-Datei
            preset_params: Optional - Basic Pitch Parameter aus Preset
                          (onset_threshold, frame_threshold, minimum_note_length, etc.)
            
        Returns:
            Dict mit:
                - midi_path: Pfad zur erstellten MIDI-Datei
                - confidence_scores: Liste von Confidence-Scores pro Note
                - avg_confidence: Durchschnittliche Confidence
                - note_count: Anzahl erkannter Noten
                - success: Boolean
                - warnings: Liste von Warnungen
                
        Raises:
            FileNotFoundError: Audio-Datei nicht gefunden
            TimeoutError: Conversion dauert zu lange
            ValueError: Keine Noten erkannt
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio-Datei nicht gefunden: {audio_path}")
        
        logging.info(f"🎵 Konvertiere {audio_path.name} zu MIDI...")
        
        warnings = []
        
        # Extrahiere Basic Pitch Parameter aus Preset
        onset_threshold = 0.5  # Default
        frame_threshold = 0.3  # Default
        minimum_note_length = None  # Use Basic Pitch default
        minimum_frequency = None
        maximum_frequency = None
        melodia_trick = False  # Default
        
        if preset_params:
            onset_threshold = preset_params.get('onset_threshold', 0.5)
            frame_threshold = preset_params.get('frame_threshold', 0.3)
            minimum_note_length = preset_params.get('minimum_note_length')
            minimum_frequency = preset_params.get('minimum_frequency')
            maximum_frequency = preset_params.get('maximum_frequency')
            melodia_trick = preset_params.get('melodia_trick', False)
            
            logging.info(
                f"📊 Verwende Preset-Parameter: onset={onset_threshold}, "
                f"frame={frame_threshold}, melodia_trick={melodia_trick}"
            )
        
        try:
            # Basic Pitch Prediction mit Parametern
            # predict() gibt zurück: (model_output, midi_data, note_events)
            model_output, midi_data, note_events = predict(
                str(audio_path),
                model_or_model_path=ICASSP_2022_MODEL_PATH,
                onset_threshold=onset_threshold,
                frame_threshold=frame_threshold,
                minimum_note_length=minimum_note_length,
                minimum_frequency=minimum_frequency,
                maximum_frequency=maximum_frequency,
                melodia_trick=melodia_trick
            )
            
            # Extrahiere Confidence-Scores aus note_events
            # note_events: List[(start_time, end_time, pitch, velocity, optional_confidence)]
            confidence_scores = []
            if note_events and len(note_events) > 0:
                for note in note_events:
                    # Basic Pitch note format: (start, end, pitch, velocity)
                    # Confidence ist im model_output enthalten, nicht direkt in note_events
                    # Wir nutzen velocity als Proxy für Confidence (0-127 normalisiert)
                    if len(note) >= 4:
                        velocity = note[3]
                        confidence = velocity / 127.0  # Normalisiere auf 0-1
                        confidence_scores.append(confidence)
            
            note_count = len(note_events) if note_events else 0
            
            if note_count == 0:
                error_msg = "Keine Noten erkannt. Audio möglicherweise zu leise oder unverständlich."
                if self.fallback_on_low_confidence == 'abort':
                    raise ValueError(error_msg)
                else:
                    warnings.append(error_msg)
            
            # Berechne durchschnittliche Confidence
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            # Prüfe Confidence-Threshold
            if avg_confidence < self.min_confidence:
                warning_msg = (
                    f"Niedrige Konversions-Qualität (Confidence: {avg_confidence:.2%}). "
                    "Ergebnisse könnten unzuverlässig sein."
                )
                warnings.append(warning_msg)
                
                if self.fallback_on_low_confidence == 'abort':
                    raise ValueError(warning_msg)
            
            # Speichere MIDI-Datei
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # midi_data ist ein pretty_midi.PrettyMIDI Objekt
            # Verwende die write() Methode
            try:
                midi_data.write(str(output_path))
            except Exception as e:
                logging.error(f"Fehler beim Schreiben der MIDI-Datei: {e}")
                raise IOError(f"MIDI-Datei konnte nicht geschrieben werden: {e}")
            
            logging.info(
                f"✅ Konversion erfolgreich: {note_count} Noten, "
                f"Confidence: {avg_confidence:.2%}"
            )
            
            return {
                "midi_path": str(output_path),
                "confidence_scores": confidence_scores,
                "avg_confidence": float(avg_confidence),
                "note_count": note_count,
                "success": True,
                "warnings": warnings
            }
            
        except Exception as e:
            logging.error(f"❌ Konversion fehlgeschlagen: {e}")
            raise
    
    def batch_convert(self, audio_files: Dict[str, Path], output_dir: Path, preset_params: Optional[Dict] = None) -> Dict[str, Dict]:
        """Konvertiert mehrere Audio-Dateien zu MIDI.
        
        Args:
            audio_files: Dict mit role -> audio_path mapping
                         z.B. {"referenz": Path(...), "schueler": Path(...)}
            output_dir: Verzeichnis für Output-MIDI-Dateien
            preset_params: Optional - Basic Pitch Parameter aus Preset
            
        Returns:
            Dict mit role -> conversion_result mapping
        """
        results = {}
        
        for role, audio_path in audio_files.items():
            output_path = output_dir / f"{role}_MP3_to_MIDI.mid"
            
            try:
                result = self.convert(audio_path, output_path, preset_params)
                results[role] = result
            except Exception as e:
                results[role] = {
                    "success": False,
                    "error": str(e),
                    "midi_path": None,
                    "confidence_scores": [],
                    "avg_confidence": 0.0,
                    "note_count": 0,
                    "warnings": [str(e)]
                }
        
        return results
