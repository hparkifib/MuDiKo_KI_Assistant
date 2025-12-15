"""
Note Analyzer - Analysiert Noten (Tonhöhe, Bereich, etc.)
"""

from typing import List, Tuple
from ..models.midi_data import Note, TrackData
from ..models.analysis_result import NoteAnalysis


class NoteAnalyzer:
    """Analysiert Noten in einem Track"""
    
    def analyze(self, track: TrackData) -> NoteAnalysis:
        """
        Analysiert alle Noten in einem Track
        
        Args:
            track: TrackData-Objekt
        
        Returns:
            NoteAnalysis-Objekt mit Statistiken
        """
        # Filtere nur Note-Ons (keine Note-Offs)
        notes = [n for n in track.notes if n.velocity > 0]
        
        if not notes:
            return NoteAnalysis(
                count=0,
                lowest_note="N/A",
                highest_note="N/A",
                span_semitones=0,
                note_list=[]
            )
        
        # Zähle Noten
        count = len(notes)
        
        # Finde Notenbereich
        lowest_note, highest_note, span = self._get_note_range(notes)
        
        # Erstelle Notenliste für API
        note_list = self._create_note_list(notes)
        
        return NoteAnalysis(
            count=count,
            lowest_note=lowest_note,
            highest_note=highest_note,
            span_semitones=span,
            note_list=note_list
        )
    
    def _get_note_range(self, notes: List[Note]) -> Tuple[str, str, int]:
        """
        Findet tiefste und höchste Note
        
        Args:
            notes: Liste von Noten
        
        Returns:
            Tuple: (tiefste_note, höchste_note, span_in_semitones)
        """
        note_numbers = [n.note_number for n in notes]
        min_note = min(note_numbers)
        max_note = max(note_numbers)
        
        # Finde die Note-Objekte
        lowest = next(n for n in notes if n.note_number == min_note)
        highest = next(n for n in notes if n.note_number == max_note)
        
        span = max_note - min_note
        
        return lowest.note_name, highest.note_name, span
    
    def _create_note_list(self, notes: List[Note]) -> List[dict]:
        """
        Erstellt eine Liste von Noten für API-Export
        
        Args:
            notes: Liste von Noten
        
        Returns:
            Liste von Dicts mit Noten-Informationen
        """
        note_list = []
        
        for note in notes:
            note_dict = {
                'bar': note.bar,
                'beat': note.beat,
                'note': note.note_name,
                'duration': note.duration_type if note.duration_type else 'unbekannt',
                'velocity': note.velocity,
                'dynamic': note.dynamic
            }
            note_list.append(note_dict)
        
        return note_list
    
    def count_notes(self, notes: List[Note]) -> int:
        """
        Zählt die Anzahl der Noten
        
        Args:
            notes: Liste von Noten
        
        Returns:
            Anzahl der Noten
        """
        return len([n for n in notes if n.velocity > 0])
