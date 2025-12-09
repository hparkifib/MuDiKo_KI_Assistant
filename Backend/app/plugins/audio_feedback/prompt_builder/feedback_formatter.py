# Feedback Formatter - Formatiert Analyse-Ergebnisse für Anzeige

from typing import Dict, Any

class FeedbackFormatter:
    """Formatter für Analyse-Ergebnisse und Feedback."""
    
    def format_analysis_results(self, results: Dict[str, Any], format_type: str = "detailed") -> str:
        """Formatiert Analyse-Ergebnisse.
        
        Args:
            results: Analyse-Ergebnisse
            format_type: 'detailed' oder 'compact'
            
        Returns:
            Formatierter String
        """
        if format_type == "detailed":
            return self._format_detailed(results)
        else:
            return self._format_compact(results)
    
    def _format_detailed(self, results: Dict[str, Any]) -> str:
        """Detaillierte Formatierung mit Erklärungen."""
        lines = []
        for key, value in results.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    lines.append(f"  {sub_key}: {sub_value}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    def _format_compact(self, results: Dict[str, Any]) -> str:
        """Kompakte Formatierung."""
        return ", ".join([f"{k}={v}" for k, v in results.items()])
