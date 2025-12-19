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
- **Schüler*innen** (Sekundarstufe I): Komponieren einfache Melodien, erkunden generierte Musik
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

### Backend-Struktur (Objektorientierter Ansatz)

```
Backend/app/plugins/markov_generator/
├── config.yaml                           # Plugin-Konfiguration
├── __init__.py                           # Package marker
│
├── markov_generator_plugin.py            # Plugin Entry Point (erbt MusicToolPlugin)
├── markov_generator_routes.py            # Flask Blueprint (API-Layer)
├── markov_generator_service.py           # Orchestrierungs-Service (Facade)
│
├── models/                               # Domain Models
│   ├── __init__.py
│   ├── note.py                           # Note Dataclass
│   ├── melody.py                         # Melody (List[Note] + Validierung)
│   └── markov_state.py                   # MarkovState (Tupel-Wrapper)
│
├── core/                                 # Business Logic
│   ├── __init__.py
│   ├── markov_model.py                   # MarkovModel Klasse (Transition Matrix)
│   ├── melody_generator.py               # MelodyGenerator (Probabilistische Generierung)
│   ├── melody_validator.py               # MelodyValidator (C-Dur Validierung)
│   └── delta_calculator.py               # DeltaCalculator (Before/After Diff)
│
├── repositories/                         # Data Access Layer
│   ├── __init__.py
│   ├── model_repository.py               # ModelRepository (JSON Persistence)
│   ├── melody_repository.py              # MelodyRepository (MIDI File Storage)
│   └── session_code_repository.py        # SessionCodeRepository (Code-Lookup)
│
├── midi/                                 # MIDI-spezifische Logik
│   ├── __init__.py
│   ├── midi_parser.py                    # MidiParser (MIDI → Melody)
│   ├── midi_exporter.py                  # MidiExporter (Melody → MIDI)
│   └── midi_constants.py                 # Konstanten (C_MAJOR_SCALE, BPM, etc.)
│
└── templates/                            # Optional für Prompts
```

### Design-Prinzipien

#### Single Responsibility Principle (SRP)
- **Note**: Repräsentiert eine einzelne musikalische Note
- **Melody**: Verwaltet Liste von Noten + Validierung
- **MarkovModel**: Nur Transition Matrix + Training
- **MelodyGenerator**: Nur probabilistische Generierung
- **MelodyValidator**: Nur C-Dur Validierung
- **Repositories**: Nur Datenpersistierung

#### Open/Closed Principle (OCP)
- `MelodyValidator` als abstrakte Basis → später `MinorScaleValidator` hinzufügbar
- `MelodyGenerator` mit Strategy-Pattern → 1st/2nd/3rd Order austauschbar
- `ModelRepository` mit Interface → später andere Storage-Backends möglich

#### Liskov Substitution Principle (LSP)
- Alle Repositories implementieren gemeinsames Interface
- Validators sind austauschbar

#### Interface Segregation Principle (ISP)
- Kleine, fokussierte Interfaces statt großer Service-Klassen
- `IModelStorage`, `IMelodyStorage`, `ICodeLookup` getrennt

#### Dependency Inversion Principle (DIP)
- Service-Klasse abhängig von Interfaces, nicht Implementierungen
- Dependency Injection via Constructor

### Klassendiagramm (vereinfacht)

