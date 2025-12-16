# 🎼 MP3-to-MIDI Feedback Plugin - Vision & Lastenheft

**Version:** 1.0  
**Datum:** 16. Dezember 2025  
**Status:** Konzeption  
**Branch:** `Experimental_MP3_to_Midi_Conversion`

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

**Limitation**: Wenn Schüler nur MP3-Aufnahmen liefern können (z.B. Smartphone-Recordings), gibt es keine Note-by-Note-Analyse wie bei MIDI.

### Die Lösung
Ein neues Plugin, das die **Brücke schlägt**:
1. Nimmt MP3-Aufnahmen entgegen (wie Audio-Feedback)
2. Konvertiert sie via **Spotify's Basic Pitch** in MIDI
3. Analysiert die MIDIs **taktbasiert** (wie MIDI-Comparison)
4. Liefert **präzises, notenbasiertes Feedback** mit musikalischer Struktur

### Der Mehrwert
- ✅ **Genauere Analyse**: Note-by-Note-Vergleich statt nur spektraler Features
- ✅ **Taktbasiert**: Musikalisch sinnvolle Segmentierung statt arbiträrer Zeitfenster
- ✅ **Zugänglicher**: Funktioniert mit Smartphone-Aufnahmen, keine MIDI-Hardware nötig
- ✅ **Strukturiert**: LLM erhält Takt-für-Takt-Analyse für präziseres Feedback

---

## 🔄 Abgrenzung zu bestehenden Plugins

| Feature | Audio-Feedback | MIDI-Comparison | **MP3-to-MIDI (NEU)** |
|---------|---------------|-----------------|----------------------|
| **Input-Format** | MP3/WAV/MP4 | MIDI-Dateien | MP3/WAV/MP4 |
| **Analyse-Granularität** | Zeitfenster (8s) | Takt-basiert | **Takt-basiert** |
| **Analyse-Typ** | Spektral, Tempo, Pitch | Noten, Rhythmus, Dynamik | **Noten + Confidence** |
| **Output-Präzision** | Allgemeine Audio-Features | Exakte Note-Unterschiede | **Note-Unterschiede + Qualität** |
| **Vergleichs-Methode** | Audio-Korrelation | MIDI-Event-Matching | **MIDI-Matching** |
| **Nutzt Basic Pitch** | ❌ | ❌ | ✅ |
| **Nutzt MIDI-Analyzer** | ❌ | ✅ | ✅ |
| **Nutzt Audio-Service** | ✅ | ❌ | ✅ (für Segmentierung) |

### Wiederverwendeter Code
- ✅ `SessionService`, `StorageService` (shared)
- ✅ `MidiAnalyzer` Library (MIDI-Comparison-Plugin)
- ✅ `AudioService` (nur für zeitbasierte Segmentierung an Takt-Grenzen)
- ✅ `BasePromptBuilder` (shared)
- ✅ Plugin-Interface (`MusicToolPlugin`)

### Neuer Code
- 🆕 `Mp3ToMidiConverter` - Basic Pitch Integration
- 🆕 `BarBasedAudioSegmenter` - Taktbasierte Audio-Segmentierung
- 🆕 `Mp3ToMidiFeedbackService` - Orchestrierung
- 🆕 `Mp3ToMidiReportGenerator` - Strukturierter Report
- 🆕 Frontend-Pages für neues Tool

---

## ✅ Funktionale Anforderungen

### Must-Have (Phase 1-3)

#### FR-1: MP3-Upload
- **Beschreibung**: Nutzer lädt Referenz- und Schüler-MP3 hoch
- **Input**: 2 MP3/WAV/MP4-Dateien (max. 100 MB je Datei)
- **Output**: Session-ID, Bestätigung der gespeicherten Dateien
- **Validierung**: Unterstützte Formate, Dateigröße

#### FR-2: Basic Pitch MIDI-Konversion
- **Beschreibung**: Beide MP3s werden in MIDI konvertiert
- **Engine**: Spotify Basic Pitch (Python Library)
- **Output**: 2 MIDI-Dateien + Confidence-Scores pro Note
- **Fehlerbehandlung**: Falls keine Noten erkannt → Warnung, aber kein Abbruch

