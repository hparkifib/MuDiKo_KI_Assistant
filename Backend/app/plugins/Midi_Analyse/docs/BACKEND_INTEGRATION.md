# Backend Integration Guide

## Übersicht

Dieser Guide zeigt, wie Sie das `midi_analyzer` Package in Ihr Backend (Docker-Compose Umgebung) integrieren.

## Installation

### Option 1: Als Python Package (Empfohlen)

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Kopiere das midi_analyzer Package
COPY midi_analyzer/ /app/midi_analyzer/

# Installiere als Package
RUN pip install -e /app/midi_analyzer

# Installiere Backend-Dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Kopiere Backend-Code
COPY . .

CMD ["python", "main.py"]
```

### Option 2: Direkt in requirements.txt

```txt
# requirements.txt
-e ./midi_analyzer
mido>=1.3.2
```

## Docker-Compose Integration

### Projektstruktur

```
your_webapp/
├── docker-compose.yml
├── frontend/
│   └── ...
└── backend/
    ├── Dockerfile
    ├── requirements.txt
    ├── midi_analyzer/          # 👈 Kopieren Sie dieses Package hierhin
    │   ├── __init__.py
    │   ├── api.py
    │   ├── core/
    │   ├── models/
    │   ├── formatters/
    │   └── utils/
    └── app/
        ├── main.py
        └── routes/
            └── midi_routes.py
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - midi-uploads:/app/uploads
    environment:
      - PYTHONUNBUFFERED=1
      - MIDI_UPLOAD_DIR=/app/uploads

volumes:
  midi-uploads:
```

## FastAPI Integration

### Schritt 1: Route erstellen

```python
# backend/app/routes/midi_routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from midi_analyzer import MidiAnalyzer

router = APIRouter(prefix="/api/midi", tags=["MIDI"])
analyzer = MidiAnalyzer()


@router.post("/analyze")
async def analyze_midi(file: UploadFile = File(...)):
    """Analysiert eine MIDI-Datei"""
    try:
        content = await file.read()
        result = analyzer.analyze_bytes(content, file.filename)
        return result.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/compare")
