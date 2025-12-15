"""
Datenmodelle für MIDI-Analyse
"""

from .midi_data import (
    Note,
    TempoChange,
    TimeSignature,
    KeySignature,
    ProgramChange,
    ControlChange,
    PedalEvent,
    TrackData,
    MidiData
)

from .analysis_result import (
    NoteAnalysis,
    DynamicsAnalysis,
    RhythmAnalysis,
    IntervalAnalysis,
    TrackAnalysis,
    AnalysisResult
)

from .comparison_result import (
    Difference,
    ComparisonSummary,
    ComparisonResult
)

__all__ = [
    # MIDI Data
    'Note',
    'TempoChange',
    'TimeSignature',
    'KeySignature',
    'ProgramChange',
    'ControlChange',
    'PedalEvent',
    'TrackData',
    'MidiData',
    # Analysis Results
    'NoteAnalysis',
    'DynamicsAnalysis',
    'RhythmAnalysis',
    'IntervalAnalysis',
    'TrackAnalysis',
    'AnalysisResult',
    # Comparison Results
    'Difference',
    'ComparisonSummary',
    'ComparisonResult',
]
