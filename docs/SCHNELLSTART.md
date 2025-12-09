# 🚀 Schnellstart - Neue Architektur verwenden

## ✅ Phase 1 ist abgeschlossen!

Die neue modulare, plugin-basierte Architektur ist implementiert und funktioniert.

## 🎯 Was wurde erreicht?

- ✅ Service Layer (Session, Storage, Audio)
- ✅ Plugin System (Interface + Manager)
- ✅ Neue main.py (nur 9 Zeilen!)
- ✅ Config-System mit YAML
- ✅ Automatisches Session-Management

## 🏃 Starten der neuen App

### Variante 1: Direkt aus Backend-Ordner
```powershell
cd Backend
python -c "import sys; sys.path.insert(0, '.'); from app.main_NEW import app; app.run(host='0.0.0.0', port=5000)"
```

### Variante 2: Als Python-Modul (nach finalem Setup)
```powershell
cd Backend
python -m app.main_NEW
```

## 🧪 Testen der API

### Health Check
```powershell
curl http://localhost:5000/api/health
```

Erwartete Antwort:
```json
{
  "status": "ok",
  "message": "MuDiKo API is running",
  "plugins": 0,
  "active_sessions": 0
}
```

### Liste aller Tools
```powershell
curl http://localhost:5000/api/tools
```

### Session starten
```powershell
curl -X POST http://localhost:5000/api/session/start
```

Erwartete Antwort:
```json
{
  "success": true,
  "sessionId": "abc123...",
  "ttl": 3600
}
```

## 📦 Nächste Schritte

### 1. Audio Feedback Plugin aktivieren

Öffne: `Backend/app/plugins/audio_feedback/config.yaml`

Ändere:
```yaml
enabled: false  # ← Auf true setzen
```

Zu:
```yaml
enabled: true
```

### 2. Plugin vollständig implementieren

Das Plugin ist aktuell nur ein Placeholder. Um es vollständig zu implementieren:

1. Erstelle `audio_feedback/service.py` (Business Logic)
2. Erstelle `audio_feedback/routes.py` (API Endpoints)
3. Migriere Code aus `AudioFeedbackPipeline.py`
4. Aktualisiere `audio_feedback/plugin.py`

### 3. Alte main.py ersetzen (optional)

Wenn alles funktioniert:
```powershell
cd Backend\app
# Backup erstellen (bereits als main_OLD_BACKUP.py vorhanden)
# Neue Version aktivieren
Copy-Item main_NEW.py main.py -Force
```

## 🔧 Entwicklung neuer Tools

### Tool-Plugin erstellen

1. **Ordner erstellen:**
```powershell
mkdir Backend\app\plugins\mein_tool
```

2. **config.yaml erstellen:**
```yaml
enabled: true
class: MeinToolPlugin
display_name: Mein Tool
description: Beschreibung meines Tools
version: 0.1.0

settings:
  # Tool-spezifische Einstellungen
```

3. **plugin.py erstellen:**
```python
from flask import Blueprint, jsonify
from app.plugins.base.plugin_interface import MusicToolPlugin

class MeinToolPlugin(MusicToolPlugin):
    @property
    def name(self) -> str:
        return "mein-tool"
    
    @property
    def version(self) -> str:
        return "0.1.0"
    
    @property
    def display_name(self) -> str:
        return "Mein Tool"
    
    @property
    def description(self) -> str:
        return "Beschreibung"
    
    def initialize(self, app_context):
        self.session_service = app_context['session_service']
        self.storage_service = app_context['storage_service']
        self.audio_service = app_context['audio_service']
    
    def get_blueprint(self) -> Blueprint:
        bp = Blueprint('mein_tool', __name__)
        
        @bp.route('/test')
        def test():
            return jsonify({"message": "Mein Tool funktioniert!"})
        
        return bp
    
    def get_frontend_routes(self):
        return ['/tools/mein-tool']
```

4. **Neustart und testen:**
```powershell
# App neustarten
# Tool wird automatisch geladen!

# Testen:
curl http://localhost:5000/api/tools
curl http://localhost:5000/api/tools/mein-tool/test
```

## 🎓 Services verwenden

### Session Service
```python
def initialize(self, app_context):
    self.session_service = app_context['session_service']

# Im Endpoint
session = self.session_service.get_session(session_id)
session.set_data('key', 'value')
value = session.get_data('key')
```

### Storage Service
```python
def initialize(self, app_context):
    self.storage_service = app_context['storage_service']

# Im Endpoint
file_path = self.storage_service.save_file(
    file=request.files['audio'],
    session_id=session_id,
    role='referenz'  # oder filename='meinefile.mp3'
)

files = self.storage_service.list_files(session_id)
```

### Audio Service
```python
def initialize(self, app_context):
    self.audio_service = app_context['audio_service']

# Im Service
audio_data, sr = self.audio_service.load_audio(file_path)
segments = self.audio_service.segment_audio(audio_data, sr, segment_length_sec=8)
```

## 📚 Dokumentation

- **Architektur-Plan**: `docs/ARCHITECTURE_OPTIMIZATION_PLAN.md`
- **Quick Start Guide**: `docs/QUICK_START_REFACTORING.md`
- **Status Report**: `docs/PHASE1_STATUS_REPORT.md`
- **Diese Datei**: `docs/SCHNELLSTART.md`

## 🐛 Troubleshooting

### Import-Fehler
Stelle sicher, dass alle Imports mit `app.` beginnen:
```python
from app.core.config import get_config  # ✅
from .config import get_config           # ❌
```

### Plugin wird nicht geladen
Prüfe:
1. `config.yaml` existiert im Plugin-Ordner
2. `enabled: true` in config.yaml
3. `class` in config.yaml entspricht Klassennamen
4. `plugin.py` existiert mit korrekter Klasse

### Session-Fehler
```python
try:
    session = session_service.get_session(session_id)
except SessionNotFoundException:
    # Session existiert nicht
    pass
except SessionExpiredException:
    # Session ist abgelaufen
    pass
```

## 💡 Tipps

1. **Logging statt Print**: Später Logger implementieren
2. **Validierung**: Input-Validierung in Services
3. **Tests**: Unit Tests für Services schreiben
4. **Dokumentation**: Docstrings pflegen
5. **Type Hints**: Überall verwenden

## 🎉 Viel Erfolg!

Die neue Architektur ist bereit für Ihre Tool-Bibliothek!

Bei Fragen: Siehe Dokumentation in `docs/`
