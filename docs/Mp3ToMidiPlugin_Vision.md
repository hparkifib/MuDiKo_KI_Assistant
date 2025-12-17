# 🎼 MP3-to-MIDI Converter Plugin - Vision & Lastenheft

**Version:** 1.3  
**Datum:** 17. Dezember 2025  
**Status:** Phase 1 abgeschlossen, Fokus auf Konversion  
**Branch:** `Experimental_MP3_to_Midi_Conversion`

---

## 🎯 MIDI-Konvertierung optimieren

### Motivation
Die Qualität der MP3-zu-MIDI-Konvertierung ist entscheidend für die Weiterverwendung in anderen Tools. Basic Pitch liefert zwar State-of-the-Art-Ergebnisse, aber verschiedene Musikinstrumente und Aufnahmequalitäten erfordern unterschiedliche Parameter-Einstellungen. **Ziel ist es, dem Nutzer (Lehrkraft/Schüler) qualitativ hochwertige MIDI-Dateien zu liefern**, die dann mit dem MIDI-Comparison-Plugin analysiert werden können. Der Fokus liegt auf **optimaler Konversion**, nicht auf integrierter Analyse.

---

### 🎨 Strategie 1: Instrument-spezifische Presets (v1.2)

Wir stellen **7 vordefinierte Presets** bereit. Drums wurden entfernt (Pitch-Transkription ungeeignet). Presets liegen als separate JSON-Dateien vor und enthalten nur die genutzten Felder.

Unterstützte Presets (IDs / Dateien):
- `piano.json` — Piano/Keyboard (polyphonic)
- `vocals.json` — Singing voice (monophonic)
- `woodwinds.json` — Flute, Clarinet, Oboe, Bassoon (monophonic)
- `brass.json` — Trumpet, Trombone, French Horn, Tuba (monophonic)
- `strings.json` — Violin, Viola, Cello, Double Bass (mostly polyphonic)
- `guitar.json` — Acoustic/Electric Guitar (polyphonic)
- `ensemble.json` — Mixed instruments (polyphonic)

JSON Schema (pro Preset):
```json
{
  "id": "<preset-id>",
  "name": "<display name>",
  "description": "<short description>",
  "instruments": ["<Instrument A>", "<Instrument B>"]
  ,"parameters": {
    "onset_threshold": 0.0-1.0,
    "frame_threshold": 0.0-1.0,
    "minimum_note_length": <frames>,
    "minimum_frequency": <Hz>,
    "maximum_frequency": <Hz>,
    "melodia_trick": true|false
  }
}
```

Wichtige Hinweise:
- `minimum_note_length` ist in Frames (nicht in Notenwerten). Realistische Startwerte: 8–20.
- Preprocessing-Flags wurden entfernt; Pipeline bleibt als Phase 2 geplant.
- Legacy Aliases werden unterstützt (z. B. `klavier` → `piano`); `schlagzeug` ist entfernt und führt zu einem klaren Fehler.

Empfohlene Default-Parameter (implementiert):
- `piano`: min_note_len 8, 27.5–4186 Hz, polyphon
- `guitar`: min_note_len 8, 82–1319 Hz, polyphon
- `ensemble`: min_note_len 8, 27.5–4186 Hz, polyphon
- `vocals`: min_note_len 15, 80–1200 Hz, monophon (`melodia_trick: true`)
- `woodwinds`: min_note_len 15, 41–3136 Hz, monophon (`melodia_trick: true`)
- `brass`: min_note_len 15, 55–1400 Hz, monophon (`melodia_trick: true`)
- `strings`: min_note_len 12, 41–3520 Hz, polyphon

Frontend-Contract (Preset-Liste):
- Backend liefert je Preset: `id`, `name`, `description`, `instruments`.
- UI zeigt nur Instrument-Name, Beschreibung, Instrumentliste.

---

### 🎮 Strategie 2: Preprocessing-Pipeline (Phase 2)

#### Audio-Normalisierung
```python
def normalize_audio(audio_path: Path) -> np.ndarray:
    """Dynamik-Normalisierung für konsistente Lautstärke"""
    y, sr = librosa.load(audio_path, sr=22050)
    y_normalized = librosa.util.normalize(y)  # Peak-Normalisierung auf ±1.0
    return y_normalized, sr
```

