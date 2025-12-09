# Audio Service - Basis-Service für Audio-Operationen

import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional

class AudioService:
    """Basis-Service für Audio-Operationen (wiederverwendbar für alle Tools)."""
    
    def __init__(self, target_sr: int = 22050):
        """Initialisiert den Audio Service.
        
        Args:
            target_sr: Ziel-Sample-Rate für Audio-Verarbeitung (Standard: 22050 Hz)
        """
        self.target_sr = target_sr
    
    def load_audio(self, file_path: Path, sr: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """Lädt eine Audio-Datei.
        
        Args:
            file_path: Pfad zur Audio-Datei
            sr: Sample-Rate (None = Ziel-SR verwenden)
            
        Returns:
            Tuple[np.ndarray, int]: Audio-Daten und Sample-Rate
        """
        target = sr if sr is not None else self.target_sr
        y, sr = librosa.load(str(file_path), sr=target)
        return y, sr
    
    def save_audio(self, audio_data: np.ndarray, file_path: Path, sr: Optional[int] = None):
        """Speichert Audio-Daten.
        
        Args:
            audio_data: Audio-Daten als numpy array
            file_path: Ziel-Pfad
            sr: Sample-Rate (None = Ziel-SR verwenden)
        """
        target = sr if sr is not None else self.target_sr
        sf.write(str(file_path), audio_data, target)
    
    def segment_audio(self, audio_data: np.ndarray, sr: int, 
                     segment_length_sec: int = 8) -> List[np.ndarray]:
        """Segmentiert Audio in gleich große Teile.
        
        Args:
            audio_data: Audio-Daten
            sr: Sample-Rate
            segment_length_sec: Segment-Länge in Sekunden (Standard: 8)
            
        Returns:
            List[np.ndarray]: Liste von Audio-Segmenten
        """
        segment_samples = segment_length_sec * sr
        num_segments = int(np.ceil(len(audio_data) / segment_samples))
        
        segments = []
        for i in range(num_segments):
            start = i * segment_samples
            end = min(start + segment_samples, len(audio_data))
            segment = audio_data[start:end]
            
            # Padding falls zu kurz
            if len(segment) < segment_samples:
                segment = np.pad(
                    segment, 
                    (0, segment_samples - len(segment)), 
                    mode='constant'
                )
            segments.append(segment)
        
        return segments
    
    def segment_and_save(self, file_path: Path, output_dir: Path, 
                        segment_length_sec: int = 8,
                        base_filename: Optional[str] = None) -> List[str]:
        """Lädt, segmentiert und speichert eine Audio-Datei.
        
        Args:
            file_path: Pfad zur Eingabe-Datei
            output_dir: Ausgabe-Verzeichnis für Segmente
            segment_length_sec: Segment-Länge in Sekunden
            base_filename: Basis-Name für Segment-Dateien (oder aus file_path)
            
        Returns:
            List[str]: Liste der Segment-Dateinamen
        """
        # Lade Audio
        audio_data, sr = self.load_audio(file_path)
        
        # Segmentiere
        segments = self.segment_audio(audio_data, sr, segment_length_sec)
        
        # Bestimme Basis-Namen
        if base_filename is None:
            base_filename = file_path.stem  # Dateiname ohne Endung
        
        # Erstelle Segments-Ordner
        segments_dir = output_dir / "segments"
        segments_dir.mkdir(exist_ok=True)
        
        # Speichere Segmente
        segment_filenames = []
        for i, segment in enumerate(segments):
            segment_filename = f"{base_filename}_segment_{i}.wav"
            segment_path = segments_dir / segment_filename
            self.save_audio(segment, segment_path, sr)
            segment_filenames.append(segment_filename)
        
        print(f"🎵 {len(segments)} Segmente erstellt: {base_filename}")
        return segment_filenames
    
    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalisiert Audio-Lautstärke.
        
        Args:
            audio_data: Audio-Daten
            
        Returns:
            np.ndarray: Normalisierte Audio-Daten
        """
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val
        return audio_data
    
    def get_duration(self, audio_data: np.ndarray, sr: int) -> float:
        """Berechnet die Dauer einer Audio-Datei.
        
        Args:
            audio_data: Audio-Daten
            sr: Sample-Rate
            
        Returns:
            float: Dauer in Sekunden
        """
        return len(audio_data) / float(sr)
    
    def trim_silence(self, audio_data: np.ndarray, 
                     top_db: int = 20) -> np.ndarray:
        """Entfernt Stille am Anfang und Ende.
        
        Args:
            audio_data: Audio-Daten
            top_db: Threshold in dB unter Maximum
            
        Returns:
            np.ndarray: Audio ohne führende/nachfolgende Stille
        """
        trimmed, _ = librosa.effects.trim(audio_data, top_db=top_db)
        return trimmed
