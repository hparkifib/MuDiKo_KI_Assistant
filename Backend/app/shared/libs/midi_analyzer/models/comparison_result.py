"""
Datenmodelle für Vergleichs-Ergebnisse
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .analysis_result import AnalysisResult


@dataclass
class Difference:
    """Ein einzelner Unterschied zwischen zwei MIDI-Dateien"""
    track: int
    bar: int
    beat: int
    type: str  # 'wrong_note', 'missing_note', 'extra_note', 'wrong_duration', 'wrong_velocity'
    expected: Optional[str] = None
    actual: Optional[str] = None
    message: str = ""
    severity: str = "medium"  # 'low', 'medium', 'high'
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'track': self.track,
            'position': {
                'bar': self.bar,
                'beat': self.beat
            },
            'type': self.type,
            'message': self.message,
            'severity': self.severity
        }
        
        if self.expected:
            result['expected'] = self.expected
        
        if self.actual:
            result['actual'] = self.actual
        
        return result


@dataclass
class ComparisonSummary:
    """Zusammenfassung eines Vergleichs"""
    total_differences: int
    note_errors: int = 0
    rhythm_errors: int = 0
    dynamics_errors: int = 0
    similarity_score: float = 1.0
    length_difference: float = 0.0
    note_count_difference: int = 0
    # First-Note-Synchronisation Info
    sync_applied: bool = False
    sync_bar_offset: int = 0
    sync_beat_offset: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'total_differences': self.total_differences,
            'error_types': {
                'note_errors': self.note_errors,
                'rhythm_errors': self.rhythm_errors,
                'dynamics_errors': self.dynamics_errors
            },
            'similarity_score': round(self.similarity_score, 3),
            'differences': {
                'length_seconds': round(self.length_difference, 2),
                'note_count': self.note_count_difference
            }
        }
        
        # Füge Sync-Info hinzu wenn angewendet
        if self.sync_applied:
            result['synchronization'] = {
                'applied': True,
                'bar_offset': self.sync_bar_offset,
                'beat_offset': self.sync_beat_offset,
                'note': 'Schüleraufnahme wurde automatisch zur ersten Note synchronisiert'
            }
        
        return result


@dataclass
class ComparisonResult:
    """Komplettes Vergleichs-Ergebnis"""
    file1_analysis: AnalysisResult
    file2_analysis: AnalysisResult
    differences: List[Difference] = field(default_factory=list)
    summary: Optional[ComparisonSummary] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'reference': self.file1_analysis.to_dict(),
            'comparison': self.file2_analysis.to_dict(),
            'differences': [d.to_dict() for d in self.differences],
            'summary': self.summary.to_dict() if self.summary else {}
        }
    
    def to_json(self) -> str:
        """Konvertiert zu JSON-String"""
        import json
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def get_differences(self) -> List[Dict[str, Any]]:
        """Gibt nur die Unterschiede zurück"""
        return [d.to_dict() for d in self.differences]
    
    def get_summary(self) -> Dict[str, Any]:
        """Gibt nur die Zusammenfassung zurück"""
        result = {
            'file1': self.file1_analysis.to_summary(),
            'file2': self.file2_analysis.to_summary()
        }
        
        if self.summary:
            result.update(self.summary.to_dict())
        
        return result
