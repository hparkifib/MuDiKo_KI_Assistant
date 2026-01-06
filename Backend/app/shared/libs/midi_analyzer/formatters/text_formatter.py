"""
Text Formatter - Formatiert Ergebnisse als LLM-freundlichen Text
"""

from typing import List
from .base_formatter import BaseFormatter
from ..models.analysis_result import AnalysisResult, TrackAnalysis
from ..models.comparison_result import ComparisonResult


class TextFormatter(BaseFormatter):
    """Formatiert Ergebnisse als menschenlesbaren Text für LLM-Analyse"""
    
    def format_analysis(self, result: AnalysisResult) -> str:
        """
        Formatiert Analyse-Ergebnis als Text (für Stand-alone Analysen)
        
        Args:
            result: AnalysisResult-Objekt
        
        Returns:
            Formatierter Text
        """
        output = []
        output.append("MIDI-ANALYSE")
        output.append("=" * 80)
        output.append(f"Datei: {result.filename}")
        output.append(f"Länge: {result.length_seconds:.2f} Sekunden")
        output.append(f"Anzahl Spuren: {result.total_tracks}")
        output.append(f"Gesamtzahl Noten: {result.total_notes}")
        output.append("")
        
        for track in result.tracks:
            if track.note_analysis and track.note_analysis.count > 0:
                output.append(f"Spur {track.track_number}: {track.track_name}")
                output.append(f"  - Noten: {track.note_analysis.count}")
                output.append("")
        
        return "\n".join(output)
    
    def format_comparison(self, result: ComparisonResult) -> str:
        """
        Formatiert Vergleichs-Ergebnis als Text (minimale Version)
        
        Args:
            result: ComparisonResult-Objekt
        
        Returns:
            Formatierter Text
        """
        output = []
        output.append("VERGLEICH ZWEIER MUSIKSTÜCKE")
        output.append("=" * 80)
        output.append("Für die Analyse durch ein KI-System")
        output.append("=" * 80 + "\n")
        
        # Dateinamen
        output.append(f"Erstes Musikstück (Referenz):  {result.file1_analysis.filename}")
        output.append(f"Zweites Musikstück (Vergleich): {result.file2_analysis.filename}")
        
        # Zusammenfassung
        if result.summary:
            output.append(f"\nÄhnlichkeit: {result.summary.similarity_score * 100:.1f}%")
            output.append(f"Unterschiede gefunden: {result.summary.total_differences}")
        
        # Detaillierter Vergleich
        output.append("\n" + "=" * 80)
        output.append("DETAILLIERTER VERGLEICH: TAKT FÜR TAKT")
        output.append("=" * 80)
        output.append("\nHier werden beide Musikstücke Takt für Takt verglichen.\n")
        
        output.extend(self._format_side_by_side(result))
        
        return "\n".join(output)
    
    def _format_side_by_side(self, result: ComparisonResult) -> List[str]:
        """Formatiert den vollständigen Takt-für-Takt Vergleich (ohne Fehlermarkierung)"""
        output = []
        
        # Finde alle Tracks, die in mindestens einer Datei existieren
        max_tracks = max(len(result.file1_analysis.tracks), len(result.file2_analysis.tracks))
        
        for track_num in range(max_tracks):
            # Hole Track-Informationen
            track1 = None
            track2 = None
            track_name = ""
            
            if track_num < len(result.file1_analysis.tracks):
                track1 = result.file1_analysis.tracks[track_num]
                track_name = track1.track_name
            
            if track_num < len(result.file2_analysis.tracks):
                track2 = result.file2_analysis.tracks[track_num]
                if not track_name and track2:
                    track_name = track2.track_name
            
            # Extrahiere Noten aus beiden Tracks
            notes1_by_pos = self._group_notes_by_position(track1)
            notes2_by_pos = self._group_notes_by_position(track2)
            
            # Wenn beide Tracks keine Noten haben, überspringe
            if not notes1_by_pos and not notes2_by_pos:
                continue
            
            # Finde alle Positionen aus beiden Tracks
            all_positions = sorted(set(list(notes1_by_pos.keys()) + list(notes2_by_pos.keys())),
                                 key=lambda x: (x[0], x[1]))  # Sortiere nach (bar, beat)
            
            # Wenn keine Positionen vorhanden sind, überspringe
            if not all_positions:
                continue
            
            # Track-Header
            output.append(f"\n### Spur {track_num}: {track_name}\n")
            output.append("Position            | Referenz                                                  | Vergleich")
            output.append("-" * 130)
            
            # Zeige alle Positionen (ohne Fehlermarkierung - das LLM entscheidet selbst)
            for bar, beat in all_positions:
                pos_str = f"Takt {bar}, Zählzeit {beat}"
                notes1 = notes1_by_pos.get((bar, beat), [])
                notes2 = notes2_by_pos.get((bar, beat), [])
                
                # Formatiere Noten mit Längenangabe
                notes1_str = self._format_notes(notes1) if notes1 else "keine Noten"
                notes2_str = self._format_notes(notes2) if notes2 else "keine Noten"
                
                # Keine Fehlermarkierung mehr - das LLM analysiert selbst
                output.append(f"{pos_str:19s} | {notes1_str:57s} | {notes2_str:57s}")
        
        return output
    
    def _group_notes_by_position(self, track: TrackAnalysis) -> dict:
        """Gruppiert Noten nach (Takt, Zählzeit)"""
        if not track or not track.note_analysis or not track.note_analysis.note_list:
            return {}
        
        notes_by_pos = {}
        for note in track.note_analysis.note_list:
            bar = note.get('bar', 0)
            beat = note.get('beat', 0)
            key = (bar, beat)
            
            if key not in notes_by_pos:
                notes_by_pos[key] = []
            
            notes_by_pos[key].append(note)
        
        return notes_by_pos
    
    def _format_notes(self, notes: list) -> str:
        """Formatiert eine Liste von Noten mit Längenangabe"""
        if not notes:
            return "keine Noten"
        
        formatted_notes = []
        for note in notes:
            note_name = note.get('note', '?')
            duration = note.get('duration', 'unbekannt')
            formatted_notes.append(f"{note_name} ({duration})")
        
        return ", ".join(formatted_notes)
