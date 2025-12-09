# Spectral Analyzer - Spektrale Feature-Analyse

import librosa
import numpy as np
from typing import Dict, Any, Tuple
from .base_analyzer import BaseAnalyzer

class SpectralAnalyzer(BaseAnalyzer):
    """Analyzer für spektrale Features (Klangfarbe, Frequenzverteilung)."""
    
    def analyze(self, audio_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Analysiert spektrale Features.
        
        Args:
            audio_data: Tuple von (audio_array, sample_rate)
            
        Returns:
            Dict mit spektralen Features
        """
        y, sr = audio_data
        n_fft = min(2048, len(y))
        
        results = {}
        
        # Spectral Centroid (Klangfarbe/Helligkeit)
        centroid_data = self._analyze_spectral_centroid(y, sr, n_fft)
        results.update(centroid_data)
        
        # Spectral Bandwidth (Frequenzbreite)
        bandwidth_data = self._analyze_spectral_bandwidth(y, sr, n_fft)
        results.update(bandwidth_data)
        
        # Spectral Rolloff (Hochfrequenz-Anteil)
        rolloff_data = self._analyze_spectral_rolloff(y, sr, n_fft)
        results.update(rolloff_data)
        
        # Zero Crossing Rate (Rauschanteil)
        zcr_data = self._analyze_zero_crossing_rate(y, n_fft)
        results.update(zcr_data)
        
        return results
    
    def _analyze_spectral_centroid(self, y: np.ndarray, sr: int, n_fft: int) -> Dict[str, float]:
        """Analysiert Spectral Centroid (Klangfarbe)."""
        centroids = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=n_fft)[0]
        
        return {
            "mean_centroid": float(np.mean(centroids)),
            "min_centroid": float(np.min(centroids)),
            "max_centroid": float(np.max(centroids)),
        }
    
    def _analyze_spectral_bandwidth(self, y: np.ndarray, sr: int, n_fft: int) -> Dict[str, float]:
        """Analysiert Spectral Bandwidth."""
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, n_fft=n_fft)[0]
        
        return {
            "mean_bandwidth": float(np.mean(bandwidth)),
            "min_bandwidth": float(np.min(bandwidth)),
            "max_bandwidth": float(np.max(bandwidth)),
        }
    
    def _analyze_spectral_rolloff(self, y: np.ndarray, sr: int, n_fft: int) -> Dict[str, float]:
        """Analysiert Spectral Rolloff."""
        rolloff = librosa.feature.spectral_rolloff(
            y=y, sr=sr, roll_percent=0.85, n_fft=n_fft
        )[0]
        
        return {
            "mean_rolloff": float(np.mean(rolloff)),
            "min_rolloff": float(np.min(rolloff)),
            "max_rolloff": float(np.max(rolloff)),
        }
    
    def _analyze_zero_crossing_rate(self, y: np.ndarray, n_fft: int) -> Dict[str, float]:
        """Analysiert Zero Crossing Rate."""
        zcr = librosa.feature.zero_crossing_rate(y, frame_length=n_fft)[0]
        
        return {
            "mean_zcr": float(np.mean(zcr)),
            "min_zcr": float(np.min(zcr)),
            "max_zcr": float(np.max(zcr))
        }
    
    def get_feature_names(self) -> list:
        """Gibt die Namen der extrahierten Features zurück."""
        return [
            'mean_centroid', 'min_centroid', 'max_centroid',
            'mean_bandwidth', 'min_bandwidth', 'max_bandwidth',
            'mean_rolloff', 'min_rolloff', 'max_rolloff',
            'mean_zcr', 'min_zcr', 'max_zcr'
        ]