#### FR-3: Takt-Struktur-Extraktion
- **Beschreibung**: MIDI-Parser extrahiert Takt-Struktur aus Referenz-MIDI
- **Output**: 
  - Takt-Grenzen (Bar 0, 1, 2, ...)
  - Tempo (BPM pro Takt)
  - Taktart (4/4, 3/4, etc.)
  - Zeitstempel (Takt X = 0.0s - 2.5s)
- **Besonderheit**: Start bei **Takt 0** (für Auftakte)

#### FR-4: Taktbasierte Audio-Segmentierung
- **Beschreibung**: Audio wird an MIDI-Takt-Grenzen geschnitten
- **Gruppierung**: **4 Takte pro Segment** (musikalische Phrasen)
- **Output**: Liste von Audio-Segmenten mit Metadaten:
  ```python
  {
    'segment_id': 0,
    'bars': [0, 1, 2, 3],
    'time_start': 0.0,
    'time_end': 10.5,
    'tempo_bpm': 120.0,
    'time_signature': '4/4'
  }
  ```
- **Flexibilität**: Variable Takt-Längen bei Tempo-Änderungen

#### FR-5: MIDI-Comparison pro Segment
- **Beschreibung**: Jedes 4-Takt-Segment wird verglichen (Referenz vs. Schüler)
- **Engine**: Bestehender `MidiAnalyzer` aus MIDI-Comparison-Plugin
- **Output**: Pro Segment:
  - Similarity-Score (0-100%)
  - Takt-für-Takt-Unterschiede (Note, Velocity, Duration)
  - Aggregierte Statistiken (Total Differences, Note Count)

#### FR-6: Strukturierter Report
- **Beschreibung**: LLM-freundlicher Text-Report mit klaren Sektionen
- **Struktur**:
  1. **Übersicht**: Gesamt-Ähnlichkeit, Anzahl Segmente, erkannte Takte
  2. **Segment-Details** (pro 4-Takt-Gruppe):
     - Takte X-Y
     - MIDI-Vergleich (Takt-für-Takt-Tabelle wie MIDI-Comparison)
     - Basic Pitch Confidence (Durchschnitt + Ausreißer)
  3. **Zusammenfassung**: Häufigste Fehler, Stärken, Verbesserungsvorschläge

### Should-Have (Phase 4+)
- Audio-Feature-Extraktion pro Segment (Tempo, Tonart, Dynamik)
- Visualisierung: Takt-Timeline im Frontend
- Export: Annotierte MIDI-Dateien mit Fehlern markiert

### Won't-Have (Out of Scope)
- ❌ Echtzeit-Konversion (Basic Pitch braucht ~10-30s pro Minute Audio)
- ❌ Audio-Feature-Comparison (bleibt beim Audio-Feedback-Plugin)
- ❌ Automatische Tempo-Korrektur
- ❌ Polyphonie-Separation (Basic Pitch macht das bereits)

---

## 🏗️ Technische Architektur

### System-Komponenten

```
┌─────────────────────────────────────────────────────────────┐
│                    MP3-to-MIDI Feedback Plugin              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐         ┌──────────────────┐          │
│  │ Upload Handler  │────────►│ Storage Service  │          │
│  └─────────────────┘         └──────────────────┘          │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────┐           │
│  │      Mp3ToMidiFeedbackService               │           │
│  │  (Orchestriert gesamten Workflow)           │           │
│  └─────────────────────────────────────────────┘           │
│           │                                                 │
│           ├──────────────────┬──────────────────┐          │
│           ▼                  ▼                  ▼          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────┐ │
│  │ Mp3ToMidi       │ │ BarBasedAudio   │ │ MidiAnalyzer│ │
│  │ Converter       │ │ Segmenter       │ │ (shared lib)│ │
│  │ (Basic Pitch)   │ │ (neu)           │ │             │ │
│  └─────────────────┘ └─────────────────┘ └─────────────┘ │
│           │                  │                  │          │
│           └──────────────────┴──────────────────┘          │
│                              ▼                             │
│                  ┌───────────────────────┐                 │
│                  │ Mp3ToMidiReport       │                 │
│                  │ Generator             │                 │
│                  └───────────────────────┘                 │
│                              │                             │
└──────────────────────────────┼─────────────────────────────┘
                               ▼
                    ┌──────────────────┐
                    │  LLM Prompt      │
                    │  (für Frontend)  │
                    └──────────────────┘
```

