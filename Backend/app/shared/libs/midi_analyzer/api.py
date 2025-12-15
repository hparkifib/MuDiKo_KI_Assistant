"""
Public API - Hauptfassade für MIDI-Analyse
"""

from typing import Union, BinaryIO
from .core import (
    MidiParser, NoteAnalyzer, RhythmAnalyzer,
    DynamicsAnalyzer, IntervalAnalyzer, ComparisonEngine
)
from .models import AnalysisResult, ComparisonResult, TrackAnalysis
from .formatters import TextFormatter, JSONFormatter


class MidiAnalyzer:
    """
    Hauptklasse für MIDI-Analyse und -Vergleich
    
    Diese Klasse ist die primäre Schnittstelle für Backend-Integration.
    Sie orchestriert alle Analyzer und bietet eine einfache API.
    
    Beispiel:
        analyzer = MidiAnalyzer()
        result = analyzer.analyze_file("song.mid")
        json_output = result.to_json()
    """
    
    def __init__(self):
        """Initialisiert den MidiAnalyzer mit allen benötigten Komponenten"""
        self.parser = MidiParser()
        self.note_analyzer = NoteAnalyzer()
        self.rhythm_analyzer = RhythmAnalyzer()
        self.dynamics_analyzer = DynamicsAnalyzer()
        self.interval_analyzer = IntervalAnalyzer()
        self.comparison_engine = ComparisonEngine()
        self.text_formatter = TextFormatter()
        self.json_formatter = JSONFormatter()
    
    def analyze_file(self, filepath: str) -> AnalysisResult:
        """
        Analysiert eine MIDI-Datei vom Dateisystem
        
        Args:
            filepath: Pfad zur MIDI-Datei
        
        Returns:
            AnalysisResult mit vollständiger Analyse
        
        Raises:
            FileNotFoundError: Wenn Datei nicht existiert
            ValueError: Wenn Datei kein gültiges MIDI ist
        
        Beispiel:
            result = analyzer.analyze_file("song.mid")
            print(f"Gefunden: {result.total_notes} Noten")
        """
        # Parse MIDI
        midi_data = self.parser.parse_file(filepath)
        
        # Analysiere
        return self._analyze_midi_data(midi_data)
    
    def analyze_bytes(
        self, data: bytes, filename: str = "uploaded.mid"
    ) -> AnalysisResult:
        """
        Analysiert MIDI-Daten aus Bytes (für File-Uploads)
        
        Args:
            data: MIDI-Datei als Bytes
            filename: Optionaler Dateiname für Referenz
        
        Returns:
            AnalysisResult mit vollständiger Analyse
        
        Raises:
            ValueError: Wenn Daten kein gültiges MIDI sind
        
        Beispiel:
            with open("song.mid", "rb") as f:
                data = f.read()
            result = analyzer.analyze_bytes(data, "song.mid")
        """
        # Parse MIDI
        midi_data = self.parser.parse_bytes(data, filename)
        
        # Analysiere
        return self._analyze_midi_data(midi_data)
    
    def compare_files(
        self, file1: str, file2: str
    ) -> ComparisonResult:
        """
        Vergleicht zwei MIDI-Dateien
        
        Args:
            file1: Pfad zur ersten Datei (Referenz)
            file2: Pfad zur zweiten Datei (Vergleich)
        
        Returns:
            ComparisonResult mit allen Unterschieden
        
        Beispiel:
            result = analyzer.compare_files("reference.mid", "performance.mid")
            print(f"Gefunden: {result.summary.total_differences} Unterschiede")
        """
        analysis1 = self.analyze_file(file1)
        analysis2 = self.analyze_file(file2)
        
        return self.comparison_engine.compare(analysis1, analysis2)
    
    def compare_bytes(
        self,
        data1: bytes,
        data2: bytes,
        filename1: str = "reference.mid",
        filename2: str = "comparison.mid"
    ) -> ComparisonResult:
        """
        Vergleicht zwei MIDI-Dateien aus Bytes
        
        Args:
            data1: Erste MIDI-Datei als Bytes (Referenz)
            data2: Zweite MIDI-Datei als Bytes (Vergleich)
            filename1: Optionaler Dateiname für erste Datei
            filename2: Optionaler Dateiname für zweite Datei
        
        Returns:
            ComparisonResult mit allen Unterschieden
        
        Beispiel:
            result = analyzer.compare_bytes(ref_data, perf_data)
            differences = result.get_differences()
        """
        analysis1 = self.analyze_bytes(data1, filename1)
        analysis2 = self.analyze_bytes(data2, filename2)
        
        return self.comparison_engine.compare(analysis1, analysis2)
    
    def _analyze_midi_data(self, midi_data) -> AnalysisResult:
        """
        Interne Methode: Führt die vollständige Analyse durch
        
        Args:
            midi_data: Geparste MIDI-Daten
        
        Returns:
            AnalysisResult
        """
        tracks = []
        total_notes = 0
        
        for track_data in midi_data.tracks:
            # Filtere nur Tracks mit Noten
            note_count = len([n for n in track_data.notes if n.velocity > 0])
            if note_count == 0:
                continue
            
            # Analysiere Track
            track_analysis = self._analyze_track(track_data)
            tracks.append(track_analysis)
            total_notes += note_count
        
        return AnalysisResult(
            filename=midi_data.filename,
            length_seconds=midi_data.length_seconds,
            ticks_per_beat=midi_data.ticks_per_beat,
            midi_type=midi_data.midi_type,
            tracks=tracks,
            total_notes=total_notes,
            total_tracks=len(tracks)
        )
    
    def _analyze_track(self, track_data) -> TrackAnalysis:
        """
        Interne Methode: Analysiert einen einzelnen Track
        
        Args:
            track_data: TrackData-Objekt
        
        Returns:
            TrackAnalysis
        """
        # Führe alle Analysen durch
        note_analysis = self.note_analyzer.analyze(track_data)
        dynamics_analysis = self.dynamics_analyzer.analyze(track_data)
        rhythm_analysis = self.rhythm_analyzer.analyze(track_data)
        interval_analysis = self.interval_analyzer.analyze(track_data)
        
        # Konvertiere Events zu Dicts für TrackAnalysis
        tempo_changes = [t.to_dict() for t in track_data.tempo_changes]
        time_signatures = [ts.to_dict() for ts in track_data.time_signatures]
        key_signatures = [ks.to_dict() for ks in track_data.key_signatures]
        program_changes = [pc.to_dict() for pc in track_data.program_changes]
        
        # Zähle Pedal-Events
        pedal_count = len([p for p in track_data.pedal_events if p.state == "gedrückt"])
        
        return TrackAnalysis(
            track_number=track_data.track_number,
            track_name=track_data.track_name,
            note_analysis=note_analysis,
            dynamics_analysis=dynamics_analysis,
            rhythm_analysis=rhythm_analysis,
            interval_analysis=interval_analysis,
            tempo_changes=tempo_changes,
            time_signatures=time_signatures,
            key_signatures=key_signatures,
            program_changes=program_changes,
            pedal_count=pedal_count
        )


# Convenience-Funktionen für direkten Import
def analyze_midi_file(filepath: str) -> AnalysisResult:
    """
    Convenience-Funktion: Analysiert eine MIDI-Datei
    
    Args:
        filepath: Pfad zur MIDI-Datei
    
    Returns:
        AnalysisResult
    """
    analyzer = MidiAnalyzer()
    return analyzer.analyze_file(filepath)


def compare_midi_files(file1: str, file2: str) -> ComparisonResult:
    """
    Convenience-Funktion: Vergleicht zwei MIDI-Dateien
    
    Args:
        file1: Erste Datei (Referenz)
        file2: Zweite Datei (Vergleich)
    
    Returns:
        ComparisonResult
    """
    analyzer = MidiAnalyzer()
    return analyzer.compare_files(file1, file2)
