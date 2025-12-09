# Tempo Analyzer - Tempo- und Rhythmus-Analyse

import librosa
import numpy as np
from typing import Dict, Any, Tuple
from .base_analyzer import BaseAnalyzer

class TempoAnalyzer(BaseAnalyzer):
    """Analyzer für Tempo- und Rhythmus-bezogene Features."""
    
    def analyze(self, audio_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Analysiert Tempo und Rhythmus.
        
        Args:
            audio_data: Tuple von (audio_array, sample_rate)
            
        Returns:
            Dict mit Tempo-Features
        """
        y, sr = audio_data
        
        results = {}
        
        # Tempo (BPM)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        results['tempo'] = float(tempo)
        
        # Rhythmus-Stabilität
        rhythm_stability = self._analyze_rhythm_stability(y, sr)
        if rhythm_stability:
            results.update(rhythm_stability)
        
        # Onset Count (Anzahl Noteneinsätze)
        onsets = librosa.onset.onset_detect(y=y, sr=sr)
        results['onset_count'] = int(len(onsets))
        
        return results
    
    def _analyze_rhythm_stability(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Analysiert die Rhythmus-Stabilität.
        
        Args:
            y: Audio-Array
            sr: Sample-Rate
            
        Returns:
            Dict mit Rhythmus-Stabilitäts-Metriken oder None
        """
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
        if len(onsets) < 2:
            return None  # zu wenig Daten
        
        intervals = np.diff(onsets)  # Abstand zwischen den Onsets
        std_interval = float(np.std(intervals))
        mean_interval = float(np.mean(intervals))
        
        return {
            "rhythm_std_interval": std_interval,
            "rhythm_mean_interval": mean_interval
        }
    
    def get_feature_names(self) -> list:
        """Gibt die Namen der extrahierten Features zurück."""
        return ['tempo', 'onset_count', 'rhythm_std_interval', 'rhythm_mean_interval']
