# 🏗️ Architektur-Optimierungsplan für MuDiKo KI Assistant

## 📊 Aktuelle Architektur-Analyse

### Stärken ✅
- **Klare Trennung**: Frontend (React) und Backend (Flask) sind getrennt
- **Grundlegende OOP**: `AudioManager` und `AudioFeedbackPipeline` Klassen vorhanden
- **Session-Management**: Grundlegendes Session-System implementiert
- **Docker-Ready**: Containerisierung bereits vorhanden

### Schwachstellen ⚠️
1. **Monolithische Struktur**: Alle Backend-Logik in 3 Dateien (main.py: 412 Zeilen)
2. **Fehlende Abstraktionen**: Keine Plugin-Architektur für neue Tools
3. **Tight Coupling**: Direkte Abhängigkeiten zwischen Komponenten
4. **Mangelnde Erweiterbarkeit**: Hinzufügen neuer Tools erfordert Code-Änderungen überall
5. **Keine Service-Schicht**: Business-Logik direkt in Route-Handlern
6. **Globale Zustände**: `SESSIONS` Dictionary, `original_filenames` im Manager
7. **Fehlende Interfaces**: Keine abstrakten Basisklassen für Tools

---

## 🎯 Ziel-Architektur: Plugin-basierte Tool-Bibliothek

### Vision
Eine modulare, erweiterbare Plattform für verschiedene Musik-Übungstools mit:
- **Plug & Play**: Neue Tools ohne Änderung des Core-Codes hinzufügen
- **Shared Services**: Gemeinsame Services (Audio, Session, Storage)
- **Konsistente APIs**: Einheitliche Schnittstellen für alle Tools
- **Konfigurierbar**: Tools per Config aktivieren/deaktivieren

---

## 📐 Empfohlene Architektur-Muster

### 1. **Plugin-Architecture Pattern**
```
Core System (stabil)
    ↓
Plugin Interface (abstrakt)
    ↓
Tool Plugins (erweiterbar)
```

### 2. **Service Layer Pattern**
```
Routes (HTTP Handling)
    ↓
Service Layer (Business Logic)
    ↓
Data Access Layer (Storage/DB)
```

### 3. **Factory Pattern**
Für die dynamische Erstellung von Tool-Instanzen

### 4. **Strategy Pattern**
Für verschiedene Analyse-Algorithmen innerhalb eines Tools

---

## 🏛️ Neue Ordnerstruktur

