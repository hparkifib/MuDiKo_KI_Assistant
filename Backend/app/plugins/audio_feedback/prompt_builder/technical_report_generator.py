# Technical Report Generator - Technischer Feature-Extraktion-Report
# 
# Diese Variante fokussiert sich auf rohe Feature-Daten ohne pädagogische
# Interpretation. Ideal für:
# - Technische Analyse
# - Machine Learning Pipelines
# - Vergleich mit anderen Systemen
# - Debug/Entwicklung

from typing import Dict, Any, List
from .base_report_generator import BaseReportGenerator

class TechnicalReportGenerator(BaseReportGenerator):
    """Generiert technischen Feature-Extraktion-Report ohne Kontext.
    
    Dieser Report liefert rohe Feature-Daten in strukturierter Form,
    ohne pädagogische Interpretationen oder aufwändige Formatierung.
    
    Features:
    - Plain-Text Formatierung
    - Technische Feature-Namen (wie im Code)
    - Keine Interpretationen
    - Kompakte Darstellung
    - Alle numerischen Werte präzise
    
    Use Cases:
    - Feature-Extraktion für ML-Modelle
    - Technische Dokumentation
    - Debugging und Entwicklung
    - Vergleich mit anderen Audio-Analyse-Tools
    """
    
    def _initialize_feature_mappings(self):
        """Verwendet technische Feature-Namen."""
        # Bei technischem Report: Feature-Namen = Key-Namen
        self.feature_contexts = {}
    
    def generate_report(self, segment_results: List[Dict[str, Any]]) -> str:
        """Generiert technischen Feature-Extraktion-Report.
        
        Args:
            segment_results: Liste der Segment-Analyse-Ergebnisse
            
        Returns:
            Kompakter Report mit rohen Feature-Daten
        """
        lines = ["\n" + "="*70]
        lines.append("FEATURE EXTRACTION REPORT")
        lines.append("="*70 + "\n")
        
        for idx, segment in enumerate(segment_results, 1):
            lines.append(f"SEGMENT {idx}")
            lines.append(f"Time Range: {segment['schueler_start']:.2f}s - {segment['schueler_end']:.2f}s")
            lines.append("-" * 40)
            
            analysis = segment.get('analysis', {})
            
            # Gruppiere nach Feature-Typen
            feature_groups = self._group_features_by_type(analysis)
            
            for group_name, features in feature_groups.items():
                if not features:
                    continue
                
                lines.append(f"\n{group_name.upper()}:")
                lines.extend(self._format_technical_features(features))
            
            lines.append("\n")
        
        lines.append("="*70)
        return "\n".join(lines)
    
    def _group_features_by_type(self, analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Gruppiert Features nach technischen Kategorien."""
        groups = {
            'temporal': {},
            'spectral': {},
            'harmonic': {},
            'dynamic': {},
            'comparison': {}
        }
        
        for key, value in analysis.items():
            if not self._is_feature_enabled(key.replace('referenz_', '').replace('schueler_', '')):
                continue
            
            # Kategorisiere Feature
            if any(kw in key.lower() for kw in ['tempo', 'onset', 'rhythm', 'attack']):
                groups['temporal'][key] = value
            elif any(kw in key.lower() for kw in ['centroid', 'bandwidth', 'rolloff', 'zcr', 'mfcc', 'timbre']):
                groups['spectral'][key] = value
            elif any(kw in key.lower() for kw in ['pitch', 'key', 'chord', 'chroma', 'vibrato']):
                groups['harmonic'][key] = value
            elif any(kw in key.lower() for kw in ['rms', 'dynamic', 'loudness', 'silence']):
                groups['dynamic'][key] = value
            elif any(kw in key.lower() for kw in ['distance', 'similarity', 'correlation', 'dtw']):
                groups['comparison'][key] = value
        
        return groups
    
    def _format_technical_features(self, features: Dict[str, Any]) -> List[str]:
        """Formatiert Features im technischen Stil."""
        lines = []
        
        for key, value in sorted(features.items()):
            formatted_val = self._format_value(value)
            lines.append(f"  {key}: {formatted_val}")
        
        return lines
