# Timbre Analyzer - Klangfarben-Analyse (MFCC, Timbre Consistency)

import librosa
import numpy as np
from typing import Dict, Any, Tuple
from .base_analyzer import BaseAnalyzer

class TimbreAnalyzer(BaseAnalyzer):
    """Analyzer für Klangfarben-Features."""
    
    def __init__(self, target_sr: int = 22050, n_mfcc: int = 13):
        """Initialisiert den Timbre Analyzer.
        
        Args:
            target_sr: Ziel-Sample-Rate
            n_mfcc: Anzahl MFCC-Koeffizienten
        """
        super().__init__(target_sr)
        self.n_mfcc = n_mfcc
    
    def analyze(self, audio_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Analysiert Klangfarben-Features.
        
        Args:
            audio_data: Tuple von (audio_array, sample_rate)
            
        Returns:
            Dict mit Timbre-Features
        """
        y, sr = audio_data
        n_fft = min(2048, len(y))
        
        results = {}
        
        # MFCC (Mel-Frequency Cepstral Coefficients)
        mfcc_data = self._analyze_mfcc(y, sr, n_fft)
        results.update(mfcc_data)
        
        # Timbre Consistency
        consistency_data = self._analyze_timbre_consistency(y, sr, n_fft)
        results.update(consistency_data)
        
        return results
    
    def _analyze_mfcc(self, y: np.ndarray, sr: int, n_fft: int) -> Dict[str, float]:
        """Analysiert MFCC-Features."""
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc, n_fft=n_fft)
        mfcc_means = np.mean(mfccs, axis=1)
        mfcc_vars = np.var(mfccs, axis=1)
        
        return {
            "mfcc_mean_1": float(mfcc_means[0]),
            "mfcc_mean_2": float(mfcc_means[1]),
            "mfcc_mean_3": float(mfcc_means[2]),
            "mfcc_var_1": float(mfcc_vars[0]),
            "mfcc_var_2": float(mfcc_vars[1]),
            "mfcc_var_3": float(mfcc_vars[2]),
        }
    
    def _analyze_timbre_consistency(self, y: np.ndarray, sr: int, n_fft: int) -> Dict[str, float]:
        """Analysiert Klangfarben-Konsistenz."""
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc, n_fft=n_fft)
        
        # Varianz über die Zeit (niedrig = konsistenter)
        timbre_variance = float(np.mean(np.var(mfccs, axis=1)))
        
        # Durchschnittliche Distanz zwischen aufeinanderfolgenden Frames
        frame_distances = []
        for i in range(mfccs.shape[1] - 1):
            dist = np.linalg.norm(mfccs[:, i+1] - mfccs[:, i])
            frame_distances.append(dist)
        
        mean_frame_distance = float(np.mean(frame_distances)) if frame_distances else 0.0
        
        return {
            "timbre_variance": timbre_variance,
            "timbre_frame_distance": mean_frame_distance
        }
    
    def get_feature_names(self) -> list:
        """Gibt die Namen der extrahierten Features zurück."""
        return [
            'mfcc_mean_1', 'mfcc_mean_2', 'mfcc_mean_3',
            'mfcc_var_1', 'mfcc_var_2', 'mfcc_var_3',
            'timbre_variance', 'timbre_frame_distance'
        ]