```
Backend/
├── app/
│   ├── __init__.py                      # Flask App Factory
│   ├── main.py                          # Application Entry Point (minimal)
│   │
│   ├── core/                            # ⭐ CORE SYSTEM (stabil)
│   │   ├── __init__.py
│   │   ├── app_factory.py               # Flask App Initialisierung
│   │   ├── config.py                    # Konfiguration
│   │   ├── exceptions.py                # Custom Exceptions
│   │   └── extensions.py                # Flask Extensions (CORS, etc.)
│   │
│   ├── shared/                          # 🔧 SHARED SERVICES
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── session_service.py       # Session-Verwaltung
│   │   │   ├── storage_service.py       # Dateispeicherung
│   │   │   ├── audio_service.py         # Audio-Grundoperationen
│   │   │   └── ai_service.py            # OpenAI Integration
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── session.py               # Session Datenmodell
│   │   │   ├── audio_file.py            # Audio Datei Modell
│   │   │   └── analysis_result.py       # Analyse-Ergebnis Modell
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validators.py            # Input-Validierung
│   │       └── decorators.py            # Common Decorators
│   │
│   ├── plugins/                         # 🎵 TOOL PLUGINS
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   ├── plugin_interface.py      # Abstract Base Class
│   │   │   └── plugin_manager.py        # Plugin Discovery & Loading
│   │   │
│   │   ├── audio_feedback/              # Tool 1: Audio Feedback
│   │   │   ├── __init__.py
│   │   │   ├── plugin.py                # Plugin Registration
│   │   │   ├── routes.py                # Tool-spezifische Routes
│   │   │   ├── service.py               # Business Logic
│   │   │   ├── models.py                # Tool-spezifische Modelle
│   │   │   ├── analyzers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tempo_analyzer.py
│   │   │   │   ├── pitch_analyzer.py
│   │   │   │   └── dynamics_analyzer.py
│   │   │   └── config.yaml              # Tool-Konfiguration
│   │   │
│   │   ├── midi_tool/                   # Tool 2: MIDI Tool (geplant)
│   │   │   ├── __init__.py
│   │   │   ├── plugin.py
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   └── config.yaml
│   │   │
│   │   └── rhythm_trainer/              # Tool 3: Rhythmus-Trainer (Beispiel)
│   │       ├── __init__.py
│   │       ├── plugin.py
│   │       └── config.yaml
│   │
│   ├── api/                             # 🌐 API LAYER
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py                # Core API Routes
│   │   │   └── schemas.py               # API Request/Response Schemas
│   │   │
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── session_middleware.py
│   │       └── error_handler.py
│   │
│   └── Uploads/                         # Temporäre Dateien (wie bisher)
│
├── tests/                               # 🧪 TESTS
│   ├── unit/
│   │   ├── test_services/
│   │   └── test_plugins/
│   ├── integration/
│   └── fixtures/
│
├── config/                              # ⚙️ KONFIGURATION
│   ├── default.yaml
│   ├── development.yaml
│   └── production.yaml
│
├── requirements.txt
└── README.md

Frontend/
├── src/
│   ├── core/                            # 🎨 CORE COMPONENTS
│   │   ├── App.jsx
│   │   ├── Router.jsx
│   │   └── Layout.jsx
│   │
│   ├── shared/                          # 🔧 SHARED COMPONENTS
│   │   ├── components/
│   │   │   ├── AudioPlayer.jsx
│   │   │   ├── FileUploader.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useSession.js
│   │   │   ├── useAudioUpload.js
│   │   │   └── useApi.js
│   │   │
│   │   └── services/
│   │       ├── api.js                   # Axios/Fetch Wrapper
│   │       └── session.js               # Session Management
│   │
│   ├── tools/                           # 🎵 TOOL-SPEZIFISCHE SEITEN
│   │   ├── audio-feedback/
│   │   │   ├── pages/
│   │   │   │   ├── AudioUploadPage.jsx
│   │   │   │   ├── RecordingsPage.jsx
│   │   │   │   ├── LanguagePage.jsx
│   │   │   │   ├── InstrumentsPage.jsx
│   │   │   │   ├── PersonalizationPage.jsx
│   │   │   │   └── PromptPage.jsx
│   │   │   │
│   │   │   ├── components/
│   │   │   └── services/
│   │   │
│   │   ├── midi-tool/
│   │   │   └── pages/
│   │   │
│   │   └── rhythm-trainer/
│   │       └── pages/
│   │
│   ├── pages/
│   │   ├── HomePage.jsx                 # Tool-Auswahl
│   │   └── NotFoundPage.jsx
│   │
│   └── assets/
│
└── package.json
```

---

## 🔧 Phase 1: Refactoring (Priorität: HOCH)

### 1.1 Backend: Service Layer einführen
**Ziel**: Business-Logik aus Routes extrahieren

#### Schritt 1: Session Service
```python
# shared/services/session_service.py
from typing import Optional, Dict
from datetime import datetime, timedelta
import uuid
import shutil
from pathlib import Path

class SessionService:
    """Verwaltet User-Sessions und deren Lebenszyklus."""
    
    def __init__(self, base_path: str, ttl_seconds: int = 3600):
        self.base_path = Path(base_path)
        self.ttl_seconds = ttl_seconds
        self._sessions: Dict[str, 'Session'] = {}
    
    def create_session(self) -> 'Session':
        """Erstellt eine neue Session."""
        session_id = uuid.uuid4().hex
        session = Session(session_id, self.base_path, self.ttl_seconds)
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional['Session']:
        """Holt eine existierende Session."""
        session = self._sessions.get(session_id)
        if session and not session.is_expired():
            session.touch()
            return session
        return None
    
    def end_session(self, session_id: str) -> bool:
        """Beendet eine Session und räumt auf."""
        session = self._sessions.pop(session_id, None)
        if session:
            session.cleanup()
            return True
        return False
    
    def cleanup_expired(self):
        """Entfernt abgelaufene Sessions."""
        expired = [
            sid for sid, sess in self._sessions.items() 
            if sess.is_expired()
        ]
        for sid in expired:
            self.end_session(sid)
```

