"""
Interval Analyzer - Analysiert melodische Intervalle
"""

from typing import List
from ..models.midi_data import Note, TrackData
from ..models.analysis_result import IntervalAnalysis
from ..utils import classify_interval, get_movement_description


class IntervalAnalyzer:
    """Analysiert melodische Intervalle zwischen Noten"""
    
    def analyze(self, track: TrackData) -> IntervalAnalysis:
        """
        Analysiert die Intervalle zwischen aufeinanderfolgenden Noten
        
        Args:
            track: TrackData-Objekt
        
        Returns:
            IntervalAnalysis-Objekt mit Statistiken
        """
        # Filtere und sortiere Noten nach Zeit
        notes = sorted(
            [n for n in track.notes if n.velocity > 0],
            key=lambda x: x.time
        )
        
        if len(notes) < 2:
            return IntervalAnalysis(
                avg_interval=0.0,
                max_leap=0,
                interval_types=[],
                movement_description="Zu wenige Noten für Intervall-Analyse"
            )
        
        intervals = []
        interval_names = []
        
        for i in range(len(notes) - 1):
            interval = notes[i + 1].note_number - notes[i].note_number
            intervals.append(interval)
            interval_names.append(classify_interval(abs(interval)))
        
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        max_leap = max(abs(i) for i in intervals) if intervals else 0
        
        # Unique Intervall-Typen (max 10)
        unique_types = list(set(interval_names))[:10]
        
        movement = get_movement_description(max_leap)
        
        return IntervalAnalysis(
            avg_interval=avg_interval,
            max_leap=max_leap,
            interval_types=unique_types,
            movement_description=movement
        )
