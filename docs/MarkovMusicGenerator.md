# 🎵 Lastenheft: Markov-Musikgenerator-Plugin

**MuDiKo KI Assistant - Erweiterung für kollaborative Musikkomposition mit Machine Learning**

---

## 📋 Projektübersicht

### Projektname
Markov-Musikgenerator-Plugin für MuDiKo KI Assistant

### Version
1.0.0 (Initial MVP)

### Datum
Dezember 2025

### Branch
`Experimental_Markov_Music_Generator`

---

## 🎯 Zielsetzung

### Pädagogisches Ziel
Ein innovatives Tool für den digitalen Musikunterricht, das Schüler*innen spielerisch an die Themen Musikkomposition, Wahrscheinlichkeitstheorie und Machine Learning heranführt. Durch kollaboratives Komponieren einfacher Melodien entsteht ein klassenweites Markov-Modell, das neue Musikstücke generiert und musikalische Muster sichtbar macht.

### Lernziele
- **Musikalisch**: Verständnis für Melodiestrukturen, Notenfolgen und musikalische Zusammenhänge
- **Mathematisch**: Spielerischer Zugang zu Wahrscheinlichkeiten und statistischen Mustern
- **Technologisch**: Einblick in Machine Learning und datenbasierte Musikgenerierung
- **Kollaborativ**: Gemeinsames Erschaffen eines Klassenwerks

---

## 👥 Zielgruppen

### Primäre Nutzer
- **Schüler*innen** (Grundschule bis Sekundarstufe I): Komponieren einfache Melodien, erkunden generierte Musik
- **Lehrkräfte**: Moderieren Klassenaktivitäten, exportieren/importieren Modelle für spätere Stunden

### Nutzungskontext
- **Klassenzimmer**: Gemeinsame Session mit Beamer/Whiteboard für Visualisierung
- **Einzelarbeit**: Schüler*innen komponieren auf eigenen Geräten (Tablets, Laptops)
- **Hausaufgaben**: Optional zum Experimentieren außerhalb des Unterrichts

---

## 🔧 Funktionale Anforderungen

### 1. Session-Management

#### FA-1.1: Klassen-Session erstellen
- Jede*r Nutzer*in kann eine neue Klassen-Session initiieren
- System generiert automatisch einen 6-stelligen alphanumerischen Klassencode
- Code ist eindeutig und kollisionsfrei (bei Duplikat: automatischer Retry)
- Session hat eine Lebensdauer von 8 Stunden (TTL: 28800 Sekunden)

#### FA-1.2: Klassen-Session beitreten
- Nutzer*innen können über Klassencode einer bestehenden Session beitreten
- Code-Eingabe über einfaches Textfeld
- Bei gültigem Code: Zugang zur gemeinsamen Session
- Bei ungültigem Code: Fehlermeldung mit Hinweis

#### FA-1.3: Session-Persistierung
- Markov-Modell wird als JSON-Datei gespeichert: `markov_model_{session_id}.json`
- Speicherort: `Backend/app/Uploads/{session_id}/`
- Automatisches Laden beim Beitritt zur Session
- Automatisches Löschen nach 8 Stunden durch Garbage Collector

---

### 2. Melodie-Komposition

#### FA-2.1: Vereinfachtes MIDI-Keyboard
- Virtuelles Keyboard nur mit C-Dur-Tonleiter (weiße Tasten)
- Tonumfang: C4 bis B4 (MIDI-Noten 60-71)
- Tasten: C, D, E, F, G, A, B + Pause-Button
- Visualisierung als Button-Grid im MuDiKo-Design

#### FA-2.2: Quantisiertes Notenraster
- Melodien werden in 4/4-Takt eingegeben
- Nur Viertelnoten als Notenwerte (Architektur für Achtelnoten vorbereitet)
- Pausen sind als Viertelpausen möglich
- Maximale Melodielänge: 16 Noten (4 Takte)

#### FA-2.3: Echtzeit-Playback
- Play-Button zum Abspielen der komponierten Melodie
- Audio-Synthese via Web Audio API
- Piano-ähnlicher Oszillator (Mischung aus Sinus- und Triangle-Waveform)
- ADSR-Envelope für natürlichen Klang
- Festes Tempo: 120 BPM