#### Schritt 2: Storage Service
```python
# shared/services/storage_service.py
from pathlib import Path
from typing import List, Optional
import shutil

class StorageService:
    """Verwaltet Dateispeicherung und -zugriff."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file_data, session_id: str, 
                  filename: str) -> Path:
        """Speichert eine Datei in der Session."""
        session_dir = self.base_path / session_id
        session_dir.mkdir(exist_ok=True)
        
        file_path = session_dir / filename
        file_data.save(str(file_path))
        return file_path
    
    def get_file_path(self, session_id: str, 
                      filename: str) -> Optional[Path]:
        """Gibt den Pfad zu einer Datei zurück."""
        file_path = self.base_path / session_id / filename
        return file_path if file_path.exists() else None
    
    def list_files(self, session_id: str) -> List[str]:
        """Listet alle Dateien in einer Session."""
        session_dir = self.base_path / session_id
        if not session_dir.exists():
            return []
        return [f.name for f in session_dir.iterdir() if f.is_file()]
    
    def delete_session_files(self, session_id: str):
        """Löscht alle Dateien einer Session."""
        session_dir = self.base_path / session_id
        if session_dir.exists():
            shutil.rmtree(session_dir)
```

#### Schritt 3: Audio Service (Grundoperationen)
```python
# shared/services/audio_service.py
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import Tuple, List

class AudioService:
    """Basis-Service für Audio-Operationen (wiederverwendbar)."""
    
    def __init__(self, target_sr: int = 22050):
        self.target_sr = target_sr
    
    def load_audio(self, file_path: Path) -> Tuple[np.ndarray, int]:
        """Lädt eine Audio-Datei."""
        y, sr = librosa.load(str(file_path), sr=self.target_sr)
        return y, sr
    
    def save_audio(self, audio_data: np.ndarray, 
                   file_path: Path, sr: int = None):
        """Speichert Audio-Daten."""
        sr = sr or self.target_sr
        sf.write(str(file_path), audio_data, sr)
    
    def segment_audio(self, audio_data: np.ndarray, sr: int,
                     segment_length_sec: int = 8) -> List[np.ndarray]:
        """Segmentiert Audio in gleich große Teile."""
        segment_samples = segment_length_sec * sr
        num_segments = int(np.ceil(len(audio_data) / segment_samples))
        
        segments = []
        for i in range(num_segments):
            start = i * segment_samples
            end = min(start + segment_samples, len(audio_data))
            segment = audio_data[start:end]
            
            # Padding falls zu kurz
            if len(segment) < segment_samples:
                segment = np.pad(
                    segment, 
                    (0, segment_samples - len(segment)), 
                    mode='constant'
                )
            segments.append(segment)
        
        return segments
    
    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalisiert Audio-Lautstärke."""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val
        return audio_data
```

### 1.2 Backend: Plugin Interface definieren
**Ziel**: Abstrakte Basisklasse für alle Tools

```python
# plugins/base/plugin_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from flask import Blueprint

class MusicToolPlugin(ABC):
    """Abstract Base Class für alle Musik-Tool-Plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Eindeutiger Name des Tools."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Version des Tools."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Beschreibung des Tools."""
        pass
    
    @abstractmethod
    def get_blueprint(self) -> Blueprint:
        """Gibt Flask Blueprint mit allen Routes zurück."""
        pass
    
    @abstractmethod
    def initialize(self, app_context: Dict[str, Any]):
        """Initialisiert das Plugin mit App-Kontext (Services, Config)."""
        pass
    
    @abstractmethod
    def get_frontend_routes(self) -> List[str]:
        """Gibt Frontend-Route-Pfade zurück."""
        pass
    
    def get_dependencies(self) -> List[str]:
        """Optionale Abhängigkeiten zu anderen Plugins."""
        return []
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Optionales Config-Schema für Tool-spezifische Settings."""
        return {}
    
    def cleanup(self):
        """Aufräumen beim Shutdown."""
        pass
```