### Modul-Struktur

```
Backend/app/plugins/mp3_to_midi_feedback/
├── __init__.py
├── config.yaml                          # Plugin-Konfiguration
├── mp3_to_midi_feedback_plugin.py       # Plugin-Klasse (MusicToolPlugin)
├── mp3_to_midi_feedback_routes.py       # Flask Routes
├── mp3_to_midi_feedback_service.py      # Hauptlogik
├── mp3_to_midi_converter.py             # Basic Pitch Wrapper
├── bar_based_audio_segmenter.py         # Taktbasierte Segmentierung
├── mp3_to_midi_report_generator.py      # Report-Generator
└── templates/
    └── system_prompt.txt                # LLM-Prompt-Template
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

### Workflow: Upload bis Analyse

```
1. USER: Upload MP3s
   │
   ├─► Frontend: AudioUploadPage.jsx
   │      └─► POST /api/tools/mp3-to-midi-feedback/upload
   │            ├─► SessionService.create_session()
   │            └─► StorageService.save_file(role='referenz')
   │            └─► StorageService.save_file(role='schueler')
   │
   ▼
2. BACKEND: MIDI Conversion
   │
   ├─► POST /api/tools/mp3-to-midi-feedback/convert-and-analyze
   │      └─► Mp3ToMidiFeedbackService.process()
   │            │
   │            ├─► Mp3ToMidiConverter.convert(referenz.mp3)
   │            │     └─► basic_pitch.predict() → referenz.mid + confidence
   │            │
   │            ├─► Mp3ToMidiConverter.convert(schueler.mp3)
   │            │     └─► basic_pitch.predict() → schueler.mid + confidence
   │            │
   ▼            ▼
3. MIDI Analysis: Takt-Struktur extrahieren
   │
   ├─► MidiParser.parse_file(referenz.mid)
   │     └─► Extrahiert:
   │           - Takt-Grenzen (Bar 0, 1, 2, ...)
   │           - Tempo-Änderungen (BPM pro Takt)
   │           - Taktart (4/4, 3/4, ...)
   │           - Zeitstempel (Takt → Sekunden)
   │
   ▼
4. Audio Segmentation: Taktbasiert schneiden
   │
   ├─► BarBasedAudioSegmenter.segment_by_bars()
   │     └─► Input: referenz.mp3 + MIDI-Takt-Zeitstempel
   │     └─► Output: 4 Segmente à 4 Takte
   │           Segment 0: Takte 0-3 (0.0s - 10.5s)
   │           Segment 1: Takte 4-7 (10.5s - 21.0s)
   │           ...
   │
   ▼
5. MIDI Comparison: Pro Segment vergleichen
   │
   ├─► Für jedes Segment:
   │     └─► MidiAnalyzer.compare_files(ref_segment.mid, stu_segment.mid)
   │           └─► Output: ComparisonResult
   │                 - similarity_score: 0.87
   │                 - total_differences: 12
   │                 - per_bar_differences: [...]
   │
   ▼
6. Report Generation: Strukturierter Output
   │
   ├─► Mp3ToMidiReportGenerator.generate()
   │     └─► Input: Alle Segment-Comparisons + Confidence-Scores
   │     └─► Output: Markdown-Report mit Sektionen
   │
   ▼
7. FRONTEND: Prompt anzeigen
   │
   └─► PromptPage.jsx
         └─► Zeigt strukturierten Report
         └─► Copy to Clipboard für LLM