```
┌─────────────────────────────────────┐
│   MarkovGeneratorService (Facade)   │
├─────────────────────────────────────┤
│ - model_repo: IModelStorage         │
│ - melody_repo: IMelodyStorage       │
│ - code_repo: ICodeLookup            │
│ - validator: IMelodyValidator       │
│ - generator: IMelodyGenerator       │
├─────────────────────────────────────┤
│ + create_class_session()            │
│ + join_class_session()              │
│ + upload_melody()                   │
│ + generate_melody()                 │
│ + export_model()                    │
└─────────────────────────────────────┘
           ↓ delegates to
    ┌──────────────┬──────────────┬──────────────┐
    ↓              ↓              ↓              ↓
┌─────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐
│ Model   │  │ Melody     │  │ Code       │  │ Melody   │
│ Repo    │  │ Repo       │  │ Repo       │  │ Generator│
└─────────┘  └────────────┘  └────────────┘  └──────────┘
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

## 📊 Datenmodelle (Objektorientiert)

### 1. Domain Models

#### Note (models/note.py)
```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)  # Immutable für Hashability
class Note:
    """Repräsentiert eine einzelne musikalische Note oder Pause."""
    pitch: Optional[int]  # 60-71 (C4-B4) oder None für Pause
    duration: int         # 1 = Viertelnote, 0.5 = Achtelnote (später)
    is_rest: bool = False # True bei Pause
    
    def __post_init__(self):
        """Validierung beim Erstellen."""
        if not self.is_rest and self.pitch is None:
            raise ValueError("Nicht-Pause Note muss pitch haben")
        if self.is_rest and self.pitch is not None:
            raise ValueError("Pause kann keinen pitch haben")
        if self.duration <= 0:
            raise ValueError("Duration muss positiv sein")
    
    def to_midi_note(self) -> int:
        """Konvertiert zu MIDI-Notennummer."""
        if self.is_rest:
            raise ValueError("Pause hat keine MIDI-Note")
        return self.pitch
    
    @classmethod
    def from_midi(cls, pitch: int, duration: int = 1) -> 'Note':
        """Factory Method für MIDI-Import."""
        return cls(pitch=pitch, duration=duration, is_rest=False)
    
    @classmethod
    def rest(cls, duration: int = 1) -> 'Note':
        """Factory Method für Pause."""
        return cls(pitch=None, duration=duration, is_rest=True)
```

#### Melody (models/melody.py)
```python
from typing import List
from .note import Note

class Melody:
    """Repräsentiert eine Melodie als Sequenz von Noten."""
    
    def __init__(self, notes: List[Note], name: str = ""):
        self._notes = notes
        self.name = name
    
    @property
    def notes(self) -> List[Note]:
        """Read-only Zugriff auf Noten."""
        return self._notes.copy()
    
    @property
    def length(self) -> int:
        """Anzahl der Noten."""
        return len(self._notes)
    
    @property
    def duration(self) -> float:
        """Gesamtdauer in Viertelnoten."""
        return sum(note.duration for note in self._notes)
    
    def get_note_pairs(self) -> List[tuple[Note, Note]]:
        """Gibt alle aufeinanderfolgenden Note-Paare zurück."""
        return [(self._notes[i], self._notes[i+1]) 
                for i in range(len(self._notes) - 1)]
    
    def get_transitions(self) -> List[tuple[Note, Note, Note]]:
        """Gibt alle 2nd-order Transitions zurück (prev, curr, next)."""
        return [(self._notes[i], self._notes[i+1], self._notes[i+2])
                for i in range(len(self._notes) - 2)]
```

#### MarkovState (models/markov_state.py)
```python
from dataclasses import dataclass
from typing import Tuple
from .note import Note

@dataclass(frozen=True)
class MarkovState:
    """Repräsentiert einen 2nd-order Markov State (2 Noten)."""
    note1: Note
    note2: Note
    
    def to_tuple(self) -> Tuple[Note, Note]:
        """Konvertiert zu Tupel für Dictionary-Keys."""
        return (self.note1, self.note2)
    
    @classmethod
    def from_tuple(cls, tup: Tuple[Note, Note]) -> 'MarkovState':
        """Factory Method aus Tupel."""
        return cls(note1=tup[0], note2=tup[1])
```

---

### 2. Core Business Logic

#### MarkovModel (core/markov_model.py)
```python
from typing import Dict, List, Optional
from collections import defaultdict
from ..models.note import Note
from ..models.markov_state import MarkovState