### 1.3 Backend: Plugin Manager
**Ziel**: Automatisches Laden und Verwalten von Plugins

```python
# plugins/base/plugin_manager.py
import importlib
import pkgutil
from typing import Dict, List
from pathlib import Path
import yaml

class PluginManager:
    """Verwaltet alle Tool-Plugins."""
    
    def __init__(self, plugins_dir: str, app_context: Dict):
        self.plugins_dir = Path(plugins_dir)
        self.app_context = app_context
        self._plugins: Dict[str, MusicToolPlugin] = {}
    
    def discover_plugins(self):
        """Findet und lädt alle verfügbaren Plugins."""
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                if item.name != 'base':  # Skip base module
                    self._load_plugin(item)
    
    def _load_plugin(self, plugin_dir: Path):
        """Lädt ein einzelnes Plugin."""
        config_file = plugin_dir / 'config.yaml'
        if not config_file.exists():
            return
        
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        # Plugin nur laden wenn aktiviert
        if not config.get('enabled', True):
            return
        
        plugin_module = plugin_dir.name
        try:
            # Import plugin.py aus dem Plugin-Ordner
            module = importlib.import_module(
                f'plugins.{plugin_module}.plugin'
            )
            
            # Hol die Plugin-Klasse
            plugin_class = getattr(module, config['class'])
            plugin_instance = plugin_class()
            
            # Initialisiere
            plugin_instance.initialize(self.app_context)
            
            # Registriere
            self._plugins[plugin_instance.name] = plugin_instance
            
            print(f"✅ Plugin geladen: {plugin_instance.name} v{plugin_instance.version}")
        
        except Exception as e:
            print(f"❌ Fehler beim Laden von {plugin_module}: {e}")
    
    def get_plugin(self, name: str) -> MusicToolPlugin:
        """Gibt ein Plugin nach Name zurück."""
        return self._plugins.get(name)
    
    def get_all_plugins(self) -> List[MusicToolPlugin]:
        """Gibt alle geladenen Plugins zurück."""
        return list(self._plugins.values())
    
    def register_blueprints(self, app):
        """Registriert alle Plugin-Blueprints bei Flask."""
        for plugin in self._plugins.values():
            blueprint = plugin.get_blueprint()
            app.register_blueprint(
                blueprint, 
                url_prefix=f'/api/tools/{plugin.name}'
            )
```

---

## 🚀 Phase 2: Plugin-Migration (Priorität: MITTEL)

### 2.1 Audio Feedback Tool als erstes Plugin migrieren

```python
# plugins/audio_feedback/plugin.py
from plugins.base.plugin_interface import MusicToolPlugin
from flask import Blueprint
from .routes import create_routes
from .service import AudioFeedbackService

class AudioFeedbackPlugin(MusicToolPlugin):
    """Audio Feedback Analyse Tool."""
    
    @property
    def name(self) -> str:
        return "audio-feedback"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Vergleicht Schüler- und Referenzaufnahmen"
    
    def initialize(self, app_context: Dict[str, Any]):
        """Initialisiert das Tool mit shared services."""
        self.session_service = app_context['session_service']
        self.storage_service = app_context['storage_service']
        self.audio_service = app_context['audio_service']
        
        # Tool-spezifischer Service
        self.feedback_service = AudioFeedbackService(
            self.audio_service,
            self.storage_service
        )
    
    def get_blueprint(self) -> Blueprint:
        """Erstellt Blueprint mit allen Routes."""
        return create_routes(self.feedback_service)
    
    def get_frontend_routes(self) -> List[str]:
        return [
            '/tools/audio-feedback/upload',
            '/tools/audio-feedback/recordings',
            '/tools/audio-feedback/language',
            '/tools/audio-feedback/instruments',
            '/tools/audio-feedback/personalization',
            '/tools/audio-feedback/prompt'
        ]
```

```yaml
# plugins/audio_feedback/config.yaml
enabled: true
class: AudioFeedbackPlugin
name: Audio Feedback Analyzer
description: Vergleicht Musikaufnahmen und gibt intelligentes Feedback

settings:
  max_file_size_mb: 100
  allowed_formats: [mp3, wav, mp4]
  segment_length_sec: 8
  default_sample_rate: 22050
  analysis_features:
    - tempo
    - pitch
    - dynamics
    - spectral_centroid
    - rhythm_stability
```