#### FA-2.4: MIDI-Upload
- Schüler*innen können komponierte Melodie hochladen
- Eingabe des eigenen Namens (optional für Personalisierung)
- System generiert eindeutige Melodie-ID (UUID)
- Speicherung als `melody_{uuid}.mid` in Session-Ordner

#### FA-2.5: Melodie-Download
- Nach Upload: Download-Link für eigene Melodie
- Download per Melodie-ID ohne zusätzliche Authentifizierung
- MIDI-Datei kann lokal gespeichert und in anderen Programmen geöffnet werden

---

### 3. Markov-Modell-Training

#### FA-3.1: Datenstruktur
- **Note-Objekt**: `Note(pitch: Optional[int], duration: int, is_rest: bool)`
  - `pitch`: MIDI-Notennummer (60-71) oder `None` bei Pause
  - `duration`: 1 = Viertelnote (später erweiterbar auf 0.5 = Achtelnote)
  - `is_rest`: Boolean-Flag für Pausen

#### FA-3.2: 2nd-Order Markov Chain
- Modell basiert auf Übergängen zwischen 2 aufeinanderfolgenden Noten
- State: Tupel aus zwei `Note`-Objekten
- Transition Matrix: `Dict[Tuple[Note, Note], Dict[Note, int]]` (Häufigkeits-Counts)

#### FA-3.3: Inkrementelles Training
- Bei jedem Melodie-Upload: Modell wird sofort aktualisiert
- Neue Übergänge werden zu bestehenden Counts addiert
- Modell-JSON wird nach jedem Training gespeichert
- Keine Batch-Verarbeitung – Echtzeit-Update

#### FA-3.4: Validierung
- Nur C-Dur-Noten werden akzeptiert (60-71, weiße Tasten)
- Nicht-konforme Noten werden gefiltert
- Mindestlänge: 3 Noten (für mindestens einen 2nd-order Übergang)

---

### 4. Musik-Generierung

#### FA-4.1: Generierungs-Parameter
- **Länge**: Anzahl der zu generierenden Noten (4-32 Noten)
- **Seed**: Start-Note-Paar für Generierung
  - Random Seed: System wählt zufällig aus existierenden States
  - Manuell: Auswahl aus Dropdowns (nur trainierte Kombinationen)

#### FA-4.2: Probabilistische Generierung
- Gewichtete Zufallsauswahl basierend auf Transition-Wahrscheinlichkeiten
- Normalisierung der Counts zu Wahrscheinlichkeiten
- Bei fehlenden Übergängen: Fallback auf Random-Note aus C-Dur-Skala

#### FA-4.3: MIDI-Export
- Generierte Melodie wird als MIDI-Datei exportiert
- Tempo: 120 BPM
- Ticks per Beat: 480
- Format: Standard MIDI File (Type 0)

#### FA-4.4: Direktes Playback
- Generierte Melodie kann direkt im Browser abgespielt werden
- Gleicher Piano-Oszillator wie bei Komposition

---

### 5. Visualisierung

#### FA-5.1: Netzwerk-Graph
- Knoten = Noten (C, D, E, F, G, A, B, Pause)
- Kanten = Übergangswahrscheinlichkeiten zwischen Note-Paaren
- Rendering via HTML Canvas oder SVG

#### FA-5.2: Force-Directed Layout
- Einfache JavaScript-Physik-Engine (ohne externe Library)
- Sehr langsame Animation (Dämpfung 0.1)
- Iterations-Limit: 5 pro Frame für Performance
- Pause nach Konvergenz (Stabilisierung)

#### FA-5.3: Top-20-Filter
- Standard-Ansicht: Nur 20 häufigste Übergänge
- Optional: Toggle für vollständige Ansicht
- Reduziert visuelle Komplexität bei vielen Daten

#### FA-5.4: Live-Updates
- Bei neuem Melodie-Upload: Delta-Visualisierung
- Neue Übergänge werden farblich hervorgehoben
- Interpolation über 2-3 Sekunden für sanfte Übergänge
- Zeigt grobe Tendenz, nicht exakte Statistik

#### FA-5.5: Styling
- Knoten: MuDiKo-Gradient (`--mudiko-gradient`)
- Kanten: Liniendicke proportional zu Wahrscheinlichkeit
- Legende: Erklärung der Farben und Größen
- Integration in Card-Layout

---

### 6. Modell-Persistierung