```

### Datenstrukturen

#### Segment-Objekt
```python
{
  'segment_id': 0,
  'bars': [0, 1, 2, 3],
  'time_start': 0.0,
  'time_end': 10.5,
  'tempo_bpm': 120.0,
  'time_signature': '4/4',
  'audio_ref': np.ndarray,      # Audio-Daten Referenz
  'audio_stu': np.ndarray,      # Audio-Daten Schüler
  'midi_ref_path': Path,        # MIDI-Segment Referenz
  'midi_stu_path': Path,        # MIDI-Segment Schüler
  'confidence_ref': [0.92, 0.88, ...],  # Pro Note
  'confidence_stu': [0.75, 0.81, ...]
}
```

#### Comparison-Result (pro Segment)
```python
{
  'segment_id': 0,
  'bars': [0, 1, 2, 3],
  'similarity_score': 0.87,
  'total_differences': 12,
  'midi_comparison': ComparisonResult,  # Von MidiAnalyzer
  'avg_confidence_ref': 0.89,
  'avg_confidence_stu': 0.76,
  'low_confidence_bars': [2, 3]  # Takte mit Confidence < 0.7
}
```

---

## 📄 Output-Struktur

### Report-Template

```markdown
# VERGLEICH: MP3-ZU-MIDI-ANALYSE

===============================================================================
Für die Analyse durch ein KI-System
===============================================================================

## 🎵 ÜBERSICHT

**Referenz-Datei:** teacher_recording.mp3
**Schüler-Datei:** student_recording.mp3

**Gesamtstatistik:**
- Erkannte Takte: 16 (Takt 0 bis Takt 15)
- Anzahl Segmente: 4 (à 4 Takte)
- Durchschnittliche Ähnlichkeit: 82.5%
- Gesamtzahl Unterschiede: 47

**Tempo & Taktart:**
- Takte 0-7: 120 BPM, 4/4
- Takte 8-15: 130 BPM, 4/4 (Tempo-Wechsel bei Takt 8)

**Basic Pitch Confidence:**
- Referenz: ⭐⭐⭐⭐⭐ (Durchschnitt: 91% - Sehr gut)
- Schüler: ⭐⭐⭐⚝☆ (Durchschnitt: 73% - Mittelmäßig)
  ⚠️ Niedrige Confidence in Takten: 2, 3, 11, 14

---

## 📊 SEGMENT-ANALYSE

### 🎼 Segment 1: Takte 0-3 (0.0s - 10.5s)

**Ähnlichkeit:** 88% (Gut)  
**Unterschiede:** 8  
**Tempo:** 120 BPM | Taktart: 4/4  
**Confidence:** Referenz 92% | Schüler 68% ⚠️

#### Takt-für-Takt-Vergleich:

| Position            | Referenz                  | Schüler                   | Status |
|---------------------|---------------------------|---------------------------|--------|
| Takt 0, Zählzeit 1  | C4 (♩, mf)                | C4 (♩, mp) ⚠️             | Dynamik|
| Takt 0, Zählzeit 2  | D4 (♩, mf)                | D4 (♩, mf)                | ✓      |
| Takt 0, Zählzeit 3  | E4 (♩, mf)                | E♭4 (♩, mf) ⚠️            | Note   |
| Takt 0, Zählzeit 4  | F4 (♩, mf)                | F4 (♪, mf) ⚠️             | Dauer  |
| Takt 1, Zählzeit 1  | G4 (𝅗𝅥, f)                 | G4 (𝅗𝅥, f)                 | ✓      |
| ...                 | ...                       | ...                       | ...    |

**Auffälligkeiten:**
- ⚠️ Takt 0: Schüler spielt E♭ statt E (häufiger Fehler)
- ⚠️ Niedrige Confidence in Takt 2-3: Möglicherweise undeutliche Aufnahme

---

### 🎼 Segment 2: Takte 4-7 (10.5s - 21.0s)

**Ähnlichkeit:** 91% (Sehr gut)  
**Unterschiede:** 5  
...

---

## 📝 ZUSAMMENFASSUNG

**Stärken:**
- Rhythmische Genauigkeit in Takten 4-7 und 12-15
- Korrekte Dynamik in den meisten Takten

