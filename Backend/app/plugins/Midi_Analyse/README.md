# MIDI Analyzer

**Version 2.0** - Modulares Backend-Package für MIDI-Analyse und -Vergleich

Professionelles Python-Package für die Analyse und den Vergleich von MIDI-Dateien, optimiert für **Backend-Integration** in Web-Anwendungen.

## 🎯 Features

- **📊 Umfassende MIDI-Analyse**: Noten, Rhythmus, Dynamik, Intervalle, Tempo, Taktart
- **🔄 Intelligenter Vergleich**: Findet Unterschiede zwischen zwei MIDI-Dateien
- **🐳 Backend-Ready**: Optimiert für Docker, FastAPI, Flask
- **📦 Modulare Architektur**: Objektorientiert, gut gekapselt, einfach zu integrieren
- **� Bytes-Support**: Direkte Verarbeitung von File-Uploads
- **📤 Multiple Formate**: JSON (API), Text (LLM), Dict (Python)
- **🖥️ Optional: GUI & CLI**: Für lokale Nutzung

## 🏗️ Projekt-Struktur

```
midi_analyzer/              # 👈 Backend-Package (für Integration)
├── __init__.py            # Public API
├── api.py                 # MidiAnalyzer Hauptklasse
├── core/                  # Kernlogik
│   ├── midi_parser.py
│   ├── note_analyzer.py
│   ├── rhythm_analyzer.py
│   ├── dynamics_analyzer.py
│   ├── interval_analyzer.py
│   └── comparison_engine.py
├── models/                # Datenmodelle
│   ├── midi_data.py
│   ├── analysis_result.py
│   └── comparison_result.py
├── formatters/            # Output-Formatter
│   ├── json_formatter.py
│   └── text_formatter.py
└── utils/                 # Hilfsfunktionen

apps/                      # 👈 Lokale Anwendungen (optional)
├── midi_cli.py            # Kommandozeile
└── midi_gui.py            # Grafische Oberfläche

examples/                  # 👈 Integration-Beispiele
├── midi_analyzer_fastapi.py
├── midi_analyzer_flask.py
└── midi_analyzer_basic.py

docs/                      # 👈 Dokumentation
└── BACKEND_INTEGRATION.md
```

## 🚀 Quick Start

### Für Backend-Integration

```python
from midi_analyzer import MidiAnalyzer

# Erstelle Analyzer
analyzer = MidiAnalyzer()

# Analysiere Datei
result = analyzer.analyze_file("song.mid")
print(f"Gefunden: {result.total_notes} Noten")

# Oder: Analysiere Bytes (für Uploads)
with open("song.mid", "rb") as f:
    result = analyzer.analyze_bytes(f.read(), "song.mid")

# Export als JSON (für API)
json_output = result.to_json()

# Export als Dict
data = result.to_dict()

# Vergleiche zwei Dateien
comparison = analyzer.compare_files("ref.mid", "perf.mid")
differences = comparison.get_differences()
print(f"Unterschiede: {comparison.summary.total_differences}")
```

### Für lokale Nutzung

```bash
# GUI starten
python apps/midi_gui.py

# CLI verwenden
python apps/midi_cli.py compare ref.mid perf.mid -o output.txt
```

## 🐳 Backend-Integration (Docker-Compose)

### Schritt 1: Package kopieren

```bash
# Kopieren Sie midi_analyzer/ in Ihr Backend-Verzeichnis
cp -r midi_analyzer/ your_webapp/backend/
```

### Schritt 2: Dockerfile anpassen

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# MIDI Analyzer installieren
COPY midi_analyzer/ /app/midi_analyzer/
RUN pip install -e /app/midi_analyzer

# Ihre Dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Schritt 3: FastAPI Route erstellen

```python
# backend/app/routes/midi_routes.py
from fastapi import APIRouter, UploadFile, File
from midi_analyzer import MidiAnalyzer

router = APIRouter(prefix="/api/midi")
analyzer = MidiAnalyzer()

@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    result = analyzer.analyze_bytes(content, file.filename)
    return result.to_dict()

@router.post("/compare")
async def compare(
    reference: UploadFile = File(...),
    comparison: UploadFile = File(...)
):
    ref_data = await reference.read()
    comp_data = await comparison.read()
    result = analyzer.compare_bytes(ref_data, comp_data)
    return result.get_summary()
```

**Vollständige Anleitung:** Siehe [`docs/BACKEND_INTEGRATION.md`](docs/BACKEND_INTEGRATION.md)

**Beispiele:** Siehe `examples/midi_analyzer_fastapi.py` und `examples/midi_analyzer_flask.py`

## 📦 Installation

### Für Backend-Integration

```bash
# In Ihrem Backend-Verzeichnis
pip install -e ./midi_analyzer
```

### Für lokale Entwicklung

```bash
# Requirements installieren
pip install -r requirements.txt

# Package im Development-Mode installieren
pip install -e .
```

### Dependencies

- **Core**: `mido >= 1.3.2` (MIDI-Parsing)
- **Optional**: `fastapi`, `flask` (für API-Beispiele)
- **Optional**: `tkinter` (für GUI, meist vorinstalliert)

## 📖 Dokumentation

- **[Backend Integration Guide](docs/BACKEND_INTEGRATION.md)** - Vollständige Anleitung für Docker/Web-App
- **[Beispiele](examples/)** - FastAPI, Flask, Basis-Verwendung
- **[API-Referenz](midi_analyzer/)** - Docstrings in allen Modulen

## 🧪 Tests

```bash
# Quick Test
python test_analyzer.py
python test_comparison.py

# CLI testen
python apps/midi_cli.py analyze Amazing_Grace.mid -o test_output.txt

# GUI testen
python apps/midi_gui.py
```

## 📊 API Response-Beispiele

### Analyse-Response (JSON)

```json
{
  "file_info": {
    "filename": "song.mid",
    "length_seconds": 120.5,
    "ticks_per_beat": 480
  },
  "tracks": [{
    "track_name": "Piano",
    "notes": {
      "count": 150,
      "range": {"lowest": "C3", "highest": "G5"}
    },
    "dynamics": {
      "average_velocity": 72,
      "average_dynamic": "mittellaut (mezzo-forte)"
    },
    "rhythm": {
      "most_common": "Viertel Note"
    }
  }],
  "statistics": {
    "total_notes": 150,
    "total_tracks": 1
  }
}
```

### Vergleichs-Response (JSON)

```json
{
  "summary": {
    "total_differences": 5,
    "similarity_score": 0.950
  },
  "differences": [
    {
      "track": 0,
      "position": {"bar": 3, "beat": 2},
      "type": "note_difference",
      "expected": "D3 (Viertel Note)",
      "actual": "E3 (Viertel Note)",
      "message": "In Takt 3, Schlag 2: Unterschied in Noten"
    }
  ]
}
```