### 2.2 Routes extrahieren

```python
# plugins/audio_feedback/routes.py
from flask import Blueprint, request, jsonify

def create_routes(feedback_service) -> Blueprint:
    """Erstellt Blueprint mit allen Routes für Audio Feedback."""
    
    bp = Blueprint('audio_feedback', __name__)
    
    @bp.route('/upload', methods=['POST'])
    def upload_audio():
        """Upload von Referenz- und Schüler-Aufnahmen."""
        session_id = request.headers.get('X-Session-ID')
        
        # Validierung
        if not session_id:
            return jsonify({'error': 'Session ID fehlt'}), 400
        
        files = request.files
        if 'referenz' not in files or 'schueler' not in files:
            return jsonify({
                'error': 'Beide Dateien erforderlich'
            }), 400
        
        # Service nutzen
        result = feedback_service.upload_files(
            session_id,
            files['referenz'],
            files['schueler']
        )
        
        return jsonify(result)
    
    @bp.route('/analyze', methods=['POST'])
    def analyze_audio():
        """Startet die Audio-Analyse."""
        session_id = request.headers.get('X-Session-ID')
        data = request.json or {}
        
        result = feedback_service.analyze(
            session_id,
            language=data.get('language', 'english'),
            referenz_instrument=data.get('referenzInstrument'),
            schueler_instrument=data.get('schuelerInstrument'),
            personal_message=data.get('personalMessage'),
            prompt_type=data.get('prompt_type', 'contextual'),
            use_simple_language=data.get('use_simple_language', False)
        )
        
        return jsonify(result)
    
    return bp
```

---

## 🎨 Phase 3: Frontend-Refactoring (Priorität: MITTEL)

### 3.1 Tool-Selection Homepage

```jsx
// src/pages/HomePage.jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function HomePage() {
  const [tools, setTools] = useState([])
  const navigate = useNavigate()
  
  useEffect(() => {
    // Lade verfügbare Tools vom Backend
    fetch('/api/tools')
      .then(res => res.json())
      .then(data => setTools(data.tools))
  }, [])
  
  return (
    <div className="home-page">
      <h1>MuDiKo Musik-Übungstools</h1>
      <p>Wähle ein Tool aus:</p>
      
      <div className="tool-grid">
        {tools.map(tool => (
          <ToolCard 
            key={tool.name}
            name={tool.display_name}
            description={tool.description}
            icon={tool.icon}
            onClick={() => navigate(`/tools/${tool.name}`)}
          />
        ))}
      </div>
    </div>
  )
}
```

### 3.2 Shared Hooks

```javascript
// src/shared/hooks/useSession.js
import { useState, useEffect } from 'react'

export function useSession() {
  const [sessionId, setSessionId] = useState(null)
  
  useEffect(() => {
    // Prüfe ob Session existiert
    const stored = localStorage.getItem('sessionId')
    if (stored) {
      setSessionId(stored)
    } else {
      // Erstelle neue Session
      createSession()
    }
  }, [])
  
  const createSession = async () => {
    const response = await fetch('/api/session/start', {
      method: 'POST'
    })
    const data = await response.json()
    setSessionId(data.sessionId)
    localStorage.setItem('sessionId', data.sessionId)
  }
  
  const endSession = async () => {
    if (sessionId) {
      await fetch('/api/session/end', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId })
      })
      localStorage.removeItem('sessionId')
      setSessionId(null)
    }
  }
  
  return { sessionId, createSession, endSession }
}
```

