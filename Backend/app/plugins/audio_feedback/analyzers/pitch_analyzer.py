# Pitch Analyzer - Tonhöhen-Analyse

import librosa
import numpy as np
from typing import Dict, Any, Tuple
from .base_analyzer import BaseAnalyzer

class PitchAnalyzer(BaseAnalyzer):
    """Analyzer für Tonhöhen-bezogene Features."""
    
    def analyze(self, audio_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Analysiert Tonhöhe und harmonische Features.
        
        Args:
            audio_data: Tuple von (audio_array, sample_rate)
            
        Returns:
            Dict mit Pitch-Features
        """
        y, sr = audio_data
        
        results = {}
        
        # Grundtonhöhe (Pitch)
        pitch_data = self._analyze_pitch(y, sr)
        results.update(pitch_data)
        
        # Tonart-Erkennung (Chroma Key)
        key_data = self._analyze_chroma_key(y, sr)
        results.update(key_data)
        
        # Akkord-Histogramm
        chord_data = self._analyze_chord_histogram(y, sr)
        results.update(chord_data)
        
        # Vibrato-Analyse
        vibrato_data = self._analyze_vibrato(y, sr)
        results.update(vibrato_data)
        
        return results
    
    def _analyze_pitch(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Analysiert die Grundtonhöhe."""
        pitches = librosa.yin(
            y, 
            fmin=librosa.note_to_hz("C2"), 
            fmax=librosa.note_to_hz("C7"), 
            sr=sr
        )
        valid_pitches = pitches[pitches > 0]
        
        if len(valid_pitches) > 0:
            mean_pitch = float(np.mean(valid_pitches))
            min_pitch = float(np.min(valid_pitches))
            max_pitch = float(np.max(valid_pitches))
        else:
            mean_pitch = min_pitch = max_pitch = 0.0
        
        return {
            "mean_pitch": mean_pitch,
            "min_pitch": min_pitch,
            "max_pitch": max_pitch,
        }
    
    def _analyze_chroma_key(self, y: np.ndarray, sr: int) -> Dict[str, str]:
        """Analysiert die Tonart."""
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_sums = np.sum(chroma, axis=1)
        key_idx = np.argmax(chroma_sums)
        key_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        key = key_names[key_idx]
        
        return {"estimated_key": key}
    
    def _analyze_chord_histogram(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analysiert Akkord-Verteilung."""
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        
        # Akkord-Templates (Dur und Moll)
        major_template = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
        minor_template = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])
        
        num_frames = chroma.shape[1]
        chord_sequence = []
        
        for frame_idx in range(num_frames):
            chroma_frame = chroma[:, frame_idx]
            best_corr = -1
            best_chord = "Unknown"
            
            for root in range(12):
                # Rotiere Templates
                major_rot = np.roll(major_template, root)
                minor_rot = np.roll(minor_template, root)
                
                # Korrelation
                corr_major = np.corrcoef(chroma_frame, major_rot)[0, 1]
                corr_minor = np.corrcoef(chroma_frame, minor_rot)[0, 1]
                
                if corr_major > best_corr:
                    best_corr = corr_major
                    key_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
                    best_chord = key_names[root] + "_major"
                
                if corr_minor > best_corr:
                    best_corr = corr_minor
                    key_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
                    best_chord = key_names[root] + "_minor"
            
            chord_sequence.append(best_chord)
        
        # Häufigste Akkorde
        from collections import Counter
        chord_counts = Counter(chord_sequence)
        most_common = chord_counts.most_common(3)
        
        return {
            "dominant_chord": most_common[0][0] if most_common else "Unknown",
            "chord_variety": len(set(chord_sequence))
        }
    
    def _analyze_vibrato(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Analysiert Vibrato."""
        pitches = librosa.yin(
            y, 
            fmin=librosa.note_to_hz("C2"), 
            fmax=librosa.note_to_hz("C7"), 
            sr=sr
        )
        valid_pitches = pitches[pitches > 0]
        
        if len(valid_pitches) > 10:
            # Vibrato als Standardabweichung der Tonhöhe
            vibrato_strength = float(np.std(valid_pitches))
            # Vibrato-Rate (Periodizität)
            autocorr = np.correlate(valid_pitches - np.mean(valid_pitches), 
                                   valid_pitches - np.mean(valid_pitches), 
                                   mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            peaks = []
            for i in range(1, len(autocorr)-1):
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                    peaks.append(i)
            
            vibrato_rate = float(peaks[0]) if peaks else 0.0
        else:
            vibrato_strength = 0.0
            vibrato_rate = 0.0
        
        return {
            "vibrato_strength": vibrato_strength,
            "vibrato_rate": vibrato_rate
        }
    
    def get_feature_names(self) -> list:
        """Gibt die Namen der extrahierten Features zurück."""
        return [
            'mean_pitch', 'min_pitch', 'max_pitch', 'estimated_key',
            'dominant_chord', 'chord_variety', 'vibrato_strength', 'vibrato_rate'
        ]
