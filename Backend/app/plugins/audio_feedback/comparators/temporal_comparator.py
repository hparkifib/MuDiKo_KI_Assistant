# Temporal Comparator - Zeit-basierte Vergleiche (DTW, RMS Correlation)

import librosa
import numpy as np
from typing import Dict, Any, Tuple
from .base_comparator import BaseComparator

class TemporalComparator(BaseComparator):
    """Comparator für zeitliche Vergleiche und Synchronisation."""
    
    def __init__(self, n_mfcc: int = 13):
        """Initialisiert den Temporal Comparator.
        
        Args:
            n_mfcc: Anzahl MFCC-Koeffizienten für DTW
        """
        self.n_mfcc = n_mfcc
    
    def compare(self, ref_data: Tuple[np.ndarray, int], 
                sch_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Vergleicht zeitliche Aspekte zwischen Referenz und Schüler.
        
        Args:
            ref_data: Referenz-Audio
            sch_data: Schüler-Audio
            
        Returns:
            Dict mit zeitlichen Vergleichsmetriken
        """
        results = {}
        
        # DTW Distance (Dynamic Time Warping)
        dtw_dist = self._compare_dtw(ref_data, sch_data)
        results.update(dtw_dist)
        
        # RMS Correlation (Lautstärke-Synchronisation)
        rms_corr = self._compare_rms(ref_data, sch_data)
        results.update(rms_corr)
        
        # Pitch Contour Similarity (Melodie-Verlauf)
        pitch_sim = self._compare_pitch_contour(ref_data, sch_data)
        results.update(pitch_sim)
        
        return results
    
    def _compare_dtw(self, ref_data: Tuple[np.ndarray, int], 
                    sch_data: Tuple[np.ndarray, int]) -> Dict[str, float]:
        """Vergleicht mit Dynamic Time Warping."""
        from librosa.sequence import dtw
        
        y_ref, sr_ref = ref_data
        y_sch, sr_sch = sch_data
        n_fft = min(2048, len(y_ref), len(y_sch))
        
        mfcc_ref = librosa.feature.mfcc(y=y_ref, sr=sr_ref, n_mfcc=self.n_mfcc, n_fft=n_fft)
        mfcc_sch = librosa.feature.mfcc(y=y_sch, sr=sr_sch, n_mfcc=self.n_mfcc, n_fft=n_fft)
        
        min_frames = min(mfcc_ref.shape[1], mfcc_sch.shape[1])
        mfcc_ref = mfcc_ref[:, :min_frames]
        mfcc_sch = mfcc_sch[:, :min_frames]
        
        D, wp = dtw(X=mfcc_ref, Y=mfcc_sch, metric="euclidean")
        dtw_dist = float(D[-1, -1])
        
        return {"dtw_distance": dtw_dist}
    
    def _compare_rms(self, ref_data: Tuple[np.ndarray, int], 
                    sch_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Vergleicht RMS (Lautstärke-Synchronisation)."""
        y_ref, sr_ref = ref_data
        y_sch, sr_sch = sch_data
        n_fft = min(2048, len(y_ref), len(y_sch))
        
        rms_ref = librosa.feature.rms(y=y_ref, frame_length=n_fft)[0]
        rms_sch = librosa.feature.rms(y=y_sch, frame_length=n_fft)[0]
        
        min_len = min(len(rms_ref), len(rms_sch))
        rms_ref = rms_ref[:min_len]
        rms_sch = rms_sch[:min_len]
        
        if min_len > 1:
            corr = float(np.corrcoef(rms_ref, rms_sch)[0, 1])
        else:
            corr = None
        
        return {"rms_correlation": corr}
    
    def _compare_pitch_contour(self, ref_data: Tuple[np.ndarray, int], 
                               sch_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Vergleicht Tonhöhen-Verläufe."""
        y_ref, sr_ref = ref_data
        y_sch, sr_sch = sch_data
        
        # Pitch contour mit YIN berechnen
        pitch_ref = librosa.yin(
            y_ref,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sr_ref,
        )
        pitch_sch = librosa.yin(
            y_sch,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sr_sch,
        )
        
        # Nur gültige (nicht-Null) Werte verwenden
        valid_ref = pitch_ref[pitch_ref > 0]
        valid_sch = pitch_sch[pitch_sch > 0]
        
        min_len = min(len(valid_ref), len(valid_sch))
        if min_len < 2:
            return {"pitch_contour_correlation": None}
        
        # Kürzen auf gleiche Länge
        valid_ref = valid_ref[:min_len]
        valid_sch = valid_sch[:min_len]
        
        corr = float(np.corrcoef(valid_ref, valid_sch)[0, 1])
        
        return {"pitch_contour_correlation": corr}
