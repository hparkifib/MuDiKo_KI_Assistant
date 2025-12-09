# Base Comparator - Abstract Base Class für Vergleichsanalysen

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class BaseComparator(ABC):
    """Abstract Base Class für Audio Comparators.
    
    Comparators vergleichen Features zwischen Referenz- und Schüler-Aufnahmen.
    """
    
    @abstractmethod
    def compare(self, ref_data: Tuple[np.ndarray, int], 
                sch_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Vergleicht zwei Audio-Aufnahmen.
        
        Args:
            ref_data: Referenz-Audio als (audio_array, sample_rate)
            sch_data: Schüler-Audio als (audio_array, sample_rate)
            
        Returns:
            Dict mit Vergleichsmetriken
        """
        pass