#### Noise Reduction (Optional)
```python
def reduce_noise(audio: np.ndarray, sr: int) -> np.ndarray:
    """Hintergrundgeräusche filtern (z.B. Raumhall, Ventilator)"""
    import noisereduce as nr
    reduced = nr.reduce_noise(y=audio, sr=sr, prop_decrease=0.8)
    return reduced
```

#### Instrument-spezifische Filter
- **Atemgeräusche** (Holzbläser): High-Pass-Filter >130 Hz
- **Bogengeräusche** (Streicher): Notch-Filter bei hohen Frequenzen
- **Plektrum-Noise** (Gitarre): Transient-Suppression

---

### 🎛️ Strategie 3: Parameter-Tuning (Advanced)

#### Für Power-User: Erweiterte Einstellungen
Nach Preset-Auswahl optional einblendbar:

**Onset Threshold** (0.0 - 1.0)
- *Niedrig (0.2)*: Erkennt auch leise Noten-Einsätze → Mehr Noten, aber mehr False Positives
- *Mittel (0.5)*: Standard → Balance
- *Hoch (0.7)*: Nur deutliche Anschläge → Weniger Noten, präziser

**Frame Threshold** (0.0 - 1.0)
- *Niedrig (0.2)*: Toleriert kurze Noten → Gut für Staccato
- *Mittel (0.3)*: Standard
- *Hoch (0.5)*: Nur lange, stabile Töne → Filtert Vibrato/Glissandi

**Minimum Note Length** (Frames)
- 8–12: Polyphone Instrumente (Piano/Gitarre/Ensemble)
- 12–20: Sustained/monophone Linien (Vocals/Winds/Strings)

**Frequency Range** (Hz)
- Instrument-spezifisch begrenzen → Filtert Störgeräusche außerhalb des Tonumfangs

---

### 🧪 Strategie 4: Post-Processing

#### Quantisierung
```python
def quantize_midi(midi_path: Path, grid: str = '16th') -> Path:
    """Zeitlich auf Taktraster ausrichten"""
    midi = mido.MidiFile(midi_path)
    quantized = quantize_notes_to_grid(midi, grid='16th')  # 1/16-Noten-Raster
    return quantized
```

#### MIDI-Cleanup
- **Redundante Noten entfernen**: Gleiche Tonhöhe < 50ms Abstand
- **Velocity-Glättung**: Dynamik-Sprünge reduzieren
- **Sustain-Pedal-Korrektur**: Note-Off-Events anpassen

---

### 📊 Strategie 5: Qualitäts-Feedback

#### Confidence-Score-Analyse
```python
def analyze_confidence(confidence_scores: np.ndarray) -> dict:
    """Gibt Qualitäts-Indikatoren zurück"""
    return {
        'avg_confidence': np.mean(confidence_scores),
        'min_confidence': np.min(confidence_scores),
        'low_confidence_ratio': np.sum(confidence_scores < 0.7) / len(confidence_scores),
        'quality_rating': '⭐⭐⭐⭐⭐' if avg > 0.9 else '⭐⭐⭐'
    }
```

#### Benutzer-Hinweise im Report
```markdown
**Aufnahme-Qualität:** ⚠️ Niedrige Confidence (68%)
**Empfehlung:**
- Ruhigere Umgebung wählen (Hintergrundgeräusche erkannt)
- Mikrofon näher am Instrument platzieren
- Alternative: Preset 'Gesang' mit erhöhtem Frame Threshold versuchen
```

---

### 🚀 Implementierungs-Roadmap

### ✅ Phase 1: Preset-System (PRIORITÄT)
- [x] 7 Presets als JSON (englische IDs)
- [x] Frontend: `Mp3ToMidiPresetSelectionPage.jsx` nutzt nur benötigte Felder
- [x] Backend: Preset-Parameter in Konverter integriert; Legacy Aliases
- [x] Workflow: Upload → PresetSelection → Conversion → Result

#### ⏳ Phase 2: Preprocessing
- [ ] Audio-Normalisierung (librosa)
- [ ] Noise Reduction (noisereduce Library)
- [ ] Instrument-spezifische Filter
- [ ] Toggle in Frontend: "Audio-Vorverarbeitung aktivieren"

#### ⏳ Phase 3: Post-Processing
- [ ] MIDI-Quantisierung
- [ ] Note-Cleanup-Algorithmen
- [ ] Optional: Nutzerwahl "Quantisierung: Aus / 8th / 16th / 32nd"

#### ⏳ Phase 4: Advanced Settings
- [ ] Slider für Onset/Frame Threshold
- [ ] Frequency Range Picker
- [ ] "Erweiterte Einstellungen" Collapsible Panel
- [ ] Preset als Ausgangspunkt für manuelle Anpassung