#### FA-6.1: Export
- Modell kann als JSON-Datei heruntergeladen werden
- Format: `{metadata: {...}, transition_matrix: {...}}`
- Metadaten: Anzahl Melodien, Erstellungsdatum, Session-Code
- Dateiname: `markov_model_{class_code}_{date}.json`

#### FA-6.2: Import
- JSON-Datei kann hochgeladen werden
- Erstellt neue Session mit importierten Daten
- Überschreibt bestehendes Modell (kein Merge)
- Validierung der JSON-Struktur

#### FA-6.3: Keine Reset-Funktion
- Kein manueller Reset-Button (Troll-Schutz)
- Neue Session erstellen für Neustart
- Alte Sessions werden automatisch nach 8h gelöscht

---

## 🎨 Nicht-funktionale Anforderungen

### NFA-1: Usability
- **Einfachheit**: UI für Grundschüler verständlich
- **Intuitivität**: Keine Schulung erforderlich
- **Feedback**: Sofortige visuelle Rückmeldung bei Aktionen
- **Fehlertoleranz**: Klare Fehlermeldungen, keine Abstürze

### NFA-2: Performance
- **Latenz**: Playback-Start < 100ms
- **Upload**: Verarbeitung < 2 Sekunden
- **Visualisierung**: Flüssige Animation (30+ FPS)
- **Session-Kapazität**: 30+ Schüler*innen pro Session

### NFA-3: Design
- **Konsistenz**: MuDiKo-Design-System einhalten
- **Farben**: CSS-Variablen nutzen (`--bg-color`, `--button-color`, etc.)
- **Komponenten**: Wiederverwendung von `Button.jsx`, `Card.jsx`, etc.
- **Responsivität**: Mobile und Desktop optimiert

### NFA-4: Sicherheit
- **Vertrauen**: Keine Authentifizierung (Klassenzimmer-Kontext)
- **Isolation**: Sessions strikt getrennt
- **Cleanup**: Automatisches Löschen nach TTL
- **Validierung**: Input-Validierung gegen Injection

### NFA-5: Wartbarkeit
- **Code-Qualität**: PEP 8 (Python), ESLint (JavaScript)
- **Dokumentation**: Inline-Kommentare, README
- **Modularität**: Klare Trennung Backend/Frontend/Service
- **Erweiterbarkeit**: Architektur für Features vorbereitet (Achtelnoten, Tonarten)

---

## 🏗️ Systemarchitektur

### Backend-Struktur
```
Backend/app/plugins/markov_generator/
├── config.yaml                      # Plugin-Konfiguration
├── markov_generator_plugin.py       # Plugin-Hauptklasse (erbt MusicToolPlugin)
├── markov_generator_routes.py       # Flask Blueprint mit API-Endpunkten
├── markov_generator_service.py      # Markov-Modell-Logik
└── templates/                       # Optional für Prompts
```

### Frontend-Struktur
```
Frontend/src/pages/markov-generator/
├── MarkovGeneratorJoinPage.jsx      # Session erstellen/beitreten
├── MarkovGeneratorComposePage.jsx   # Keyboard & Komposition
├── MarkovGeneratorGeneratePage.jsx  # Melodie-Generierung
└── MarkovGeneratorVisualizePage.jsx # Modell-Visualisierung
```

---

## 🔌 API-Spezifikation

### Endpunkte

#### POST `/api/tools/markov-generator/create-class`
**Request:** `{}`  
**Response:** `{class_code: string, session_id: string}`

#### POST `/api/tools/markov-generator/join-class`
**Request:** `{class_code: string}`  
**Response:** `{session_id: string, success: boolean}`

#### POST `/api/tools/markov-generator/upload`
**Request:** FormData mit `midi_file` + `student_name`  
**Response:** `{melody_id: string, delta: object, snapshot: object}`

#### GET `/api/tools/markov-generator/download/:melody_id`
**Response:** MIDI-Datei (application/octet-stream)

#### GET `/api/tools/markov-generator/model/snapshot`
**Response:** `{top20: array, metadata: object}`

#### POST `/api/tools/markov-generator/generate`
**Request:** `{length: int, seed_notes: array|null}`  
**Response:** `{midi_data: base64, filename: string}`

#### GET `/api/tools/markov-generator/export`
**Response:** JSON-Datei (application/json)

#### POST `/api/tools/markov-generator/import`
**Request:** FormData mit `model_file`  
**Response:** `{session_id: string, class_code: string}`

