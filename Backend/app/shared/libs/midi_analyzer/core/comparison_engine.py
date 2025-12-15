"""
Comparison Engine - Vergleicht zwei MIDI-Analysen
"""

from typing import List, Dict, Any
from ..models.midi_data import TrackData, Note
from ..models.analysis_result import AnalysisResult, TrackAnalysis
from ..models.comparison_result import Difference, ComparisonSummary, ComparisonResult
from ..utils import get_position_key


class ComparisonEngine:
    """Vergleicht zwei MIDI-Analysen und findet Unterschiede"""
    
    def compare(
        self,
        analysis1: AnalysisResult,
        analysis2: AnalysisResult
    ) -> ComparisonResult:
        """
        Vergleicht zwei Analyse-Ergebnisse
        
        Args:
            analysis1: Erste Analyse (Referenz)
            analysis2: Zweite Analyse (Vergleich)
        
        Returns:
            ComparisonResult-Objekt mit allen Unterschieden
        """
        differences = []
        
        # Vergleiche jeden Track
        max_tracks = max(len(analysis1.tracks), len(analysis2.tracks))
        
        for i in range(max_tracks):
            if i < len(analysis1.tracks) and i < len(analysis2.tracks):
                track_diffs = self._compare_tracks(
                    analysis1.tracks[i],
                    analysis2.tracks[i],
                    i
                )
                differences.extend(track_diffs)
        
        # Erstelle Summary
        summary = self._create_summary(analysis1, analysis2, differences)
        
        return ComparisonResult(
            file1_analysis=analysis1,
            file2_analysis=analysis2,
            differences=differences,
            summary=summary
        )
    
    def _compare_tracks(
        self,
        track1: TrackAnalysis,
        track2: TrackAnalysis,
        track_num: int
    ) -> List[Difference]:
        """
        Vergleicht zwei Tracks und findet Unterschiede
        
        Args:
            track1: Erster Track
            track2: Zweiter Track
            track_num: Track-Nummer
        
        Returns:
            Liste von Difference-Objekten
        """
        differences = []
        
        # Vergleiche Noten wenn vorhanden
        if track1.note_analysis and track2.note_analysis:
            note_diffs = self._compare_notes(
                track1.note_analysis.note_list,
                track2.note_analysis.note_list,
                track_num
            )
            differences.extend(note_diffs)
        
        return differences
    
    def _compare_notes(
        self,
        notes1: List[Dict[str, Any]],
        notes2: List[Dict[str, Any]],
        track_num: int
    ) -> List[Difference]:
        """
        Vergleicht Noten an denselben Positionen
        
        Args:
            notes1: Noten von Track 1
            notes2: Noten von Track 2
            track_num: Track-Nummer
        
        Returns:
            Liste von Unterschieden
        """
        differences = []
        
        # Gruppiere Noten nach Takt.Schlag
        notes1_by_pos = self._group_notes_by_position(notes1)
        notes2_by_pos = self._group_notes_by_position(notes2)
        
        # Finde alle Positionen
        all_positions = sorted(
            set(list(notes1_by_pos.keys()) + list(notes2_by_pos.keys())),
            key=lambda x: (int(x.split(',')[0].split()[1]), 
                          int(x.split(',')[1].split()[1]))
        )
        
        for pos in all_positions:
            n1 = notes1_by_pos.get(pos, [])
            n2 = notes2_by_pos.get(pos, [])
            
            if self._notes_differ(n1, n2):
                bar, beat = self._parse_position(pos)
                
                diff = Difference(
                    track=track_num,
                    bar=bar,
                    beat=beat,
                    type='note_difference',
                    expected=self._format_notes(n1),
                    actual=self._format_notes(n2),
                    message=f"In Takt {bar}, Schlag {beat}: Unterschied in Noten",
                    severity='medium'
                )
                differences.append(diff)
        
        return differences
    
    def _group_notes_by_position(
        self, notes: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Gruppiert Noten nach Takt.Schlag Position
        
        Args:
            notes: Liste von Noten
        
        Returns:
            Dict mit Position als Key und Notenliste als Value
        """
        grouped = {}
        
        for note in notes:
            pos = get_position_key(note['bar'], note['beat'])
            if pos not in grouped:
                grouped[pos] = []
            grouped[pos].append(note)
        
        return grouped
    
    def _notes_differ(
        self, notes1: List[Dict[str, Any]], notes2: List[Dict[str, Any]]
    ) -> bool:
        """
        Prüft ob zwei Notenlisten unterschiedlich sind
        
        Args:
            notes1: Erste Notenliste
            notes2: Zweite Notenliste
        
        Returns:
            True wenn unterschiedlich
        """
        # Vergleiche Noten-Namen und Längen
        str1 = self._format_notes(notes1)
        str2 = self._format_notes(notes2)
        
        return str1 != str2
    
    def _format_notes(self, notes: List[Dict[str, Any]]) -> str:
        """
        Formatiert Notenliste zu String für Vergleich
        
        Args:
            notes: Notenliste
        
        Returns:
            Formatierter String
        """
        if not notes:
            return "keine Noten"
        
        formatted = []
        for note in notes:
            duration = note.get('duration', 'unbekannt')
            formatted.append(f"{note['note']} ({duration})")
        
        return ", ".join(formatted)
    
    def _parse_position(self, pos: str) -> tuple:
        """
        Parst Position-String zu Takt und Schlag
        
        Args:
            pos: String wie "Takt 3, Zählzeit 2"
        
        Returns:
            Tuple (bar, beat)
        """
        parts = pos.split(',')
        bar = int(parts[0].split()[1])
        beat = int(parts[1].split()[1])
        return bar, beat
    
    def _create_summary(
        self,
        analysis1: AnalysisResult,
        analysis2: AnalysisResult,
        differences: List[Difference]
    ) -> ComparisonSummary:
        """
        Erstellt eine Zusammenfassung des Vergleichs
        
        Args:
            analysis1: Erste Analyse
            analysis2: Zweite Analyse
            differences: Liste der Unterschiede
        
        Returns:
            ComparisonSummary-Objekt
        """
        total_diffs = len(differences)
        
        # Zähle Fehlertypen
        note_errors = len([d for d in differences if 'note' in d.type.lower()])
        rhythm_errors = len([d for d in differences if 'rhythm' in d.type.lower() or 'duration' in d.type.lower()])
        dynamics_errors = len([d for d in differences if 'velocity' in d.type.lower() or 'dynamic' in d.type.lower()])
        
        # Berechne Similarity Score (vereinfacht)
        max_notes = max(analysis1.total_notes, analysis2.total_notes)
        if max_notes > 0:
            similarity = 1.0 - (total_diffs / max_notes)
            similarity = max(0.0, min(1.0, similarity))
            similarity *= 100.0  # in Prozent
        else:
            similarity = 1.0
            similarity *= 100.0  # in Prozent
        
        length_diff = abs(analysis1.length_seconds - analysis2.length_seconds)
        note_diff = abs(analysis1.total_notes - analysis2.total_notes)
        
        return ComparisonSummary(
            total_differences=total_diffs,
            note_errors=note_errors,
            rhythm_errors=rhythm_errors,
            dynamics_errors=dynamics_errors,
            similarity_score=similarity,
            length_difference=length_diff,
            note_count_difference=note_diff
        )
