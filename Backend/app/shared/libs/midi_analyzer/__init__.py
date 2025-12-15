"""
MIDI Analyzer - Backend-Package für MIDI-Analyse und -Vergleich

Dieses Package bietet eine vollständige MIDI-Analyse-Lösung für Backend-Integration.

Hauptklassen:
    MidiAnalyzer: Zentrale Klasse für alle Operationen

Beispiel:
    from midi_analyzer import MidiAnalyzer
    
    analyzer = MidiAnalyzer()
    
    # Datei analysieren
    result = analyzer.analyze_file("song.mid")
    json_data = result.to_dict()
    
    # Bytes analysieren (für Uploads)
    result = analyzer.analyze_bytes(file_data, "upload.mid")
    
    # Dateien vergleichen
    comparison = analyzer.compare_files("ref.mid", "perf.mid")
    differences = comparison.get_differences()

Version: 2.0.0
"""

__version__ = "2.0.0"

# Public API
from .api import MidiAnalyzer, analyze_midi_file, compare_midi_files
from .models import AnalysisResult, ComparisonResult

# Für erweiterte Nutzung
from .formatters import TextFormatter, JSONFormatter

__all__ = [
    # Hauptklasse
    'MidiAnalyzer',
    # Convenience Functions
    'analyze_midi_file',
    'compare_midi_files',
    # Results
    'AnalysisResult',
    'ComparisonResult',
    # Formatter
    'TextFormatter',
    'JSONFormatter',
    # Version
    '__version__',
]