#### ⏳ Phase 5: KI-Optimierung (Zukunft)
- [ ] Automatische Instrument-Erkennung (ML-Klassifikator)
- [ ] Adaptive Parameter-Anpassung basierend auf Audio-Features
- [ ] Feedback-Loop: Nutzer-Korrekturen → Parameter-Lernen

---

### 📚 Technische Referenzen

**Basic Pitch Parameter-Dokumentation:**
- [GitHub: basic-pitch/inference.py](https://github.com/spotify/basic-pitch/blob/main/basic_pitch/inference.py)
- Parameter: `onset_threshold`, `frame_threshold`, `minimum_note_length`, `minimum_frequency`, `maximum_frequency`, `melodia_trick`

**Audio-Preprocessing-Libraries:**
- `librosa.util.normalize()` - Peak-Normalisierung
- `noisereduce` - Spektrale Noise Reduction
- `scipy.signal` - Filter-Design (High-Pass, Notch)

**MIDI-Quantisierung:**
- `mido.tick2second()` / `mido.second2tick()` - Zeitumrechnung
- Custom-Algorithmus: Nächste Grid-Position finden

---

## 📋 Inhaltsverzeichnis

1. [Vision & Motivation](#vision--motivation)
2. [Abgrenzung zu bestehenden Plugins](#abgrenzung-zu-bestehenden-plugins)
3. [Funktionale Anforderungen](#funktionale-anforderungen)
4. [Technische Architektur](#technische-architektur)
5. [Datenfluss & Pipeline](#datenfluss--pipeline)
6. [Output-Struktur](#output-struktur)
7. [Entwicklungs-Phasen](#entwicklungs-phasen)
8. [Technische Entscheidungen](#technische-entscheidungen)
9. [Erfolgs-Kriterien](#erfolgs-kriterien)

---

## 🎯 Vision & Motivation

### Das Problem
Aktuelle Plugins im MuDiKo-System:
- **Audio-Feedback**: Analysiert MP3/WAV-Aufnahmen, aber nur auf Audio-Feature-Ebene (Spektralanalyse, RMS, MFCC)
- **MIDI-Comparison**: Vergleicht MIDI-Dateien taktbasiert, erfordert aber bereits existierende MIDI-Dateien

**Limitation**: Wenn Schüler nur MP3-Aufnahmen liefern können (z.B. Smartphone-Recordings), fehlt die Möglichkeit, diese in MIDI zu konvertieren für die präzise Note-by-Note-Analyse.

### Die Lösung
Ein **spezialisiertes Konvertierungs-Plugin**:
1. Nimmt MP3-Aufnahmen entgegen
2. Konvertiert sie via **Spotify's Basic Pitch** in hochwertige MIDI-Dateien
3. Optimiert Parameter durch **instrument-spezifische Presets**
4. Liefert **qualitativ beste MIDI-Files** für weitere Analyse im MIDI-Comparison-Plugin

### Der Mehrwert
- ✅ **Spezialisiert**: Fokus auf optimale Konversion, nicht auf Analyse
- ✅ **Modular**: MIDI-Dateien können in MIDI-Comparison-Plugin weiterverwendet werden
- ✅ **Zugänglich**: Funktioniert mit Smartphone-Aufnahmen, keine MIDI-Hardware nötig
- ✅ **Instrument-optimiert**: Presets liefern bessere Ergebnisse als Generic-Einstellungen
- ✅ **Klare Trennung**: Konversion (dieses Plugin) vs. Analyse (MIDI-Comparison)

---

## 🔄 Abgrenzung zu bestehenden Plugins

| Feature | Audio-Feedback | MIDI-Comparison | **MP3-to-MIDI Converter (NEU)** |
|---------|---------------|-----------------|--------------------------------|
| **Input-Format** | MP3/WAV/MP4 | MIDI-Dateien | MP3/WAV/MP4 |
| **Output-Format** | Analyse-Report | Analyse-Report | **MIDI-Dateien** |
| **Hauptfunktion** | Audio-Feature-Analyse | MIDI-Vergleich & Analyse | **MP3 → MIDI Konversion** |
| **Analyse-Typ** | Spektral, Tempo, Pitch | Noten, Rhythmus, Dynamik | **Keine (nur Konversion)** |
| **Weiterverwendung** | LLM-Feedback | LLM-Feedback | **→ MIDI-Comparison-Plugin** |
| **Nutzt Basic Pitch** | ❌ | ❌ | ✅ |
| **Nutzt MIDI-Analyzer** | ❌ | ✅ | ❌ |
| **Preset-System** | ❌ | ❌ | ✅ |

### Wiederverwendeter Code
- ✅ `SessionService`, `StorageService` (shared)
- ✅ Plugin-Interface (`MusicToolPlugin`)

### Neuer Code
- 🆕 `Mp3ToMidiConverter` - Basic Pitch Integration
- 🆕 `Mp3ToMidiConverterService` - Orchestrierung der Konversion
- 🆕 `PresetManager` - Preset-Verwaltung
- 🆕 Frontend-Pages für Upload & Preset-Auswahl
- 🆕 7 Instrument-Presets (JSON)

---

## ✅ Funktionale Anforderungen

### Must-Have (Phase 1-3)

#### FR-1: MP3-Upload
- **Beschreibung**: Nutzer lädt MP3/WAV-Aufnahme hoch
- **Input**: 1 MP3/WAV/MP4-Datei (max. 100 MB)
- **Output**: Session-ID, Bestätigung der gespeicherten Datei
- **Validierung**: Unterstützte Formate, Dateigröße

#### FR-2: Preset-Auswahl
- **Beschreibung**: Nutzer wählt Preset basierend auf Instrument
- **Input**: Preset-ID (piano, guitar, vocals, woodwinds, brass, strings, ensemble)
- **Output**: Bestätigung der Auswahl
- **Anzeige**: Icon, Name (Deutsch), Beschreibung, Instrument-Liste

#### FR-3: Basic Pitch MIDI-Konversion
- **Beschreibung**: MP3 wird mit Preset-Parametern in MIDI konvertiert
- **Engine**: Spotify Basic Pitch (Python Library)
- **Parameter**: onset_threshold, frame_threshold, minimum_note_length, frequency_range, melodia_trick (aus Preset)
- **Output**: 
  - MIDI-Datei (downloadbar)
  - Confidence-Scores pro Note (für Qualitätsbewertung)
  - Metadaten: Anzahl Noten, Durchschnittliche Confidence, Dauer
- **Fehlerbehandlung**: Falls keine Noten erkannt → Warnung + leere MIDI

#### FR-4: MIDI-Export mit Metadaten
- **Beschreibung**: Konvertierte MIDI-Datei kann heruntergeladen werden
- **Format**: Standard MIDI File (.mid)
- **Zusatz-Info**: JSON mit Confidence-Scores, verwendetem Preset, Konversions-Timestamp
- **Weiterverwendung**: MIDI kann im MIDI-Comparison-Plugin genutzt werden

### Should-Have (Phase 4+)
- Audio-Preprocessing: Normalisierung, Noise Reduction
- MIDI-Post-Processing: Quantisierung, Note Cleanup
- Erweiterte Einstellungen: Manuelle Parameter-Anpassung basierend auf Preset
- Confidence-basierte Warnungen: "Niedrige Qualität, bitte neu aufnehmen"

### Won't-Have (Out of Scope)
- ❌ Echtzeit-Konversion (Basic Pitch braucht ~10-30s pro Minute Audio)
- ❌ Integrierte MIDI-Analyse (→ MIDI-Comparison-Plugin)
- ❌ Taktbasierte Segmentierung (→ MIDI-Comparison-Plugin)
- ❌ Feedback-Report-Generierung (→ MIDI-Comparison-Plugin)
- ❌ Automatische Tempo-Korrektur
- ❌ Polyphonie-Separation (Basic Pitch macht das bereits)

---

## 🏗️ Technische Architektur

### System-Komponenten

```
┌─────────────────────────────────────────────────────────────┐
│                 MP3-to-MIDI Converter Plugin                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐         ┌──────────────────┐          │
│  │ Upload Handler  │────────►│ Storage Service  │          │
│  └─────────────────┘         └──────────────────┘          │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────┐           │
│  │      Mp3ToMidiConverterService              │           │
│  │  (Orchestriert Konversion)                  │           │
│  └─────────────────────────────────────────────┘           │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────┐           │
│  │      PresetManager                          │           │
│  │  (Lädt Preset-Parameter)                    │           │
│  └─────────────────────────────────────────────┘           │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────┐           │
│  │      Mp3ToMidiConverter                     │           │
│  │  (Basic Pitch Integration)                  │           │
│  └─────────────────────────────────────────────┘           │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────┐           │
│  │  MIDI File + Confidence Scores              │           │
│  │  (Output für Download/Weiterverwendung)     │           │
│  └─────────────────────────────────────────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ MIDI-Comparison Plugin│
                  │ (für Analyse)         │
                  └───────────────────────┘
```

### Modul-Struktur

```
Backend/app/plugins/mp3_to_midi_feedback/
├── __init__.py
├── config.yaml                          # Plugin-Konfiguration
├── mp3_to_midi_feedback_plugin.py       # Plugin-Klasse (MusicToolPlugin)
├── mp3_to_midi_feedback_routes.py       # Flask Routes
├── mp3_to_midi_feedback_service.py      # Hauptlogik (Orchestrierung)
├── mp3_to_midi_converter.py             # Basic Pitch Wrapper
└── presets/
    ├── __init__.py                      # PresetManager
    ├── piano.json
    ├── guitar.json
    ├── vocals.json
    ├── woodwinds.json
    ├── brass.json
    ├── strings.json
    └── ensemble.json
```

### Dependencies

**Neue Dependencies** (zu `requirements.txt` hinzufügen):
```txt
basic-pitch==0.3.2        # Spotify's Audio-to-MIDI
tensorflow>=2.12.0        # Required by Basic Pitch
```

**Bestehende Dependencies** (werden wiederverwendet):
```txt
flask>=2.3.0
librosa>=0.10.0
mido>=1.3.2
numpy>=1.24.0
```

---

## 🔄 Datenfluss & Pipeline

### Workflow: Upload bis MIDI-Export

```
1. USER: Upload MP3 + Preset-Auswahl
   │
   ├─► Frontend: AudioUploadPage.jsx → Mp3ToMidiPresetSelectionPage.jsx
   │      ├─► POST /api/tools/mp3-to-midi-feedback/upload
   │      │     └─► SessionService.create_session()
   │      │     └─► StorageService.save_file()
   │      │
   │      └─► GET /api/tools/mp3-to-midi-feedback/presets
   │            └─► PresetManager.get_preset_list()
   │
   ▼
2. BACKEND: MIDI Conversion mit Preset-Parametern
   │
   ├─► POST /api/tools/mp3-to-midi-feedback/convert-and-analyze
   │      └─► Mp3ToMidiConverterService.process()
   │            │
   │            ├─► PresetManager.load_preset(preset_id)
   │            │     └─► Lädt Parameter aus JSON
   │            │
   │            └─► Mp3ToMidiConverter.convert(audio.mp3, preset_params)
   │                  └─► basic_pitch.predict() mit Preset-Parametern
   │                        ├─► onset_threshold (aus Preset)
   │                        ├─► frame_threshold (aus Preset)
   │                        ├─► minimum_note_length (aus Preset)
   │                        ├─► minimum/maximum_frequency (aus Preset)
   │                        └─► melodia_trick (aus Preset)
   │
   ▼
3. OUTPUT: MIDI-Datei + Metadaten
   │
   ├─► MIDI-File (.mid)
   │     └─► Standard MIDI Format
   │     └─► Gespeichert in Session-Folder
   │
   ├─► Confidence-Scores (JSON)
   │     └─► Pro Note: Timestamp, Pitch, Confidence
   │     └─► Aggregiert: Durchschnitt, Minimum, Low-Confidence-Ratio
   │
   └─► Metadaten (JSON)
         ├─► used_preset: "piano"
         ├─► conversion_timestamp: "2025-12-17T14:30:00Z"
         ├─► audio_duration_seconds: 120.5
         ├─► note_count: 342
         └─► avg_confidence: 0.87
   │
   ▼
4. FRONTEND: Download + Weiterverwendungs-Optionen
   │
   └─► Mp3ToMidiResultPage.jsx
         ├─► Download MIDI-Datei
         ├─► Zeige Confidence-Statistiken
         ├─► Button: "In MIDI-Comparison-Plugin analysieren"
         └─► Warnung: "Niedrige Confidence (< 70%) → Neu aufnehmen?"
```

### Datenstrukturen

#### Conversion-Result
```python
{
  'session_id': 'abc123',
  'midi_file_path': Path,
  'midi_filename': 'converted.mid',
  'audio_duration_seconds': 120.5,
  'note_count': 342,
  'confidence_scores': {
    'per_note': [
      {'time': 0.0, 'pitch': 60, 'confidence': 0.92},
      {'time': 0.5, 'pitch': 62, 'confidence': 0.88},
      ...
    ],
    'statistics': {
      'avg_confidence': 0.87,
      'min_confidence': 0.52,
      'low_confidence_ratio': 0.15,  # 15% der Noten < 0.7
      'quality_rating': '⭐⭐⭐⭐☆'
    }
  },
  'metadata': {
    'used_preset': 'piano',
    'preset_parameters': {...},
    'conversion_timestamp': '2025-12-17T14:30:00Z',
    'basic_pitch_version': '0.3.2'
  }
}
```

---

## 📄 Output-Struktur

### Frontend-Anzeige (Result Page)

```markdown
# ✅ MIDI-Konversion erfolgreich

**Datei:** student_recording.mp3 → student_recording.mid
**Preset:** 🎹 Klavier
**Dauer:** 2:00 min
**Noten:** 342

## 📊 Qualitätsbewertung

**Confidence:** ⭐⭐⭐⭐☆ (87% durchschnittlich)
- Sehr gute Noten (>90%): 68%
- Gute Noten (70-90%): 17%
- Unsichere Noten (<70%): 15%

⚠️ **Hinweis:** 15% der Noten haben niedrige Confidence.
**Empfehlung:** 
- Ruhigere Umgebung wählen
- Mikrofon näher am Instrument platzieren
- Alternative: Preset mit anderen Parametern versuchen

## 💾 Download & Weiterverwendung

[📥 MIDI-Datei herunterladen]
[📊 In MIDI-Comparison-Plugin analysieren]
```

---

## 🛠️ Entwicklungs-Phasen

### ✅ Phase 1: Preset-System & Basic Conversion (ABGESCHLOSSEN)
**Ziel**: Funktionale MIDI-Konversion mit instrument-spezifischen Presets

**Abgeschlossen**:
- [x] Plugin-Struktur erstellt (`config.yaml`, `__init__.py`)
- [x] 7 Presets als JSON (piano, guitar, vocals, woodwinds, brass, strings, ensemble)
- [x] Deutsche Namen/Beschreibungen für 12-16-Jährige
- [x] Icons (🎹🎸🎤🎺🎷🎻👥) in Frontend integriert
- [x] Backend: `PresetManager` mit `get_preset_list()`, Legacy-Alias-Support
- [x] Frontend: `Mp3ToMidiPresetSelectionPage.jsx` mit Icon-Dropdown
- [x] Basic Pitch Integration mit Preset-Parametern
- [x] Routes: `/upload`, `/presets`, `/convert-and-analyze`
- [x] Workflow: Upload → Preset-Auswahl → Konversion → MIDI-Download

**Output**: Nutzer können MP3s mit optimierten Presets zu MIDI konvertieren

---

### ⏳ Phase 2: Preprocessing für bessere Konversion
**Ziel**: Verbesserte Konversionsqualität durch Audio-Aufbereitung

**Geplant**:
- [ ] Audio-Normalisierung (librosa)
- [ ] Noise Reduction (noisereduce Library)
- [ ] Instrument-spezifische Filter (High-Pass, Low-Pass)
- [ ] Toggle in Frontend: "Audio-Vorverarbeitung aktivieren"
- [ ] A/B-Vergleich: Mit/Ohne Preprocessing
- [ ] Confidence-Score-Vergleich

**Output**: Höhere Confidence-Scores, weniger False Positives

---

### ⏳ Phase 3: Post-Processing für sauberere MIDIs
**Ziel**: MIDI-Bereinigung für bessere Weiterverwendung

**Geplant**:
- [ ] MIDI-Quantisierung (zu Raster snappen)
- [ ] Note-Cleanup: Sehr kurze Noten entfernen
- [ ] Overlap-Behandlung (überlappende Noten gleicher Tonhöhe)
- [ ] Optional: Nutzerwahl "Quantisierung: Aus / 8th / 16th / 32nd"
- [ ] Velocity-Normalisierung
- [ ] Download-Optionen: "Original MIDI" vs. "Bereinigte MIDI"

**Output**: Professionell aussehende MIDI-Dateien, besser für MIDI-Comparison-Plugin geeignet

---

### ⏳ Phase 4: Erweiterte Einstellungen (Optional)
**Ziel**: Power-User können Parameter manuell anpassen

**Geplant**:
- [ ] Slider für Onset/Frame Threshold
- [ ] Frequency Range Picker (Min/Max Hz)
- [ ] Melodia Trick Toggle
- [ ] Minimum Note Length Anpassung
- [ ] "Erweiterte Einstellungen" Collapsible Panel
- [ ] Preset als Ausgangspunkt für manuelle Anpassung
- [ ] "Parameter als neues Preset speichern" (Custom Presets)

**Output**: Maximale Flexibilität für erfahrene Nutzer

---

### ⏳ Phase 5: KI-Optimierung (Zukunftsvision)
**Ziel**: Automatische Parameter-Anpassung durch Audio-Analyse

**Konzept**:
- [ ] Automatische Instrument-Erkennung (ML-Klassifikator)
- [ ] Adaptive Parameter-Anpassung basierend auf Audio-Features
- [ ] LLM-basiertes Preset-Interview (siehe Strategie 6)
- [ ] Feedback-Loop: Nutzer-Korrekturen → Parameter-Lernen
- [ ] Custom-Presets pro Nutzer/Schule
- [ ] A/B-Testing verschiedener Preset-Kombinationen

**Output**: Selbst-optimierende Konversion, keine manuelle Preset-Auswahl nötig

---

---

## 🔧 Technische Entscheidungen

### TD-1: Warum Basic Pitch?
**Entscheidung**: Spotify's Basic Pitch als Konversions-Engine

**Begründung**:
- ✅ State-of-the-Art polyphonic audio-to-MIDI
- ✅ Open Source, gut dokumentiert
- ✅ Liefert Confidence-Scores (Qualitätsindikator)
- ✅ Funktioniert mit realen Aufnahmen (nicht nur synthetische Audio)
- ✅ Aktiv maintained (letztes Update 2024)

**Alternative erwogen**: `crepe`, `aubio` → Monophon, keine Confidence-Scores

---

### TD-2: Warum Preset-System statt Generic-Parameter?
**Entscheidung**: 7 instrument-spezifische Presets statt universeller Einstellungen

**Begründung**:
- ✅ Bessere Ergebnisse durch optimierte Parameter pro Instrument-Typ
- ✅ Einfachere UX für Zielgruppe (12-16 Jahre) - keine technischen Parameter nötig
- ✅ Frequenzbereiche angepasst (z.B. Gesang 80-1200Hz, Klavier 27.5-4186Hz)
- ✅ melodia_trick für Monophon-Instrumente aktiviert (Gesang, Holzbläser, Blechbläser)
- ✅ minimum_note_length angepasst (8-20 Frames je nach Instrument)

**Konfigurierbar in**: Presets unter `presets/*.json`

---

### TD-3: Keine integrierte MIDI-Analyse
**Entscheidung**: Plugin liefert nur MIDI-Dateien, keine Analyse

**Begründung**:
- ✅ Separation of Concerns - MIDI-Comparison-Plugin macht Analyse bereits
- ✅ Reduziert Komplexität dieses Plugins
- ✅ Vermeidet Code-Duplication
- ✅ Modularer: MIDI-Dateien können in anderen Workflows genutzt werden
- ✅ Fokus auf optimale Konversion, nicht auf Analyse

**Workflow**: MP3 → Conversion (dieses Plugin) → Analysis (MIDI-Comparison-Plugin)

---

### TD-4: Confidence-Scores als Qualitätsindikator
**Entscheidung**: Nutze Basic Pitch Confidence-Scores für Qualitätsbewertung

**Begründung**:
- ✅ Direktes Feedback zur Konversionsqualität
- ✅ Hilft Nutzern schlechte Aufnahmen zu identifizieren
- ✅ Basis für spätere Pre/Post-Processing-Entscheidungen
- ✅ Warnung: "Niedrige Confidence → Bitte neu aufnehmen"

---

### TD-5: Deutsche Beschreibungen für Jugendliche
**Entscheidung**: Preset-Beschreibungen auf Deutsch, altersgerecht formuliert

**Begründung**:
- ✅ Zielgruppe: 12-16-jährige Schüler in Deutschland
- ✅ Vermeidet technisches Jargon (Onset Threshold, Frame Threshold)
- ✅ Icons als visuelle Anker (🎹🎸🎤🎺🎷🎻👥)
- ✅ Instrument-Liste zeigt Anwendungsfälle klar

**Beispiel**: "Perfekt für Klavieraufnahmen mit klaren Anschlägen" statt "High onset threshold for percussive onsets"

---

## 📈 Erfolgs-Kriterien

### Funktionale Kriterien
- [x] MP3-Upload funktioniert (max 100MB)
- [x] Preset-Auswahl mit Icons funktioniert
- [x] Basic Pitch konvertiert mit Preset-Parametern
- [ ] MIDI-Download funktioniert
- [ ] Confidence-Scores werden angezeigt
- [ ] Qualitätswarnungen bei niedriger Confidence (<70%)

### Qualitäts-Kriterien
- [ ] Basic Pitch Confidence > 80% bei sauberen Aufnahmen
- [ ] Preset-Parameter liefern bessere Ergebnisse als Generic-Einstellungen
- [ ] MIDI-Dateien können im MIDI-Comparison-Plugin genutzt werden
- [ ] Keine Code-Duplication mit bestehenden Plugins
- [ ] Fehlerbehandlung für alle bekannten Edge-Cases

### Usability-Kriterien
- [x] Preset-Beschreibungen verständlich für 12-16-Jährige
- [x] Icons erleichtern Instrument-Erkennung
- [ ] Workflow intuitiv: Upload → Preset → Konversion → Download
- [ ] Klare Fehlermeldungen bei Problemen
- [ ] Fortschrittsanzeige während Konversion

### Performance-Kriterien
- [ ] Basic Pitch Conversion: <30s pro Minute Audio
- [ ] Gesamtdurchlauf (Upload → MIDI): <60s für 2min Audio
- [ ] Frontend bleibt responsiv (Progress-Updates alle 2s)

---

## 📚 Referenzen

### Code-Referenzen (bestehende Plugins)
- `Backend/app/plugins/audio_feedback/` - Upload-Pattern, Service-Struktur
- `Backend/app/plugins/midi_comparison/` - MIDI-Analyse (separate Verantwortung)
- `Backend/app/shared/services/` - Session, Storage Services
- `Backend/app/plugins/base/` - Plugin-Interface

### Externe Libraries
- [Basic Pitch Docs](https://github.com/spotify/basic-pitch)
- [Mido MIDI Library](https://mido.readthedocs.io/)
- [Librosa Audio Analysis](https://librosa.org/)

### Projekt-Dokumentation
- `docs/ProjectOverview.md` - Gesamtprojekt-Kontext
- `docs/QuickStartRefactoring.md` - Plugin-Architektur
- `docs/ArchitectureOptimizationPlan.md` - Service-Layer-Design

---

**Ende des Lastenhefts**

---

## 🔄 Änderungshistorie

### v1.3 (17. Dezember 2025)
- **Scope-Reduktion**: Plugin fokussiert sich auf MP3-to-MIDI-Konversion
- **Entfernt**: Taktbasierte Segmentierung, MIDI-Analyse, Report-Generierung
- **Begründung**: MIDI-Comparison-Plugin übernimmt Analyse-Verantwortung
- **Neuer Fokus**: Optimale MIDI-Konversion mit Preset-System
- **Workflow**: Upload → Preset-Auswahl → Konversion → MIDI-Download
- **Weiterverwendung**: MIDI-Dateien können im MIDI-Comparison-Plugin analysiert werden

### v1.2 (17. Dezember 2025)
- Preset-System auf 7 instrument-spezifische Presets reduziert
- Drums-Preset entfernt (ungeeignet für pitch transcription)
- Deutsche Beschreibungen für 12-16-Jährige
- Icons für visuelle Erkennbarkeit integriert
- Backend: Preset-Parameter in Konverter integriert, Legacy-Alias-Support
- Frontend: Icon-Display in Dropdown und Detail-View

### v1.1 (16. Dezember 2025)
- Initiale Konzeption mit vollständiger Analyse-Pipeline
- Taktbasierte Segmentierung konzipiert
- MIDI-Comparison-Integration geplant
- Report-Generierung definiert

### v1.0 (15. Dezember 2025)
- Erstes Lastenheft erstellt
- Basic Pitch als Konversions-Engine ausgewählt
- Plugin-Architektur definiert---

**Ende des Lastenhefts**

---

## 🔄 Änderungshistorie

| Version | Datum | Änderung | Autor |
|---------|-------|----------|-------|
| 1.0 | 2025-12-16 | Initial-Version erstellt | GitHub Copilot |
| 1.1 | 2025-12-17 | Ausformulierte Presets (8 inkl. Drums), YAML-Beispiele | GitHub Copilot |
| 1.2 | 2025-12-17 | Presets auf 7 reduziert (ohne Drums), englische IDs, JSON-Schema verschlankt, Frontend-Contract und Default-Parameter aktualisiert | GitHub Copilot |