```javascript
// src/shared/hooks/useAudioUpload.js
import { useState } from 'react'
import { useSession } from './useSession'

export function useAudioUpload(toolName) {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const { sessionId } = useSession()
  
  const upload = async (refFile, studentFile) => {
    setIsUploading(true)
    setUploadStatus(null)
    
    const formData = new FormData()
    formData.append('referenz', refFile)
    formData.append('schueler', studentFile)
    
    try {
      const response = await fetch(`/api/tools/${toolName}/upload`, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Session-ID': sessionId
        }
      })
      
      const result = await response.json()
      
      if (response.ok) {
        setUploadStatus({ type: 'success', message: 'Upload erfolgreich!' })
        return result
      } else {
        setUploadStatus({ type: 'error', message: result.error })
        return null
      }
    } catch (error) {
      setUploadStatus({ type: 'error', message: 'Verbindungsfehler' })
      return null
    } finally {
      setIsUploading(false)
    }
  }
  
  return { upload, isUploading, uploadStatus }
}
```

---

## 🔮 Phase 4: Neue Tools hinzufügen (Priorität: NIEDRIG)

### Beispiel: MIDI-Tool Plugin

```python
# plugins/midi_tool/plugin.py
from plugins.base.plugin_interface import MusicToolPlugin
from flask import Blueprint
from .service import MidiToolService

class MidiToolPlugin(MusicToolPlugin):
    """MIDI-Analyse und Feedback Tool."""
    
    @property
    def name(self) -> str:
        return "midi-tool"
    
    @property
    def version(self) -> str:
        return "0.1.0"
    
    @property
    def description(self) -> str:
        return "MIDI-Datei Analyse und Feedback"
    
    def initialize(self, app_context):
        self.session_service = app_context['session_service']
        self.storage_service = app_context['storage_service']
        self.midi_service = MidiToolService()
    
    def get_blueprint(self) -> Blueprint:
        bp = Blueprint('midi_tool', __name__)
        
        @bp.route('/upload', methods=['POST'])
        def upload_midi():
            # MIDI Upload Logik
            pass
        
        @bp.route('/analyze', methods=['POST'])
        def analyze_midi():
            # MIDI Analyse
            pass
        
        return bp
    
    def get_frontend_routes(self):
        return ['/tools/midi-tool']
```

```yaml
# plugins/midi_tool/config.yaml
enabled: false  # Noch nicht produktionsreif
class: MidiToolPlugin
name: MIDI Tool
description: Analysiert MIDI-Dateien

settings:
  max_file_size_mb: 10
  allowed_formats: [mid, midi]
```

**Aktivierung**: Einfach `enabled: true` in config.yaml setzen!

---

## 📋 Implementierungs-Roadmap

### Sprint 1 (2-3 Wochen): Core Refactoring
- [ ] Service Layer implementieren (SessionService, StorageService, AudioService)
- [ ] Models definieren (Session, AudioFile, AnalysisResult)
- [ ] Neue Ordnerstruktur anlegen
- [ ] Unit Tests für Services schreiben

### Sprint 2 (2 Wochen): Plugin System
- [ ] Plugin Interface (MusicToolPlugin) definieren
- [ ] Plugin Manager implementieren
- [ ] Config-System (YAML) einrichten
- [ ] Dokumentation schreiben

### Sprint 3 (2-3 Wochen): Audio Feedback Migration
- [ ] Audio Feedback als Plugin umbauen
- [ ] Routes extrahieren
- [ ] AudioFeedbackPipeline in Service integrieren
- [ ] Tests anpassen
- [ ] Alte main.py reduzieren

### Sprint 4 (1 Woche): Frontend Refactoring
- [ ] Tool-Auswahl Homepage erstellen
- [ ] Shared Hooks implementieren (useSession, useAudioUpload)
- [ ] React Router einrichten
- [ ] Tool-spezifische Ordner anlegen

### Sprint 5 (1 Woche): Testing & Deployment
- [ ] Integration Tests
- [ ] End-to-End Tests
- [ ] Docker Update
- [ ] Deployment-Dokumentation

### Zukünftig: Neue Tools
- [ ] MIDI Tool Plugin
- [ ] Rhythmus-Trainer Plugin
- [ ] Gehörbildungs-Tool Plugin
- [ ] Akkord-Erkennung Tool Plugin

---

## 🎯 Erwartete Verbesserungen

### Technische Vorteile
✅ **Skalierbarkeit**: Neue Tools ohne Core-Änderungen  
✅ **Wartbarkeit**: Klare Trennung, kleinere Dateien  
✅ **Testbarkeit**: Services isoliert testbar  
✅ **Wiederverwendbarkeit**: Shared Services für alle Tools  
✅ **Flexibilität**: Tools per Config aktivieren/deaktivieren  

