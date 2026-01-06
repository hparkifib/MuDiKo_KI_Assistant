"""
Comparison Engine - Vergleicht zwei MIDI-Analysen

Liefert nur Rohdaten und Basis-Statistiken - keine Fehlermarkierungen.
Das LLM entscheidet selbst, was ein echter Fehler ist.

Unterstützt First-Note-Synchronisation für Schüleraufnahmen mit
anfänglicher Stille oder ungewollten Pausen.
"""

from typing import Dict, Any, Optional
from copy import deepcopy
from ..models.analysis_result import AnalysisResult
from ..models.comparison_result import ComparisonSummary, ComparisonResult


# Mindest-Velocity für "echte" Noten (filtert leise Fehlnoten/Geräusche)
MIN_VELOCITY_THRESHOLD = 30


class ComparisonEngine:
    """Vergleicht zwei MIDI-Analysen.
    
    Liefert nur Rohdaten ohne Fehlermarkierungen.
    Das LLM kann den musikalischen Kontext besser einschätzen.
    
    Unterstützt automatische Synchronisation der ersten Note, um
    anfängliche Stille in Schüleraufnahmen auszugleichen.
    """
    
    def compare(
        self,
        analysis1: AnalysisResult,
        analysis2: AnalysisResult,
        auto_sync: bool = True
    ) -> ComparisonResult:
        """
        Vergleicht zwei Analyse-Ergebnisse.
        
        Liefert nur die synchronisierten Rohdaten und Basis-Statistiken.
        Keine Fehlermarkierungen - das LLM entscheidet selbst.
        
        Args:
            analysis1: Erste Analyse (Referenz)
            analysis2: Zweite Analyse (Vergleich/Schüler)
            auto_sync: Wenn True, wird die Schüleraufnahme automatisch
                      zur ersten Note der Referenz synchronisiert
        
        Returns:
            ComparisonResult-Objekt mit Rohdaten
        """
        # Optional: Synchronisiere Schüleraufnahme zur ersten Note
        sync_info = None
        if auto_sync:
            analysis2, sync_info = self._sync_to_first_note(analysis1, analysis2)
        
        # Erstelle Summary (nur Basis-Statistiken, keine Fehler)
        summary = self._create_summary(analysis1, analysis2, sync_info)
        
        return ComparisonResult(
            file1_analysis=analysis1,
            file2_analysis=analysis2,
            differences=[],  # Keine Fehlermarkierungen mehr
            summary=summary
        )
    
    def _sync_to_first_note(
        self,
        reference: AnalysisResult,
        student: AnalysisResult
    ) -> tuple:
        """
        Synchronisiert die Schüleraufnahme zur ersten Note der Referenz.
        
        Findet die erste "echte" Note (velocity > threshold) in beiden
        Aufnahmen und verschiebt die Takt/Schlag-Positionen der Schüler-Noten
        entsprechend.
        
        Args:
            reference: Referenz-Analyse
            student: Schüler-Analyse
        
        Returns:
            Tuple (synchronisierte_analyse, sync_info_dict)
        """
        # Finde erste echte Note in Referenz
        ref_first = self._find_first_significant_note(reference)
        # Finde erste echte Note in Schüleraufnahme
        student_first = self._find_first_significant_note(student)
        
        if ref_first is None or student_first is None:
            return student, {'synced': False, 'reason': 'Keine Noten gefunden'}
        
        # Berechne Offset in Takten und Schlägen
        bar_offset = student_first['bar'] - ref_first['bar']
        beat_offset = student_first['beat'] - ref_first['beat']
        
        # Wenn kein Offset nötig, gib Original zurück
        if bar_offset == 0 and beat_offset == 0:
            return student, {'synced': False, 'reason': 'Kein Offset nötig'}
        
        # Erstelle tiefe Kopie und verschiebe alle Noten
        synced_student = self._apply_offset(student, bar_offset, beat_offset)
        
        sync_info = {
            'synced': True,
            'bar_offset': bar_offset,
            'beat_offset': beat_offset,
            'ref_first_note': f"Takt {ref_first['bar']}, Schlag {ref_first['beat']}",
            'student_first_note': f"Takt {student_first['bar']}, Schlag {student_first['beat']}"
        }
        
        return synced_student, sync_info
    
    def _find_first_significant_note(
        self,
        analysis: AnalysisResult
    ) -> Optional[Dict[str, Any]]:
        """
        Findet die erste Note mit ausreichender Velocity.
        
        Args:
            analysis: Analyse-Ergebnis
            
        Returns:
            Dict mit 'bar', 'beat', 'note' oder None
        """
        first_note = None
        
        for track in analysis.tracks:
            if not track.note_analysis or not track.note_analysis.note_list:
                continue
                
            for note in track.note_analysis.note_list:
                # Filtere leise Noten (Geräusche, Fehlnoten)
                velocity = note.get('velocity', 0)
                if velocity < MIN_VELOCITY_THRESHOLD:
                    continue
                
                bar = note.get('bar', 0)
                beat = note.get('beat', 0)
                
                # Prüfe ob diese Note früher ist
                if first_note is None:
                    first_note = {'bar': bar, 'beat': beat, 'note': note.get('note', '?')}
                elif (bar < first_note['bar']) or \
                     (bar == first_note['bar'] and beat < first_note['beat']):
                    first_note = {'bar': bar, 'beat': beat, 'note': note.get('note', '?')}
        
        return first_note
    
    def _apply_offset(
        self,
        analysis: AnalysisResult,
        bar_offset: int,
        beat_offset: int
    ) -> AnalysisResult:
        """
        Wendet einen Takt/Schlag-Offset auf alle Noten an.
        
        Args:
            analysis: Original-Analyse
            bar_offset: Offset in Takten (wird subtrahiert)
            beat_offset: Offset in Schlägen (wird subtrahiert)
            
        Returns:
            Neue AnalysisResult mit verschobenen Noten
        """
        # Tiefe Kopie erstellen
        synced = deepcopy(analysis)
        
        for track in synced.tracks:
            if not track.note_analysis or not track.note_analysis.note_list:
                continue
            
            adjusted_notes = []
            for note in track.note_analysis.note_list:
                # Kopiere Note und passe Position an
                new_note = dict(note)
                new_bar = note.get('bar', 0) - bar_offset
                new_beat = note.get('beat', 0) - beat_offset
                
                # Handle negative beats (Übertrag zum vorherigen Takt)
                # Annahme: 4/4 Takt = 4 Schläge pro Takt
                while new_beat < 1:
                    new_beat += 4
                    new_bar -= 1
                while new_beat > 4:
                    new_beat -= 4
                    new_bar += 1
                
                # Ignoriere Noten die vor Takt 1 landen würden
                if new_bar < 1:
                    continue
                
                new_note['bar'] = new_bar
                new_note['beat'] = new_beat
                adjusted_notes.append(new_note)
            
            track.note_analysis.note_list = adjusted_notes
            track.note_analysis.count = len(adjusted_notes)
        
        return synced

    def _create_summary(
        self,
        analysis1: AnalysisResult,
        analysis2: AnalysisResult,
        sync_info: Optional[Dict[str, Any]] = None
    ) -> ComparisonSummary:
        """
        Erstellt eine Zusammenfassung mit Basis-Statistiken.
        
        Keine Fehler-Zählung mehr - nur Rohdaten für das LLM.
        
        Args:
            analysis1: Erste Analyse
            analysis2: Zweite Analyse
            sync_info: Optional - Info zur First-Note-Synchronisation
        
        Returns:
            ComparisonSummary-Objekt
        """
        length_diff = abs(analysis1.length_seconds - analysis2.length_seconds)
        note_diff = abs(analysis1.total_notes - analysis2.total_notes)
        
        summary = ComparisonSummary(
            total_differences=0,  # Keine Fehler-Zählung mehr
            note_errors=0,
            rhythm_errors=0,
            dynamics_errors=0,
            similarity_score=0.0,  # LLM bewertet selbst
            length_difference=length_diff,
            note_count_difference=note_diff
        )
        
        # Füge Sync-Info hinzu wenn vorhanden
        if sync_info and sync_info.get('synced'):
            summary.sync_applied = True
            summary.sync_bar_offset = sync_info.get('bar_offset', 0)
            summary.sync_beat_offset = sync_info.get('beat_offset', 0)
        
        return summary
