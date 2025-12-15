"""
Datenmodelle für Analyse-Ergebnisse
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class NoteAnalysis:
    """Analyse der Noten"""
    count: int
    lowest_note: str
    highest_note: str
    span_semitones: int
    note_list: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'count': self.count,
            'range': {
                'lowest': self.lowest_note,
                'highest': self.highest_note,
                'span_semitones': self.span_semitones
            },
            'notes': self.note_list
        }


@dataclass
class DynamicsAnalysis:
    """Analyse der Dynamik (Lautstärke)"""
    avg_velocity: float
    min_velocity: int
    max_velocity: int
    velocity_range: int
    avg_dynamic_name: str
    distribution: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'average_velocity': round(self.avg_velocity, 2),
            'range': [self.min_velocity, self.max_velocity],
            'velocity_range': self.velocity_range,
            'average_dynamic': self.avg_dynamic_name,
            'distribution': self.distribution
        }


@dataclass
class RhythmAnalysis:
    """Analyse des Rhythmus"""
    avg_duration_ticks: float
    min_duration: int
    max_duration: int
    most_common_duration: str
    duration_variety: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'average_duration_ticks': round(self.avg_duration_ticks, 2),
            'min_duration': self.min_duration,
            'max_duration': self.max_duration,
            'most_common': self.most_common_duration,
            'variety': self.duration_variety
        }


@dataclass
class IntervalAnalysis:
    """Analyse der melodischen Intervalle"""
    avg_interval: float
    max_leap: int
    interval_types: List[str] = field(default_factory=list)
    movement_description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'average_interval': round(self.avg_interval, 2),
            'max_leap': self.max_leap,
            'interval_types': self.interval_types,
            'movement': self.movement_description
        }


@dataclass
class TrackAnalysis:
    """Komplette Analyse eines Tracks"""
    track_number: int
    track_name: str
    note_analysis: Optional[NoteAnalysis] = None
    dynamics_analysis: Optional[DynamicsAnalysis] = None
    rhythm_analysis: Optional[RhythmAnalysis] = None
    interval_analysis: Optional[IntervalAnalysis] = None
    tempo_changes: List[Dict[str, Any]] = field(default_factory=list)
    time_signatures: List[Dict[str, Any]] = field(default_factory=list)
    key_signatures: List[Dict[str, Any]] = field(default_factory=list)
    program_changes: List[Dict[str, Any]] = field(default_factory=list)
    pedal_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'track_number': self.track_number,
            'track_name': self.track_name,
        }
        
        if self.note_analysis:
            result['notes'] = self.note_analysis.to_dict()
        
        if self.dynamics_analysis:
            result['dynamics'] = self.dynamics_analysis.to_dict()
        
        if self.rhythm_analysis:
            result['rhythm'] = self.rhythm_analysis.to_dict()
        
        if self.interval_analysis:
            result['intervals'] = self.interval_analysis.to_dict()
        
        if self.tempo_changes:
            result['tempo'] = self.tempo_changes
        
        if self.time_signatures:
            result['time_signatures'] = self.time_signatures
        
        if self.key_signatures:
            result['key_signatures'] = self.key_signatures
        
        if self.program_changes:
            result['instruments'] = self.program_changes
        
        if self.pedal_count > 0:
            result['pedal_usage'] = {'pedal_presses': self.pedal_count}
        
        return result


@dataclass
class AnalysisResult:
    """Komplettes Analyse-Ergebnis einer MIDI-Datei"""
    filename: str
    length_seconds: float
    ticks_per_beat: int
    midi_type: int
    tracks: List[TrackAnalysis] = field(default_factory=list)
    total_notes: int = 0
    total_tracks: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'file_info': {
                'filename': self.filename,
                'length_seconds': round(self.length_seconds, 2),
                'ticks_per_beat': self.ticks_per_beat,
                'midi_type': self.midi_type
            },
            'tracks': [t.to_dict() for t in self.tracks],
            'statistics': {
                'total_notes': self.total_notes,
                'total_tracks': self.total_tracks
            }
        }
    
    def to_json(self) -> str:
        """Konvertiert zu JSON-String"""
        import json
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def to_summary(self) -> Dict[str, Any]:
        """Kompakte Zusammenfassung für UI"""
        return {
            'filename': self.filename,
            'duration': round(self.length_seconds, 2),
            'tracks': self.total_tracks,
            'notes': self.total_notes
        }
