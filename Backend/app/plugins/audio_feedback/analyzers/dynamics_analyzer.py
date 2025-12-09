# Dynamics Analyzer - Lautstärke und Dynamik-Analyse

import librosa
import numpy as np
from typing import Dict, Any, Tuple
from .base_analyzer import BaseAnalyzer

class DynamicsAnalyzer(BaseAnalyzer):
    """Analyzer für Lautstärke und Dynamik-Features."""
    
    def analyze(self, audio_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Analysiert Lautstärke und Dynamik.
        
        Args:
            audio_data: Tuple von (audio_array, sample_rate)
            
        Returns:
            Dict mit Dynamik-Features
        """
        y, sr = audio_data
        n_fft = min(2048, len(y))
        
        results = {}
        
        # Gesamtlänge
        results['length'] = len(y) / sr
        
        # Lautstärke (RMS)
        loudness_data = self._analyze_loudness(y, n_fft)
        results.update(loudness_data)
        
        # Dynamik-Bereich
        dynamics_data = self._analyze_dynamics(y, n_fft)
        results.update(dynamics_data)
        
        # Stille-Analyse
        silences_data = self._analyze_silences(y, sr)
        results.update(silences_data)
        
        # Attack Time
        attack_data = self._analyze_attack_time(y, sr)
        results.update(attack_data)
        
        return results
    
    def _analyze_loudness(self, y: np.ndarray, n_fft: int) -> Dict[str, float]:
        """Analysiert Lautstärke (RMS)."""
        rms = librosa.feature.rms(y=y, frame_length=n_fft)[0]
        
        return {
            "mean_rms": float(np.mean(rms)),
            "max_rms": float(np.max(rms)),
            "min_rms": float(np.min(rms))
        }
    
    def _analyze_dynamics(self, y: np.ndarray, n_fft: int) -> Dict[str, float]:
        """Analysiert Dynamik-Bereich."""
        rms = librosa.feature.rms(y=y, frame_length=n_fft)[0]
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)
        
        return {
            "dynamic_range_db": float(np.max(rms_db) - np.min(rms_db)),
            "dynamic_std_db": float(np.std(rms_db))
        }
    
    def _analyze_silences(self, y: np.ndarray, sr: int, top_db: int = 30) -> Dict[str, Any]:
        """Analysiert Pausen/Stille."""
        intervals = librosa.effects.split(y, top_db=top_db)
        total_duration = len(y) / sr
        music_duration = sum((end - start) for start, end in intervals) / sr
        silence_duration = total_duration - music_duration
        num_silences = max(0, len(intervals) - 1)
        
        longest_silence = 0.0
        if len(intervals) > 1:
            silences = [
                (intervals[i][1], intervals[i + 1][0])
                for i in range(len(intervals) - 1)
            ]
            longest_silence = max((b - a) / sr for a, b in silences)
        
        return {
            "num_silences": num_silences,
            "total_silence_duration": float(silence_duration),
            "longest_silence": float(longest_silence),
        }
    
    def _analyze_attack_time(self, y: np.ndarray, sr: int, threshold: float = 0.2) -> Dict[str, float]:
        """Analysiert Attack Time (Anschlag-Geschwindigkeit)."""
        rms = librosa.feature.rms(y=y)[0]
        max_rms = np.max(rms)
        threshold_value = threshold * max_rms
        
        attack_times = []
        for i in range(len(rms) - 1):
            if rms[i] < threshold_value and rms[i + 1] >= threshold_value:
                # Finde Peak nach Threshold-Überschreitung
                peak_idx = i + 1
                while peak_idx < len(rms) - 1 and rms[peak_idx + 1] > rms[peak_idx]:
                    peak_idx += 1
                
                attack_time = (peak_idx - i) * (512 / sr)  # hop_length default = 512
                attack_times.append(attack_time)
        
        if attack_times:
            return {
                "mean_attack_time": float(np.mean(attack_times)),
                "min_attack_time": float(np.min(attack_times)),
                "max_attack_time": float(np.max(attack_times))
            }
        else:
            return {
                "mean_attack_time": 0.0,
                "min_attack_time": 0.0,
                "max_attack_time": 0.0
            }
    
    def get_feature_names(self) -> list:
        """Gibt die Namen der extrahierten Features zurück."""
        return [
            'length', 'mean_rms', 'max_rms', 'min_rms',
            'dynamic_range_db', 'dynamic_std_db',
            'num_silences', 'total_silence_duration', 'longest_silence',
            'mean_attack_time', 'min_attack_time', 'max_attack_time'
        ]
