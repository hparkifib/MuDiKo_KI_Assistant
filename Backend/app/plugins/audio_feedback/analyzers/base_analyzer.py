# Base Analyzer - Abstract Base Class für alle Feature-Analyzer

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class BaseAnalyzer(ABC):
    """Abstract Base Class für Audio Feature Analyzer.
    
    Jeder Analyzer ist verantwortlich für die Extraktion spezifischer
    Audio-Features und folgt dem Single Responsibility Principle.
    """
    
    def __init__(self, target_sr: int = 22050):
        """Initialisiert den Analyzer.
        
        Args:
            target_sr: Ziel-Sample-Rate für Audio-Verarbeitung
        """
        self.target_sr = target_sr
    
    @abstractmethod
    def analyze(self, audio_data: Tuple[np.ndarray, int]) -> Dict[str, Any]:
        """Analysiert Audio-Daten und extrahiert Features.
        
        Args:
            audio_data: Tuple von (audio_array, sample_rate)
            
        Returns:
            Dict mit analysierten Features
        """
        pass
    
    def get_feature_names(self) -> list:
        """Gibt die Namen der extrahierten Features zurück.
        
        Returns:
            Liste von Feature-Namen
        """
        return []
