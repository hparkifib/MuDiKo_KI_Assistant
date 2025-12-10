# Migration Guide - v1 zu v2

## Was hat sich geändert?

Version 2.0 ist ein **vollständiges Refactoring** des ursprünglichen MIDI-Analyse-Tools mit Fokus auf **Backend-Integration** und **modulare Architektur**.

## Hauptänderungen

### ✅ Neue Package-Struktur

**Vorher (v1):**
```
midi_compare.py          # Monolithisches Script (~850 Zeilen)
midi_compare_gui.py      # GUI-Wrapper
run_compare.py           # Ausführungs-Script
```

**Jetzt (v2):**
```
midi_analyzer/           # Modulares Package
  ├── api.py            # Hauptklasse
  ├── core/             # Analyzer-Klassen
  ├── models/           # Datenmodelle
  ├── formatters/       # Output-Formatter
  └── utils/            # Hilfsfunktionen

apps/                    # Lokale Tools
  ├── midi_cli.py
  └── midi_gui.py

examples/                # Integration-Beispiele
docs/                    # Dokumentation
```

### ✅ Objektorientierte API

**Vorher:**
```python
from midi_compare import compare_midi_files

compare_midi_files("file1.mid", "file2.mid", "output.txt")
```

**Jetzt:**
```python
from midi_analyzer import MidiAnalyzer

analyzer = MidiAnalyzer()

# Für API: Bytes-Support
result = analyzer.analyze_bytes(file_data, "song.mid")
json_output = result.to_dict()

# Für lokale Nutzung: Weiterhin Files
result = analyzer.compare_files("file1.mid", "file2.mid")
```

### ✅ Multiple Output-Formate

**Vorher:** Nur Text-Dateien

**Jetzt:**
```python
result = analyzer.analyze_file("song.mid")

# JSON (für APIs)
json_str = result.to_json()
dict_data = result.to_dict()

# Text (für LLM)
from midi_analyzer import TextFormatter
formatter = TextFormatter()
text = formatter.format_analysis(result)
```

### ✅ Backend-Optimiert

**Neu:**
- Bytes-Support für File-Uploads
- Strukturierte Datenmodelle mit `to_dict()`
- JSON-Formatter für API-Responses
- Thread-safe Implementierung
- Keine globalen Variablen

## Migration-Schritte

### Wenn Sie das Tool lokal nutzen (CLI/GUI)

**Keine Migration nötig!** Die Apps funktionieren wie vorher:

```bash
# GUI starten (wie vorher)
python apps/midi_gui.py

# CLI verwenden (neuer Befehl)
python apps/midi_cli.py compare file1.mid file2.mid -o output.txt
```

### Wenn Sie die Python-Funktionen nutzen

**Alt:**
```python
from midi_compare import compare_midi_files
compare_midi_files("a.mid", "b.mid", "out.txt")
```

**Neu:**
```python
from midi_analyzer import MidiAnalyzer, TextFormatter

analyzer = MidiAnalyzer()
result = analyzer.compare_files("a.mid", "b.mid")

# Text-Output wie vorher
formatter = TextFormatter()
text = formatter.format_comparison(result)

with open("out.txt", "w", encoding="utf-8") as f:
    f.write(text)
```

### Für Backend-Integration (neu!)

```python
from fastapi import FastAPI, UploadFile, File
from midi_analyzer import MidiAnalyzer

app = FastAPI()
analyzer = MidiAnalyzer()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    data = await file.read()
    result = analyzer.analyze_bytes(data, file.filename)
    return result.to_dict()  # JSON-ready!
```

## Gelöschte/Verschobene Dateien

### Können gelöscht werden (obsolet):

- `test_files.py` - Nur für Debugging
- `test_midi.py` - Nur für Debugging
- `check_tracks.py` - Nur für Debugging
- `run_compare.py` - Ersetzt durch `apps/midi_cli.py`
- `example_usage.py` - Ersetzt durch `examples/midi_analyzer_basic.py`
- Alle `vergleich_*.txt` - Output-Beispiele

### Verschoben:

- `midi_compare.py` → `midi_analyzer/` (aufgeteilt in Module)
- `midi_compare_gui.py` → `apps/midi_gui.py`

### MIDI-Dateien

Verschieben Sie Ihre Test-MIDI-Dateien nach `test_data/`:

```bash
# PowerShell
mkdir test_data
mv *.mid test_data/
```

## Feature-Parität

Alle Features aus v1 sind in v2 enthalten:

- ✅ Noten-Analyse
- ✅ Rhythmus-Analyse (Notenlängen)
- ✅ Dynamik-Analyse (Velocity)
- ✅ Intervall-Analyse
- ✅ Tempo, Taktart, Tonart
- ✅ Pedal-Events
- ✅ Takt.Schlag-Format
- ✅ Detaillierter Vergleich
- ✅ LLM-freundlicher Text-Output
- ✅ GUI-Interface
- ✅ CLI-Interface

**Neu in v2:**
- ✅ JSON-Output für APIs
- ✅ Bytes-Support für Uploads
- ✅ Modulare Architektur
- ✅ Backend-Integration
- ✅ Docker-Ready
- ✅ Type Hints
- ✅ Dataclasses

## Vorteile von v2

1. **Backend-Ready**: Direkt in FastAPI/Flask integrierbar
2. **Modularer**: Klare Trennung der Verantwortlichkeiten
3. **Testbarer**: Jede Komponente einzeln testbar
4. **Erweiterbar**: Neue Analyzer einfach hinzufügen
5. **Type-Safe**: Type Hints für bessere IDE-Unterstützung
6. **Dokumentiert**: Umfangreiche Docs und Beispiele

## Rückwärtskompatibilität

Die **alte API** wird **nicht** unterstützt. Das ist eine **Breaking Change**.

**Grund:** Vollständiges Refactoring für bessere Architektur.

**Aber:** Migration ist einfach (siehe oben), und alle Features sind verfügbar.

## Support

Bei Fragen:
1. Siehe `docs/BACKEND_INTEGRATION.md`
2. Siehe `examples/` für Code-Beispiele
3. Teste mit `test_analyzer.py` und `test_comparison.py`

## Zeitplan

- **v1**: Alt (funktioniert lokal)
- **v2**: Neu (funktioniert lokal + Backend)
- **Migration**: Optional, aber empfohlen für neue Projekte