class MarkovModel:
    """2nd-Order Markov Chain für Melodie-Generierung."""
    
    def __init__(self):
        # State → {Next Note → Count}
        self._transitions: Dict[MarkovState, Dict[Note, int]] = defaultdict(lambda: defaultdict(int))
        self._total_count = 0
    
    def train(self, melody: 'Melody') -> None:
        """Trainiert Modell mit einer Melodie."""
        transitions = melody.get_transitions()
        
        for prev, curr, next_note in transitions:
            state = MarkovState(prev, curr)
            self._transitions[state][next_note] += 1
            self._total_count += 1
    
    def get_next_note_distribution(self, state: MarkovState) -> Dict[Note, float]:
        """Gibt Wahrscheinlichkeitsverteilung für nächste Note zurück."""
        if state not in self._transitions:
            return {}
        
        counts = self._transitions[state]
        total = sum(counts.values())
        return {note: count / total for note, count in counts.items()}
    
    def get_all_states(self) -> List[MarkovState]:
        """Gibt alle trainierten States zurück."""
        return list(self._transitions.keys())
    
    def get_transition_count(self) -> int:
        """Gesamtanzahl trainierter Übergänge."""
        return self._total_count
    
    @property
    def is_trained(self) -> bool:
        """Prüft ob Modell trainiert wurde."""
        return len(self._transitions) > 0
```

#### MelodyGenerator (core/melody_generator.py)
```python
import random
from typing import Optional, List
from ..models.note import Note
from ..models.melody import Melody
from ..models.markov_state import MarkovState
from .markov_model import MarkovModel

class MelodyGenerator:
    """Generiert Melodien aus Markov-Modell."""
    
    def __init__(self, model: MarkovModel, fallback_notes: List[Note]):
        self._model = model
        self._fallback_notes = fallback_notes
    
    def generate(
        self, 
        length: int, 
        seed: Optional[MarkovState] = None
    ) -> Melody:
        """Generiert neue Melodie."""
        if not self._model.is_trained:
            raise ValueError("Modell muss erst trainiert werden")
        
        # Seed wählen
        if seed is None:
            seed = self._random_seed()
        
        # Starte mit Seed-Noten
        notes = [seed.note1, seed.note2]
        
        # Generiere restliche Noten
        for _ in range(length - 2):
            current_state = MarkovState(notes[-2], notes[-1])
            next_note = self._sample_next_note(current_state)
            notes.append(next_note)
        
        return Melody(notes, name="Generated")
    
    def _random_seed(self) -> MarkovState:
        """Wählt zufälligen Seed-State."""
        states = self._model.get_all_states()
        if not states:
            # Fallback bei leerem Modell
            return MarkovState(
                random.choice(self._fallback_notes),
                random.choice(self._fallback_notes)
            )
        return random.choice(states)
    
    def _sample_next_note(self, state: MarkovState) -> Note:
        """Sampelt nächste Note basierend auf Wahrscheinlichkeiten."""
        distribution = self._model.get_next_note_distribution(state)
        
        if not distribution:
            # Fallback wenn State unbekannt
            return random.choice(self._fallback_notes)
        
        # Gewichtetes Sampling
        notes = list(distribution.keys())
        weights = list(distribution.values())
        return random.choices(notes, weights=weights, k=1)[0]
```

#### MelodyValidator (core/melody_validator.py)
```python
from abc import ABC, abstractmethod
from typing import List
from ..models.note import Note
from ..models.melody import Melody
from ..midi.midi_constants import C_MAJOR_SCALE

class IMelodyValidator(ABC):
    """Interface für Melodie-Validierung."""
    
    @abstractmethod
    def validate(self, melody: Melody) -> bool:
        pass
    
    @abstractmethod
    def filter_valid_notes(self, notes: List[Note]) -> List[Note]:
        pass

