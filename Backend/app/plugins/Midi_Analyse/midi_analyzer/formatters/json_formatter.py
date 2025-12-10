"""
JSON Formatter - Formatiert Ergebnisse als JSON
"""

import json
from .base_formatter import BaseFormatter
from ..models.analysis_result import AnalysisResult
from ..models.comparison_result import ComparisonResult


class JSONFormatter(BaseFormatter):
    """Formatiert Ergebnisse als JSON für API-Responses"""
    
    def __init__(self, pretty: bool = True, ensure_ascii: bool = False):
        """
        Initialisiert den JSON-Formatter
        
        Args:
            pretty: Wenn True, wird JSON formatiert (mit Einrückung)
            ensure_ascii: Wenn False, werden Unicode-Zeichen nicht escaped
        """
        self.pretty = pretty
        self.ensure_ascii = ensure_ascii
    
    def format_analysis(self, result: AnalysisResult) -> str:
        """
        Formatiert Analyse-Ergebnis als JSON
        
        Args:
            result: AnalysisResult-Objekt
        
        Returns:
            JSON-String
        """
        data = result.to_dict()
        
        if self.pretty:
            return json.dumps(data, indent=2, ensure_ascii=self.ensure_ascii)
        else:
            return json.dumps(data, ensure_ascii=self.ensure_ascii)
    
    def format_comparison(self, result: ComparisonResult) -> str:
        """
        Formatiert Vergleichs-Ergebnis als JSON
        
        Args:
            result: ComparisonResult-Objekt
        
        Returns:
            JSON-String
        """
        data = result.to_dict()
        
        if self.pretty:
            return json.dumps(data, indent=2, ensure_ascii=self.ensure_ascii)
        else:
            return json.dumps(data, ensure_ascii=self.ensure_ascii)