**Verbesserungspotenzial:**
- Intonation: Häufiges E♭ statt E (Takte 0, 8, 12)
- Notenlängen: Tendenziell zu kurz (Takte 0, 3, 9)
- Aufnahmequalität: Niedrige Confidence-Werte deuten auf Hintergrundgeräusche hin

**Empfehlungen:**
1. Fokus auf Intonation bei Halbtonschritten
2. Bewusstsein für Notenlängen stärken
3. Ruhigere Aufnahmeumgebung wählen
```

---

## 🛠️ Entwicklungs-Phasen

### ✅ Phase 1: Grundgerüst & Basic Pitch Integration
**Ziel**: Plugin läuft, Basic Pitch konvertiert MP3 → MIDI

**Aufgaben**:
- [ ] Plugin-Struktur erstellen (`config.yaml`, `__init__.py`)
- [ ] `Mp3ToMidiFeedbackPlugin` Klasse (implementiert `MusicToolPlugin`)
- [ ] Basic Routes: `/upload`, `/convert-and-analyze`, `/session/cleanup`
- [ ] `Mp3ToMidiConverter` Klasse:
  - [ ] Basic Pitch Integration
  - [ ] Confidence-Score-Extraktion
  - [ ] MIDI-Speicherung
- [ ] `Mp3ToMidiFeedbackService` Skelett
- [ ] Frontend: Tool-Auswahl-Karte in `ToolSelectionPage.jsx`
- [ ] Frontend: `AudioUploadPage.jsx` (ähnlich Audio-Feedback)
- [ ] Minimal-Test: Upload → Conversion → "MIDI erstellt"

**Output**: MP3s hochladen, Basic Pitch konvertiert, MIDI-Dateien liegen vor

---

### ✅ Phase 2: MIDI-Analyse & Taktbasierte Segmentierung
**Ziel**: MIDI-Parser extrahiert Takt-Struktur, Audio wird taktbasiert geschnitten

**Aufgaben**:
- [ ] `MidiParser` auf konvertierte MIDIs anwenden
- [ ] Takt-Struktur extrahieren (Bar-Nummern, Zeitstempel, Tempo, Taktart)
- [ ] `BarBasedAudioSegmenter` Klasse:
  - [ ] MIDI-Takt-Zeitstempel → Audio-Chunk-Grenzen
  - [ ] 4-Takt-Gruppierung
  - [ ] Tempo-Änderungen berücksichtigen
  - [ ] Start bei Takt 0
- [ ] Service erweitern: Segmentierte Daten strukturiert speichern
- [ ] Minimal-Report: "16 Takte erkannt, 4 Segmente erstellt"
- [ ] Frontend: Conversion-Page mit Progress ("Takte werden analysiert...")

**Output**: Taktbasierte Segmentierung funktioniert, Struktur ist extrahiert

---

### ✅ Phase 3: MIDI-Comparison Integration
**Ziel**: Segment-weiser MIDI-Vergleich liefert Takt-für-Takt-Unterschiede

**Aufgaben**:
- [ ] `MidiAnalyzer` pro Segment aufrufen
- [ ] Comparison-Results aggregieren
- [ ] Low-Confidence-Takte identifizieren
- [ ] `Mp3ToMidiReportGenerator` Klasse:
  - [ ] Übersichts-Sektion
  - [ ] Segment-Detail-Sektionen (mit MIDI-Tabellen)
  - [ ] Zusammenfassungs-Sektion
- [ ] Template in `templates/system_prompt.txt`
- [ ] Frontend: Language-Page, Personalization-Page
- [ ] Frontend: Prompt-Page mit strukturiertem Report

**Output**: Vollständiger Report mit Takt-für-Takt-MIDI-Vergleich

---

### 🔄 Phase 4: Polish & Edge-Cases (Optional)
**Ziel**: Production-ready

**Aufgaben**:
- [ ] Leere Takte behandeln (Silence-Detection)
- [ ] Fehlerbehandlung: Basic Pitch schlägt fehl
- [ ] Fehlerbehandlung: Keine Noten erkannt
- [ ] Tempo-Änderungen mid-Song korrekt verarbeiten
- [ ] Frontend: Error-Messages, Loading-States
- [ ] End-to-End-Tests mit verschiedenen MP3-Typen
- [ ] Performance-Optimierung (Basic Pitch ist langsam)

**Output**: Robustes, production-ready Plugin

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

### TD-2: Warum 4 Takte pro Segment?
**Entscheidung**: Gruppierung in 4-Takt-Phrasen

**Begründung**:
- ✅ Musikalisch sinnvoll (Standard-Phrasen-Länge)
- ✅ Balance: Granular genug für Feedback, nicht zu detailliert für LLM
- ✅ Flexibel: In `config.yaml` anpassbar

**Konfigurierbar in**: `config.yaml` → `bars_per_segment: 4`

---

### TD-3: Warum Start bei Takt 0?
**Entscheidung**: Takt-Nummerierung beginnt bei 0

**Begründung**:
- ✅ Unterstützt Auftakte (Pickup-Bars)
- ✅ Konsistent mit MIDI-Standard (Tick 0 = Beginn)
- ✅ `calculate_bar_and_beat()` kann Takt 0 verarbeiten

---

### TD-4: Keine Audio-Feature-Extraktion (vorerst)
**Entscheidung**: Fokus auf MIDI-Comparison, keine Audio-Features

**Begründung**:
- ✅ Reduziert Komplexität in Phase 1-3
- ✅ Audio-Feedback-Plugin macht das bereits
- ✅ MIDI-Comparison ist präziser als spektrale Features
- ✅ Kann später ergänzt werden (Phase 4+)

---

### TD-5: Wiederverwendung von MidiAnalyzer
**Entscheidung**: Nutze bestehenden `MidiAnalyzer` aus MIDI-Comparison

**Begründung**:
- ✅ Bewährt, getestet
- ✅ Liefert bereits taktbasierte Comparison
- ✅ Kein Code-Duplication
- ✅ Konsistenter Output-Format

---

## 📈 Erfolgs-Kriterien

### Funktionale Kriterien
- [ ] MP3-Upload funktioniert (beide Dateien, max 100MB)
- [ ] Basic Pitch konvertiert zuverlässig (>90% success rate)
- [ ] Takt-Struktur wird korrekt extrahiert (Tempo, Taktart, Grenzen)
- [ ] Audio-Segmentierung erfolgt taktbasiert (4-Takt-Gruppen)
- [ ] MIDI-Comparison liefert Takt-für-Takt-Unterschiede
- [ ] Report ist strukturiert und LLM-lesbar
- [ ] Frontend ermöglicht nahtlosen Workflow (Upload → Report)

### Qualitäts-Kriterien
- [ ] Basic Pitch Confidence > 80% bei sauberen Aufnahmen
- [ ] MIDI-Comparison Similarity-Score korrekt (manuelle Validierung)
- [ ] Report-Struktur folgt Template (Übersicht → Details → Zusammenfassung)
- [ ] Keine Code-Duplication mit bestehenden Plugins
- [ ] Fehlerbehandlung für alle bekannten Edge-Cases

### Performance-Kriterien
- [ ] Basic Pitch Conversion: <30s pro Minute Audio
- [ ] Gesamtdurchlauf (Upload → Report): <90s für 2min Audio
- [ ] Frontend bleibt responsiv (Progress-Updates alle 2s)

---

## 📚 Referenzen

### Code-Referenzen (bestehende Plugins)
- `Backend/app/plugins/audio_feedback/` - Upload-Pattern, Service-Struktur
- `Backend/app/plugins/midi_comparison/` - MIDI-Analyse, Report-Generierung
- `Backend/app/shared/libs/midi_analyzer/` - MIDI-Parser, Comparison-Engine
- `Backend/app/shared/services/` - Session, Storage, Audio-Service
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

| Version | Datum | Änderung | Autor |
|---------|-------|----------|-------|
| 1.0 | 2025-12-16 | Initial-Version erstellt | GitHub Copilot |
