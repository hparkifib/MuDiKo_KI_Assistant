# Feature Comparator - MFCC und Chroma-Vergleiche

import librosa
import numpy as np
import scipy.spatial
from typing import Dict, Any, Tuple
from .base_comparator import BaseComparator

class FeatureComparator(BaseComparator):
    """Comparator für Feature-basierte Vergleiche (MFCC, Chroma)."""
    
    def __init__(self, n_mfcc: int = 13):
        """Initialisiert den Feature Comparator.
        
        Args:
            n_mfcc: Anzahl MFCC-Koeffizienten
        """
        self.n_mfcc = n_mfcc
    
    def compare(self, ref_data: Tuple[np.ndarray, int], 
                sch_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Vergleicht Features zwischen Referenz und Schüler.
        
        Args:
            ref_data: Referenz-Audio
            sch_data: Schüler-Audio
            
        Returns:
            Dict mit Vergleichsmetriken
        """
        results = {}
        
        # MFCC Distance
        mfcc_dist = self._compare_mfcc(ref_data, sch_data)
        results.update(mfcc_dist)
        
        # Chroma Similarity
        chroma_sim = self._compare_chroma(ref_data, sch_data)
        results.update(chroma_sim)
        
        return results
    
    def _compare_mfcc(self, ref_data: Tuple[np.ndarray, int], 
                     sch_data: Tuple[np.ndarray, int]) -> Dict[str, float]:
        """Vergleicht MFCC-Features."""
        y_ref, sr_ref = ref_data
        y_sch, sr_sch = sch_data
        n_fft = min(2048, len(y_ref), len(y_sch))
        
        mfcc_ref = np.mean(
            librosa.feature.mfcc(y=y_ref, sr=sr_ref, n_mfcc=self.n_mfcc, n_fft=n_fft), 
            axis=1
        )
        mfcc_sch = np.mean(
            librosa.feature.mfcc(y=y_sch, sr=sr_sch, n_mfcc=self.n_mfcc, n_fft=n_fft), 
            axis=1
        )
        
        distance = float(scipy.spatial.distance.euclidean(mfcc_ref, mfcc_sch))
        
        return {"mfcc_distance": distance}
    
    def _compare_chroma(self, ref_data: Tuple[np.ndarray, int], 
                       sch_data: Tuple[np.ndarray, int]) -> Dict[str, float]:
        """Vergleicht Chroma-Features (harmonische Ähnlichkeit)."""
        from sklearn.metrics.pairwise import cosine_similarity
        
        y_ref, sr_ref = ref_data
        y_sch, sr_sch = sch_data
        
        chroma_ref = librosa.feature.chroma_cqt(y=y_ref, sr=sr_ref)
        chroma_sch = librosa.feature.chroma_cqt(y=y_sch, sr=sr_sch)
        
        # Mittelwert über die Zeit
        chroma_ref_mean = np.mean(chroma_ref, axis=1).reshape(1, -1)
        chroma_sch_mean = np.mean(chroma_sch, axis=1).reshape(1, -1)
        
        similarity = float(cosine_similarity(chroma_ref_mean, chroma_sch_mean)[0, 0])
        
        return {"chroma_similarity": similarity}
