"""
Rhythm Analyzer - Analysiert Rhythmus und Notenlängen
"""

from typing import List
from collections import Counter
from ..models.midi_data import Note, TrackData
from ..models.analysis_result import RhythmAnalysis


class RhythmAnalyzer:
    """Analysiert Rhythmus und Notenlängen"""
    
    def analyze(self, track: TrackData) -> RhythmAnalysis:
        """
        Analysiert den Rhythmus aller Noten in einem Track
        
        Args:
            track: TrackData-Objekt
        
        Returns:
            RhythmAnalysis-Objekt mit Statistiken
        """
        # Filtere nur Noten mit Dauer > 0
        notes = [n for n in track.notes if n.velocity > 0 and n.duration > 0]
        
        if not notes:
            return RhythmAnalysis(
                avg_duration_ticks=0.0,
                min_duration=0,
                max_duration=0,
                most_common_duration="N/A",
                duration_variety=[]
            )
        
        durations = [n.duration for n in notes]
        duration_types = [n.duration_type for n in notes if n.duration_type]
        
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        # Häufigste Notenlänge
        if duration_types:
            type_counter = Counter(duration_types)
            most_common = type_counter.most_common(1)[0][0]
            variety = list(set(duration_types))
        else:
            most_common = "unbekannt"
            variety = []
        
        return RhythmAnalysis(
            avg_duration_ticks=avg_duration,
            min_duration=min_duration,
            max_duration=max_duration,
            most_common_duration=most_common,
            duration_variety=variety
        )
