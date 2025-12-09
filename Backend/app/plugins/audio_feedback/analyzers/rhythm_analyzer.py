# Rhythm Analyzer - Rhythmus und Polyphonie-Analyse

import librosa
import numpy as np
from typing import Dict, Any, Tuple
from .base_analyzer import BaseAnalyzer

class RhythmAnalyzer(BaseAnalyzer):
    """Analyzer für erweiterte Rhythmus-Features und Polyphonie."""
    
    def analyze(self, audio_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Analysiert Rhythmus und Polyphonie.
        
        Args:
            audio_data: Tuple von (audio_array, sample_rate)
            
        Returns:
            Dict mit Rhythmus-Features
        """
        y, sr = audio_data
        
        results = {}
        
        # Polyphonie (Mehrstimmigkeit)
        polyphony_data = self._analyze_polyphony(y, sr)
        results.update(polyphony_data)
        
        return results
    
    def _analyze_polyphony(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Analysiert Polyphonie/Mehrstimmigkeit."""
        # Spectral Complexity als Indikator für Polyphonie
        n_fft = min(2048, len(y))
        S = np.abs(librosa.stft(y, n_fft=n_fft))
        
        # Anzahl aktiver Frequenzbänder pro Frame
        threshold = np.max(S) * 0.1  # 10% des Maximums
        active_bands = np.sum(S > threshold, axis=0)
        mean_active_bands = float(np.mean(active_bands))
        
        # Spectral Flatness (niedriger = mehr harmonische Struktur/Polyphonie)
        flatness = librosa.feature.spectral_flatness(y=y, n_fft=n_fft)[0]
        mean_flatness = float(np.mean(flatness))
        
        return {
            "polyphony_active_bands": mean_active_bands,
            "polyphony_spectral_flatness": mean_flatness
        }
    
    def get_feature_names(self) -> list:
        """Gibt die Namen der extrahierten Features zurück."""
        return ['polyphony_active_bands', 'polyphony_spectral_flatness']
