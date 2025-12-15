"""
Dynamics Analyzer - Analysiert Lautstärke/Velocity
"""

from typing import List, Dict
from ..models.midi_data import Note, TrackData
from ..models.analysis_result import DynamicsAnalysis
from ..utils import classify_dynamic, get_average_dynamic_name


class DynamicsAnalyzer:
    """Analysiert Dynamik (Lautstärke) der Noten"""
    
    def analyze(self, track: TrackData) -> DynamicsAnalysis:
        """
        Analysiert die Dynamik aller Noten in einem Track
        
        Args:
            track: TrackData-Objekt
        
        Returns:
            DynamicsAnalysis-Objekt mit Statistiken
        """
        # Filtere nur Note-Ons
        notes = [n for n in track.notes if n.velocity > 0]
        
        if not notes:
            return DynamicsAnalysis(
                avg_velocity=0.0,
                min_velocity=0,
                max_velocity=0,
                velocity_range=0,
                avg_dynamic_name="N/A",
                distribution={}
            )
        
        velocities = [n.velocity for n in notes]
        
        avg_vel = sum(velocities) / len(velocities)
        min_vel = min(velocities)
        max_vel = max(velocities)
        vel_range = max_vel - min_vel
        
        avg_dynamic = get_average_dynamic_name(avg_vel)
        distribution = self._get_dynamic_distribution(notes)
        
        return DynamicsAnalysis(
            avg_velocity=avg_vel,
            min_velocity=min_vel,
            max_velocity=max_vel,
            velocity_range=vel_range,
            avg_dynamic_name=avg_dynamic,
            distribution=distribution
        )
    
    def _get_dynamic_distribution(self, notes: List[Note]) -> Dict[str, int]:
        """
        Berechnet die Verteilung der Dynamik-Stufen
        
        Args:
            notes: Liste von Noten
        
        Returns:
            Dict mit Dynamik-Stufen und deren Häufigkeit
        """
        distribution = {
            'ppp': 0, 'pp': 0, 'p': 0, 'mp': 0,
            'mf': 0, 'f': 0, 'ff': 0, 'fff': 0
        }
        
        for note in notes:
            dynamic = classify_dynamic(note.velocity)
            distribution[dynamic] += 1
        
        # Entferne Einträge mit 0
        return {k: v for k, v in distribution.items() if v > 0}
