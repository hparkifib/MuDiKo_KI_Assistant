# Energy Comparator - Energie-Envelope-Vergleiche

import librosa
import numpy as np
from typing import Dict, Any, Tuple
from .base_comparator import BaseComparator

class EnergyComparator(BaseComparator):
    """Comparator für Energie- und Dynamik-Vergleiche."""
    
    def compare(self, ref_data: Tuple[np.ndarray, int], 
                sch_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Vergleicht Energie-Envelopes zwischen Referenz und Schüler.
        
        Args:
            ref_data: Referenz-Audio
            sch_data: Schüler-Audio
            
        Returns:
            Dict mit Energie-Vergleichsmetriken
        """
        results = {}
        
        # Energy Envelope Correlation
        energy_corr = self._compare_energy_envelope(ref_data, sch_data)
        results.update(energy_corr)
        
        return results
    
    def _compare_energy_envelope(self, ref_data: Tuple[np.ndarray, int], 
                                sch_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Vergleicht Energie-Envelopes."""
        y_ref, sr_ref = ref_data
        y_sch, sr_sch = sch_data
        n_fft = min(2048, len(y_ref), len(y_sch))
        
        frame_length = n_fft
        hop_length = min(512, frame_length // 2)
        
        energy_ref = librosa.feature.rms(
            y=y_ref, frame_length=frame_length, hop_length=hop_length
        )[0]
        energy_sch = librosa.feature.rms(
            y=y_sch, frame_length=frame_length, hop_length=hop_length
        )[0]
        
        min_len = min(len(energy_ref), len(energy_sch))
        if min_len < 2:
            return {"energy_envelope_correlation": None}
        
        energy_ref = energy_ref[:min_len]
        energy_sch = energy_sch[:min_len]
        
        correlation = float(np.corrcoef(energy_ref, energy_sch)[0, 1])
        
        return {"energy_envelope_correlation": correlation}