### Code-Metriken (Ziel)
- **Durchschnittliche Dateigröße**: < 200 Zeilen
- **Coupling**: Niedrig (Abhängigkeiten nur zu Interfaces)
- **Cohesion**: Hoch (klare Verantwortlichkeiten)
- **Test-Coverage**: > 80%

### Entwickler-Erfahrung
✅ Neue Entwickler können Tools unabhängig entwickeln  
✅ Klare Struktur: Jeder weiß wo was hingehört  
✅ Plug & Play: Tool entwickeln, Config erstellen, fertig  
✅ Debugging: Kleinere, fokussierte Code-Einheiten  

---

## 📚 Best Practices für neue Tools

### 1. Tool-Entwicklung Checkliste
```markdown
- [ ] Plugin-Klasse von MusicToolPlugin ableiten
- [ ] config.yaml erstellen
- [ ] Service-Klasse für Business-Logik
- [ ] Routes Blueprint definieren
- [ ] Models für Tool-spezifische Daten
- [ ] Frontend-Seiten im tools/<name> Ordner
- [ ] Unit Tests schreiben
- [ ] README.md mit Tool-Dokumentation
```

### 2. Namenskonventionen
- **Plugin-Ordner**: `snake_case` (z.B. `midi_tool`)
- **Plugin-Klasse**: `PascalCase` + `Plugin` (z.B. `MidiToolPlugin`)
- **Service-Klasse**: `PascalCase` + `Service` (z.B. `MidiToolService`)
- **API-Prefix**: `/api/tools/<tool-name>/`

### 3. Dependency Injection
Immer Services über `app_context` injizieren:
```python
def initialize(self, app_context):
    self.session_service = app_context['session_service']
    self.storage_service = app_context['storage_service']
    self.audio_service = app_context['audio_service']
```

### 4. Error Handling
Konsistente Error-Responses:
```python
return jsonify({
    'success': False,
    'error': 'Fehlermeldung',
    'error_code': 'INVALID_FILE_FORMAT'
}), 400
```

---

## 🚨 Risiken & Mitigation

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Breaking Changes in bestehender API | Mittel | Hoch | Schrittweise Migration, API-Versioning |
| Performance durch Plugin-Overhead | Niedrig | Mittel | Lazy Loading, Benchmarking |
| Komplexität erhöht | Mittel | Mittel | Gute Dokumentation, Code-Reviews |
| Frontend-Backend Inkonsistenzen | Niedrig | Hoch | API-Contracts, Integration Tests |

---

## 📖 Weiterführende Ressourcen

- **Flask Plugin Systems**: [Flask Pluggable Views](https://flask.palletsprojects.com/en/2.3.x/views/)
- **Design Patterns**: *Design Patterns: Elements of Reusable Object-Oriented Software* (Gang of Four)
- **Clean Architecture**: *Clean Architecture* by Robert C. Martin
- **Python Best Practices**: [The Hitchhiker's Guide to Python](https://docs.python-guide.org/)

---

## 🎓 Zusammenfassung

Dieser Optimierungsplan transformiert Ihr Projekt von einer monolithischen Anwendung zu einer **modularen, plugin-basierten Tool-Bibliothek**. Die empfohlene Architektur ermöglicht:

1. **Schnelles Hinzufügen neuer Tools** ohne bestehenden Code zu ändern
2. **Klare Verantwortlichkeiten** durch Service Layer und Plugin Interface
3. **Wiederverwendbarkeit** durch Shared Services
4. **Skalierbarkeit** für zukünftige Anforderungen
5. **Wartbarkeit** durch kleinere, fokussierte Module

Die Implementierung kann schrittweise erfolgen, ohne die aktuelle Funktionalität zu gefährden. Beginnen Sie mit dem Service Layer Refactoring und migrieren Sie dann Tool für Tool in die Plugin-Architektur.

**Nächste Schritte**: 
1. Review dieses Plans mit Ihrem Team
2. Priorisierung der Sprints
3. Start mit Sprint 1 (Service Layer)

Viel Erfolg! 🚀
