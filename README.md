# 🎵 MuDiKo KI Assistant

**Intelligenter Audio-Feedback-Assistent für die Musikpädagogik**

Ein webbasiertes System zur automatisierten Analyse und Bewertung von Musikaufnahmen mit KI-Unterstützung für den Bildungsbereich.

---

## 🚀 Schnellstart

### Docker (Empfohlen)
```bash
git clone https://github.com/hparkifib/MuDiKo_KI_Assistant.git
cd MuDiKo_KI_Assistant
docker-compose up -d
```
**➜ Anwendung öffnen:** http://localhost

### Development (Lokal)
```bash
# Backend starten
cd Backend/app && python main.py

# Frontend starten (neues Terminal)
cd Frontend && npm install && npm run dev
```
**➜ Anwendung öffnen:** http://localhost:5173

---

## 📖 Dokumentation

| Zielgruppe | Anleitung | Beschreibung |
|------------|-----------|--------------|
| **Einsteiger** | [🖥️ Windows Setup](docs/WINDOWS_SETUP.md) | Schritt-für-Schritt für Windows-Nutzer |
| **Entwickler** | [⚙️ Development Setup](docs/DEVELOPMENT.md) | Lokale Entwicklungsumgebung |
| **Server-Admin** | [� Server Deployment](docs/SERVER_DEPLOYMENT.md) | Produktions-Setup für Linux-Server |

---

## 🎯 Funktionen

- **🎼 Audio-Upload**: Unterstützung für MP3, WAV, MP4 Dateien
- **🤖 KI-Analyse**: Intelligente Bewertung mit OpenAI Integration
- **📊 Feedback-System**: Detaillierte Verbesserungsvorschläge
- **🎨 Responsive UI**: Moderne, benutzerfreundliche Oberfläche
- **🌐 Web-basiert**: Plattformunabhängig über Browser
- **🐳 Container-Ready**: Docker für einfache Bereitstellung

---

## 🏗️ Architektur

```
MuDiKo KI Assistant
├── Frontend/          # React + Vite Web-Interface
│   ├── src/          # React Komponenten
│   ├── public/       # Statische Assets
│   └── Dockerfile    # Container-Konfiguration
├── Backend/          # Flask API + Audio Processing
│   ├── app/          # Python Anwendung
│   └── Dockerfile    # Container-Konfiguration
├── docs/             # Dokumentation
└── docker-compose.yml # Container-Orchestrierung
```

---

## 🔧 Technologien

**Frontend:**
- React 18 mit Vite Build-System
- CSS Variables für Theming
- Responsive Design für alle Geräte

**Backend:**
- Flask (Python) REST API
- Audio-Verarbeitung mit librosa
- OpenAI GPT Integration
- File Upload Management

**Deployment:**
- Docker & Docker Compose
- Nginx Reverse Proxy
- Health Check Monitoring

---

## � System-Anforderungen

### Minimum (Docker)
- 4GB RAM
- 2GB freier Speicherplatz
- Docker Desktop oder Docker Engine

### Development
- Python 3.11+
- Node.js 18+
- Git

---

## 🎓 Verwendung

1. **Audio-Upload**: Referenz- und Schüleraufnahme hochladen
2. **Konfiguration**: Sprache, Instrument und Feedback-Präferenzen einstellen
3. **KI-Analyse**: Automatische Bewertung der Musikdateien
4. **Feedback**: Detaillierte Verbesserungsvorschläge erhalten

---

## 📊 Status

- ✅ **Frontend**: Vollständig implementiert
- ✅ **Backend**: Audio-Processing + REST API
- ✅ **Docker**: Produktionsbereit
- ✅ **Documentation**: Umfassende Anleitungen
- ✅ **Testing**: Upload und API funktionsfähig

---

## 🤝 Mitwirken

Dieses Projekt wurde im Rahmen der Musikpädagogik entwickelt. Für Verbesserungsvorschläge oder Fragen:

1. Issues über GitHub erstellen
2. Pull Requests für Verbesserungen
3. Dokumentation bei Bedarf erweitern

---

## 📞 Support

### Schnellhilfe
```bash
# Status prüfen
docker-compose ps

# Logs anzeigen
docker-compose logs

# Neustart
docker-compose restart
```

### Häufige Probleme
- **Port-Konflikte**: `docker-compose down && docker-compose up -d`
- **Build-Fehler**: `docker-compose build --no-cache`
- **Asset-Probleme**: Bereits in Docker-Setup gelöst

---

**🎵 Bereit für den Einsatz in der Musikpädagogik!**