async def compare_midi(
    reference: UploadFile = File(...),
    comparison: UploadFile = File(...)
):
    """Vergleicht zwei MIDI-Dateien"""
    try:
        ref_data = await reference.read()
        comp_data = await comparison.read()
        
        result = analyzer.compare_bytes(
            ref_data, comp_data,
            reference.filename, comparison.filename
        )
        
        return {
            "summary": result.get_summary(),
            "differences": result.get_differences()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Schritt 2: In Haupt-App registrieren

```python
# backend/app/main.py
from fastapi import FastAPI
from app.routes import midi_routes

app = FastAPI(title="Your App API")

# Registriere MIDI-Routes
app.include_router(midi_routes.router)

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## Flask Integration

```python
# backend/app/routes/midi_routes.py
from flask import Blueprint, request, jsonify
from midi_analyzer import MidiAnalyzer

midi_bp = Blueprint('midi', __name__, url_prefix='/api/midi')
analyzer = MidiAnalyzer()


@midi_bp.route('/analyze', methods=['POST'])
def analyze_midi():
    """Analysiert eine MIDI-Datei"""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    data = file.read()
    
    try:
        result = analyzer.analyze_bytes(data, file.filename)
        return jsonify(result.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@midi_bp.route('/compare', methods=['POST'])
def compare_midi():
    """Vergleicht zwei MIDI-Dateien"""
    ref_file = request.files['reference']
    comp_file = request.files['comparison']
    
    try:
        result = analyzer.compare_bytes(
            ref_file.read(), comp_file.read(),
            ref_file.filename, comp_file.filename
        )
        return jsonify(result.get_summary())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# In main.py
from app.routes.midi_routes import midi_bp
app.register_blueprint(midi_bp)
```

## API Response-Strukturen

### Analyse-Response

```json
{
  "file_info": {
    "filename": "song.mid",
    "length_seconds": 120.5,
    "ticks_per_beat": 480,
    "midi_type": 1
  },
  "tracks": [
    {
      "track_number": 0,
      "track_name": "Piano",
      "notes": {
        "count": 150,
        "range": {
          "lowest": "C3",
          "highest": "G5",
          "span_semitones": 31
        }
      },
      "dynamics": {
        "average_velocity": 72,
        "range": [48, 96],
        "average_dynamic": "mittellaut (mezzo-forte)",
        "distribution": {
          "p": 10,
          "mp": 25,
          "mf": 40,
          "f": 12
        }
      },
      "rhythm": {
        "most_common": "Viertel Note",
        "variety": ["Halbe Note", "Viertel Note", "Achtel Note"]
      },
      "intervals": {
        "max_leap": 12,
        "movement": "Die Melodie enthält einige größere Sprünge"
      }
    }
  ],
  "statistics": {
    "total_notes": 150,
    "total_tracks": 1
  }
}
```

### Vergleichs-Response

```json
{
  "reference": { /* ... Analyse wie oben ... */ },
  "comparison": { /* ... Analyse wie oben ... */ },
  "differences": [
    {
      "track": 0,
      "position": {
        "bar": 3,
        "beat": 2
      },
      "type": "note_difference",
      "expected": "D3 (Viertel Note)",
      "actual": "E3 (Viertel Note)",
      "message": "In Takt 3, Schlag 2: Unterschied in Noten",
      "severity": "medium"
    }
  ],
  "summary": {
    "total_differences": 5,
    "error_types": {
      "note_errors": 3,
      "rhythm_errors": 2,
      "dynamics_errors": 0
    },
    "similarity_score": 0.950,
    "differences": {
      "length_seconds": 2.5,
      "note_count": 3
    }
  }
}
```

### Kompakte Zusammenfassung

```python
# Endpoint für UI-Anzeige
@router.post("/compare/summary")
async def get_summary(ref: UploadFile, comp: UploadFile):
    result = analyzer.compare_bytes(...)
    return result.get_summary()
```

Response:
```json
{
  "file1": {
    "filename": "reference.mid",
    "duration": 120.5,
    "tracks": 2,
    "notes": 150
  },
  "file2": {
    "filename": "performance.mid",
    "duration": 118.0,
    "tracks": 2,
    "notes": 147
  },
  "total_differences": 5,
  "similarity_score": 0.950
}
```

## Fehlerbehandlung

```python
from midi_analyzer import MidiAnalyzer

analyzer = MidiAnalyzer()

try:
    result = analyzer.analyze_bytes(data, filename)
    return result.to_dict()
except ValueError as e:
    # Ungültige MIDI-Datei
    return {"error": f"Invalid MIDI file: {str(e)}"}, 400
except FileNotFoundError as e:
    # Datei nicht gefunden (bei analyze_file)
    return {"error": f"File not found: {str(e)}"}, 404
except Exception as e:
    # Unerwarteter Fehler
    return {"error": f"Internal error: {str(e)}"}, 500
```

## Performance-Tipps

### 1. Analyzer-Instanz wiederverwenden

```python
# ✓ Gut - Einmal instanziieren
analyzer = MidiAnalyzer()

@app.post("/analyze")
async def analyze(file: UploadFile):
    return analyzer.analyze_bytes(await file.read())
```

### 2. File-Size-Limits

```python
# FastAPI
@app.post("/analyze")
async def analyze(file: UploadFile = File(..., max_length=10_000_000)):  # 10 MB
    ...

# Flask
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB
```

### 3. Timeouts für große Dateien

```python
import asyncio

@app.post("/analyze")
async def analyze(file: UploadFile):
    try:
        result = await asyncio.wait_for(
            analyze_task(file),
            timeout=30.0  # 30 Sekunden
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Analysis timeout")
```

## Testing

```python
# test_midi_analyzer.py
from midi_analyzer import MidiAnalyzer

def test_analyze():
    analyzer = MidiAnalyzer()
    
    with open("test.mid", "rb") as f:
        data = f.read()
    
    result = analyzer.analyze_bytes(data)
    
    assert result.total_notes > 0
    assert result.total_tracks > 0
    assert result.filename == "test.mid"
```

## Vollständiges Beispiel

Siehe: `examples/midi_analyzer_fastapi.py` oder `examples/midi_analyzer_flask.py`

## Troubleshooting

### Problem: Import-Fehler

```python
# Fehler: ModuleNotFoundError: No module named 'midi_analyzer'

# Lösung: Package installieren
pip install -e ./midi_analyzer

# Oder in Dockerfile
RUN pip install -e /app/midi_analyzer
```

### Problem: MIDI-Parse-Fehler

```python
# ValueError: Ungültige MIDI-Daten

# Lösung: File-Validierung
if not file.filename.endswith(('.mid', '.midi')):
    raise HTTPException(400, "Not a MIDI file")
```

## Nächste Schritte

1. Kopieren Sie `midi_analyzer/` in Ihr Backend-Verzeichnis
2. Fügen Sie die Package-Installation zum Dockerfile hinzu
3. Erstellen Sie MIDI-Routes wie in den Beispielen
4. Testen Sie mit Postman oder curl
5. Entwickeln Sie Ihr Frontend

## Support

Bei Fragen zur Integration, siehe auch:
- `examples/` - Vollständige Beispiele
- `apps/` - Standalone-Anwendungen als Referenz