---

## 📊 Datenmodelle

### Note
```python
@dataclass
class Note:
    pitch: Optional[int]  # 60-71 or None
    duration: int         # 1 = quarter note
    is_rest: bool         # True if pause
```

### MarkovModel
```python
class MarkovModel:
    transition_matrix: Dict[Tuple[Note, Note], Dict[Note, int]]
    metadata: Dict[str, Any]
    
    def train_incremental(melody: List[Note]) -> None
    def get_snapshot() -> Dict
    def calculate_delta(before: Dict, after: Dict) -> Dict
    def generate(length: int, seed: Optional[Tuple]) -> List[Note]
    def to_dict() -> Dict
    def from_dict(data: Dict) -> MarkovModel
    def save_to_file(path: Path) -> None
    def load_from_file(path: Path) -> MarkovModel
```

---

## 🎓 User Stories

### US-1: Session starten (Lehrkraft)
**Als** Lehrkraft  
**möchte ich** eine neue Klassen-Session erstellen  
**damit** meine Schüler*innen gemeinsam komponieren können.

**Akzeptanzkriterien:**
- Button "Session erstellen" ist sichtbar
- Klassencode wird automatisch generiert
- Code wird prominent angezeigt (zum Abschreiben)
- Session ist 8 Stunden gültig

### US-2: Session beitreten (Schüler*in)
**Als** Schüler*in  
**möchte ich** über den Klassencode der Session beitreten  
**damit** ich Melodien komponieren kann.

**Akzeptanzkriterien:**
- Eingabefeld für Code ist vorhanden
- Bei richtigem Code: Weiterleitung zur Kompositionsseite
- Bei falschem Code: Verständliche Fehlermeldung

### US-3: Melodie komponieren (Schüler*in)
**Als** Schüler*in  
**möchte ich** eine einfache Melodie auf einem Keyboard eingeben  
**damit** ich meine musikalischen Ideen umsetzen kann.

**Akzeptanzkriterien:**
- Keyboard zeigt nur C-Dur-Noten
- Noten werden in Raster eingetragen
- Play-Button spielt Melodie ab
- Pause-Button ist verfügbar

### US-4: Melodie hochladen (Schüler*in)
**Als** Schüler*in  
**möchte ich** meine Melodie hochladen  
**damit** sie zum Klassenmodell beiträgt.

**Akzeptanzkriterien:**
- Upload-Button ist sichtbar
- Name kann eingegeben werden
- Erfolgsmeldung nach Upload
- Download-Link für eigene Melodie

### US-5: Modell visualisieren (alle)
**Als** Nutzer*in  
**möchte ich** sehen, wie meine Melodie das Modell verändert  
**damit** ich den Einfluss meiner Komposition verstehe.

**Akzeptanzkriterien:**
- Graph zeigt Noten und Übergänge
- Neue Übergänge sind hervorgehoben
- Animation ist langsam und verständlich
- Legende erklärt Visualisierung

### US-6: Neue Melodie generieren (alle)
**Als** Nutzer*in  
**möchte ich** eine neue Melodie vom Modell generieren lassen  
**damit** ich höre, was das Modell gelernt hat.

**Akzeptanzkriterien:**
- Länge ist einstellbar
- Random-Seed-Button ist vorhanden
- Generierte Melodie ist abspielbar
- Download als MIDI möglich

### US-7: Modell exportieren (Lehrkraft)
**Als** Lehrkraft  
**möchte ich** das trainierte Modell speichern  
**damit** ich es in der nächsten Stunde weiterverwenden kann.

**Akzeptanzkriterien:**
- Export-Button ist vorhanden
- JSON-Datei wird heruntergeladen
- Dateiname enthält Klassencode und Datum

### US-8: Modell importieren (Lehrkraft)
**Als** Lehrkraft  
**möchte ich** ein gespeichertes Modell laden  
**damit** wir an der vorherigen Stunde anknüpfen können.

**Akzeptanzkriterien:**
- Import-Button ist vorhanden
- JSON-Upload ist möglich
- Neue Session wird mit importierten Daten erstellt

---

## 🚀 Implementierungsplan

### Phase 1: Backend-Grundgerüst (Priorität: Hoch)
- Plugin-Struktur erstellen
- Session-Management implementieren
- Markov-Modell-Klasse entwickeln
- API-Endpunkte definieren
- JSON-Persistierung

