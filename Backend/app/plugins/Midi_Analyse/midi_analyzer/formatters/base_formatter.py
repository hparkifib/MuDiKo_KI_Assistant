"""
Base Formatter - Abstract Base Class für alle Formatter
"""

from abc import ABC, abstractmethod
from ..models.analysis_result import AnalysisResult
from ..models.comparison_result import ComparisonResult


class BaseFormatter(ABC):
    """Abstract Base Class für Output-Formatter"""
    
    @abstractmethod
    def format_analysis(self, result: AnalysisResult) -> str:
        """
        Formatiert ein Analyse-Ergebnis
        
        Args:
            result: AnalysisResult-Objekt
        
        Returns:
            Formatierter String
        """
        pass
    
    @abstractmethod
    def format_comparison(self, result: ComparisonResult) -> str:
        """
        Formatiert ein Vergleichs-Ergebnis
        
        Args:
            result: ComparisonResult-Objekt
        
        Returns:
            Formatierter String
        """
        pass