class CMajorValidator(IMelodyValidator):
    """Validiert Melodien auf C-Dur-Konformität."""
    
    def validate(self, melody: Melody) -> bool:
        """Prüft ob alle Noten C-Dur sind."""
        for note in melody.notes:
            if note.is_rest:
                continue
            if note.pitch not in C_MAJOR_SCALE:
                return False
        return True
    
    def filter_valid_notes(self, notes: List[Note]) -> List[Note]:
        """Filtert nur gültige C-Dur-Noten."""
        return [note for note in notes 
                if note.is_rest or note.pitch in C_MAJOR_SCALE]
```

#### DeltaCalculator (core/delta_calculator.py)
```python
from typing import Dict, Any, Set
from ..models.markov_state import MarkovState
from ..models.note import Note

class DeltaCalculator:
    """Berechnet Unterschiede zwischen Modell-Snapshots."""
    
    def calculate(
        self, 
        before: Dict[str, Any], 
        after: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Berechnet Delta zwischen zwei Snapshots."""
        before_states = set(before.get('states', []))
        after_states = set(after.get('states', []))
        
        new_states = after_states - before_states
        changed_transitions = self._find_changed_transitions(before, after)
        
        return {
            'new_states': list(new_states),
            'changed_transitions': changed_transitions,
            'state_count_delta': len(after_states) - len(before_states)
        }
    
    def _find_changed_transitions(
        self, 
        before: Dict, 
        after: Dict
    ) -> List[Dict]:
        """Findet Transitions mit geänderten Wahrscheinlichkeiten."""
        # Implementation für Transition-Diff
        return []
```

---

### 3. Data Access Layer (Repositories)

#### IModelStorage (repositories/__init__.py)
```python
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path

class IModelStorage(ABC):
    """Interface für Modell-Persistierung."""
    
    @abstractmethod
    def save(self, session_id: str, model_data: dict) -> None:
        pass
    
    @abstractmethod
    def load(self, session_id: str) -> Optional[dict]:
        pass
    
    @abstractmethod
    def exists(self, session_id: str) -> bool:
        pass

class IMelodyStorage(ABC):
    """Interface für Melodie-Speicherung."""
    
    @abstractmethod
    def save_midi(self, session_id: str, melody_id: str, midi_data: bytes) -> Path:
        pass
    
    @abstractmethod
    def load_midi(self, session_id: str, melody_id: str) -> Optional[bytes]:
        pass

class ICodeLookup(ABC):
    """Interface für Klassencode-Lookup."""
    
    @abstractmethod
    def register_code(self, code: str, session_id: str) -> None:
        pass
    
    @abstractmethod
    def lookup_session(self, code: str) -> Optional[str]:
        pass
    
    @abstractmethod
    def code_exists(self, code: str) -> bool:
        pass
```

#### ModelRepository (repositories/model_repository.py)
```python
import json
from pathlib import Path
from typing import Optional
from . import IModelStorage

class ModelRepository(IModelStorage):
    """JSON-basierte Modell-Persistierung."""
    
    def __init__(self, base_path: Path):
        self._base_path = base_path
    
    def save(self, session_id: str, model_data: dict) -> None:
        """Speichert Modell als JSON."""
        session_dir = self._base_path / session_id
        session_dir.mkdir(exist_ok=True)
        
        file_path = session_dir / f"markov_model_{session_id}.json"
        with open(file_path, 'w') as f:
            json.dump(model_data, f, indent=2)
    
    def load(self, session_id: str) -> Optional[dict]:
        """Lädt Modell aus JSON."""
        file_path = self._base_path / session_id / f"markov_model_{session_id}.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def exists(self, session_id: str) -> bool:
        """Prüft ob Modell existiert."""
        file_path = self._base_path / session_id / f"markov_model_{session_id}.json"
        return file_path.exists()
```

---

### 4. Service Layer (Facade)

#### MarkovGeneratorService (markov_generator_service.py)
```python
from typing import Dict, Any, Optional
import uuid
from pathlib import Path

from .core.markov_model import MarkovModel
from .core.melody_generator import MelodyGenerator
from .core.melody_validator import CMajorValidator
from .core.delta_calculator import DeltaCalculator
from .repositories.model_repository import ModelRepository
from .repositories.melody_repository import MelodyRepository
from .repositories.session_code_repository import SessionCodeRepository
from .midi.midi_parser import MidiParser
from .midi.midi_exporter import MidiExporter
from .midi.midi_constants import C_MAJOR_NOTES

class MarkovGeneratorService:
    """Orchestrierungs-Service (Facade Pattern)."""
    
    def __init__(
        self, 
        session_service,
        storage_service,
        plugin_config: Dict[str, Any]
    ):
        # Shared Services
        self._session_service = session_service
        self._storage_service = storage_service
        self._config = plugin_config
        
        # Repositories
        base_path = Path(storage_service.base_path)
        self._model_repo = ModelRepository(base_path)
        self._melody_repo = MelodyRepository(storage_service)
        self._code_repo = SessionCodeRepository()
        
        # Core Components
        self._validator = CMajorValidator()
        self._delta_calc = DeltaCalculator()
        self._midi_parser = MidiParser()
        self._midi_exporter = MidiExporter()
    
    def create_class_session(self) -> Dict[str, str]:
        """Erstellt neue Klassen-Session."""
        # Session erstellen
        session = self._session_service.create_session()
        
        # Klassencode generieren
        code = self._code_repo.generate_unique_code()
        self._code_repo.register_code(code, session.session_id)
        
        # Leeres Modell initialisieren
        model = MarkovModel()
        self._save_model(session.session_id, model)
        
        return {
            'class_code': code,
            'session_id': session.session_id
        }
    
    def upload_melody(
        self, 
        session_id: str, 
        midi_data: bytes,
        student_name: str
    ) -> Dict[str, Any]:
        """Verarbeitet Melodie-Upload."""
        # 1. MIDI parsen
        melody = self._midi_parser.parse(midi_data)
        
        # 2. Validieren
        if not self._validator.validate(melody):
            melody = Melody(
                self._validator.filter_valid_notes(melody.notes),
                name=student_name
            )
        
        # 3. Snapshot vor Training
        model = self._load_model(session_id)
        snapshot_before = self._create_snapshot(model)
        
        # 4. Training
        model.train(melody)
        
        # 5. Snapshot nach Training
        snapshot_after = self._create_snapshot(model)
        delta = self._delta_calc.calculate(snapshot_before, snapshot_after)
        
        # 6. Modell speichern
        self._save_model(session_id, model)
        
        # 7. MIDI speichern
        melody_id = str(uuid.uuid4())
        self._melody_repo.save_midi(session_id, melody_id, midi_data)
        
        return {
            'melody_id': melody_id,
            'delta': delta,
            'snapshot': snapshot_after
        }
    
    def generate_melody(
        self,
        session_id: str,
        length: int,
        seed_notes: Optional[list] = None
    ) -> bytes:
        """Generiert neue Melodie."""
        model = self._load_model(session_id)
        generator = MelodyGenerator(model, C_MAJOR_NOTES)
        
        melody = generator.generate(length, seed=None)  # TODO: Seed handling
        
        return self._midi_exporter.export(melody)
    
    # Private Helpers
    def _load_model(self, session_id: str) -> MarkovModel:
        """Lädt Modell aus Repository."""
        data = self._model_repo.load(session_id)
        if data is None:
            return MarkovModel()
        return MarkovModel.from_dict(data)
    
    def _save_model(self, session_id: str, model: MarkovModel) -> None:
        """Speichert Modell in Repository."""
        self._model_repo.save(session_id, model.to_dict())
    
    def _create_snapshot(self, model: MarkovModel) -> Dict[str, Any]:
        """Erstellt Snapshot für Visualisierung."""
        # TODO: Implementation
        return {}
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