### Phase 2: Frontend-Basis (Priorität: Hoch)
- Join-Page erstellen
- Keyboard-Komponente entwickeln
- Notenraster-UI bauen
- Web Audio API Integration

### Phase 3: Modell-Training (Priorität: Hoch)
- Upload-Funktionalität
- Inkrementelles Training
- Delta-Berechnung
- MIDI-Validierung

### Phase 4: Generierung (Priorität: Mittel)
- Generierungs-Algorithmus
- Seed-Auswahl-UI
- MIDI-Export
- Playback-Integration

### Phase 5: Visualisierung (Priorität: Mittel)
- Graph-Rendering-Engine
- Force-directed Layout
- Top-20-Filter
- Live-Update-Animation

### Phase 6: Import/Export (Priorität: Niedrig)
- JSON-Export-Funktionalität
- JSON-Import-Funktionalität
- Validierung
- UI-Integration

### Phase 7: Testing & Polishing (Priorität: Hoch)
- Unit-Tests (Backend)
- Integration-Tests
- UI/UX-Testing mit Schüler*innen
- Performance-Optimierung
- Dokumentation

---

## ✅ Abnahmekriterien

### Funktional
- [ ] Klassen-Sessions können erstellt und beigetreten werden
- [ ] Melodien können komponiert und hochgeladen werden
- [ ] Markov-Modell trainiert korrekt aus Melodien
- [ ] Neue Melodien können generiert werden
- [ ] Visualisierung zeigt Übergangswahrscheinlichkeiten
- [ ] Export/Import funktioniert fehlerfrei
- [ ] Automatisches Cleanup nach 8 Stunden

### Nicht-funktional
- [ ] UI entspricht MuDiKo-Design-System
- [ ] Performance: < 2s Upload-Verarbeitung
- [ ] 30+ Schüler*innen pro Session möglich
- [ ] Mobile-optimiert (Tablet-Nutzung)
- [ ] Keine Abstürze bei ungültigen Inputs

### Pädagogisch
- [ ] Tool ist für Grundschüler verständlich
- [ ] Visualisierung vermittelt Konzept intuitiv
- [ ] Spaßfaktor: Schüler*innen experimentieren gerne
- [ ] Lehrkraft kann Tool ohne Schulung einsetzen

---

## 📚 Offene Fragen & Risiken

### Offene Fragen
1. **Seed-Auswahl**: Soll es eine "Surprise me"-Funktion geben, die besonders ungewöhnliche Seeds wählt?
2. **Geschwindigkeitsvarianz**: Sollen Schüler*innen das Playback-Tempo anpassen können?
3. **Mehrsprachigkeit**: Soll das Tool auf Englisch verfügbar sein?

### Technische Risiken
- **Browser-Kompatibilität**: Web Audio API nicht in allen Browsern identisch → Testing auf Safari, Firefox, Chrome
- **Performance**: Bei 30+ Schüler*innen sehr große Transition Matrix → Lazy Loading oder Pagination
- **Persistierung**: JSON-Dateien können groß werden → Kompression erwägen

### Pädagogische Risiken
- **Überforderung**: Visualisierung zu komplex für jüngere Schüler*innen → Vereinfachte Ansicht anbieten
- **Motivationsverlust**: Generierte Melodien klingen nicht gut → Sicherstellen, dass Modell musikalisch sinnvolle Ergebnisse produziert
- **Vertrauen**: Schüler*innen manipulieren fremde Melodien → Dokumentation über Vertrauenskultur im Klassenzimmer

---

## 📝 Anhang

### Technologie-Stack
- **Backend**: Python 3.10+, Flask 2.x, mido 1.3+
- **Frontend**: React 19, Vite 5, Web Audio API
- **Storage**: JSON-Dateien, Session-Service (TTL 8h)
- **Deployment**: Docker, bestehende MuDiKo-Infrastruktur

### Referenzen
- [MuDiKo Plugin-Architektur](./ArchitectureOptimizationPlan.md)
- [File Naming Conventions](./FileNamingConventions.md)
- [Development Setup](./Development.md)
- [Markov Chains (Wikipedia)](https://en.wikipedia.org/wiki/Markov_chain)
- [Web Audio API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)

---

**Dokument erstellt am:** 19. Dezember 2025  
**Version:** 1.0  
**Status:** Finalisiert für Implementierung
