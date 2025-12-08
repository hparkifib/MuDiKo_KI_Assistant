# 🎵 MuDiKo KI Assistant

**Webbasierte Audio-Upload-Anwendung für die Musikpädagogik**

Figma UX-Design: https://www.figma.com/design/TbnOyWdiYdRzgERlU6SzWU/Music-KI-Assistent?node-id=0-1&p=f&t=DLTMI83OCbv2EKoi-0


Die Software ermöglicht Schülerinnen und Schüler die Erstellung von Prompts, um ein personalisertes Feedback zu ihrer Musik von einem LLM generieren zu lassen. 

---

## 🚀 Einfacher Start

### Option 1: Mit Docker (Empfohlen - Alles automatisch)
```powershell
# Projekt herunterladen
git clone https://github.com/hparkifib/MuDiKo_KI_Assistant.git
cd MuDiKo_KI_Assistant

# Alles starten (dauert beim ersten Mal etwas länger)
docker-compose build
docker-compose up -d
```
**➜ Dann öffnen:** http://localhost

### Option 2: Lokal weiterentwickeln (Für Programmierer)
```powershell
# Backend starten (Terminal 1)
cd Backend\app
python main.py

# Frontend starten (Terminal 2) 
cd Frontend
npm install
npm run dev
```
**➜ Dann öffnen:** http://localhost:5173

---

## 📖 Hilfe und Anleitungen

| Für wen? | Anleitung | Was steht drin? |
|----------|-----------|-----------------|
| **Windows-Nutzer** | [🖥️ Windows Anleitung](docs/WINDOWS_SETUP.md) | Schritt-für-Schritt Installation |
| **Programmierer** | [⚙️ Entwickler-Setup](docs/DEVELOPMENT.md) | Code bearbeiten und erweitern |
| **Server-Betreiber** | [🔧 Server-Installation](docs/SERVER_DEPLOYMENT.md) | Auf eigenem Server installieren |

## 🚀 Deployment (Produktivbetrieb)

So bringst du die Anwendung sicher live (z. B. auf https://music.ifib.eu):

1) Umgebungsvariablen vorbereiten
	- Lege eine Datei `.env` neben `docker-compose.yml` an (siehe Vorlage `.env.example`).
	- Setze mindestens:
	  - `SECRET_KEY` (starker, geheimer Schlüssel)
	  - `CORS_ORIGINS` (deine HTTPS-Domain, z. B. https://music.ifib.eu)
	  - `SESSION_TTL_SECONDS` (z. B. 3600)
	  - `GC_INTERVAL_SECONDS` (z. B. 900)
	  - `MAX_CONTENT_LENGTH` (z. B. 104857600)

2) Container starten
	- Docker Compose im Projektordner ausführen:

```powershell
# Images bauen und Services starten
docker-compose build
docker-compose up -d

# Status prüfen
docker-compose ps

# Backend Healthcheck
curl http://localhost:5000/api/health
```

3) Reverse Proxy & HTTPS
	- Die Compose enthält einen Caddy‑Service für HTTPS mit automatischen Zertifikaten.
	- Passe bei Bedarf die `Caddyfile` an deine Domain an.

4) Funktionstest
	- Frontend öffnen (über deine Domain), Dateien hochladen, Wiedergabe testen.
	- Session beenden (z. B. Button „Neues Feedback“); temporäre Dateien werden gelöscht.

Hinweis
- Temporäre Daten werden streng pro Session unter `Backend/app/Uploads/<sessionId>` gespeichert und nach Session‑Ende bzw. Inaktivität automatisch entfernt.
- Der SECRET_KEY ist der Flask‑App‑Schlüssel und hat nichts mit OpenAI zu tun.

---

## 🎯 Was kann die Anwendung?

### Grundfunktionen
- **🎼 Audio-Dateien hochladen**: MP3, WAV und MP4 Dateien unterstützt
- **� Datenschutzfreundlich (DSGVO)**: Uploads werden nur temporär pro Session gespeichert und nach Sitzungsende gelöscht
- **📁 Datei-Verwaltung**: Session-basierte Trennung, parallele Nutzer werden isoliert
- **🌐 Web-basiert**: Läuft plattformunabhängig über Browser - keine Installation nötig
- **📱 Responsive**: Funktioniert auf verschiedenen Bildschirmgrößen
- **🐳 Container-Ready**: Docker für einfache Bereitstellung

---

## 🏗️ Wie ist es aufgebaut?

```
MuDiKo_KI_Assistant/
├── Frontend/                    # Web-Oberfläche (React)
│   ├── src/                    # Website-Code
│   │   ├── App.jsx             # Hauptanwendung
│   │   ├── AudioUpload_Page.jsx # Upload-Seite
│   │   └── [weitere Seiten]    # Andere Funktionen
│   ├── public/                 # Bilder und Symbole
│   └── Dockerfile              # Docker-Container für Website
│
├── Backend/                     # Server-Anwendung (Python)
│   ├── app/                    # Server-Code
│   │   ├── main.py             # Haupt-Server
│   │   ├── AudioManager.py     # Audio-Datei-Verwaltung
│   │   └── AudioFeedbackPipeline.py # Audio-Verarbeitung
│   └── Dockerfile              # Docker-Container für Server
│   
│   # Session-Speicher (zur Laufzeit)
│   # Backend/app/Uploads/<sessionId>/ → temporäre Dateien je Sitzung
│
├── docs/                       # Alle Anleitungen
└── docker-compose.yml          # Automatische Installation
```

---

## 🔧 Welche Technik steckt dahinter?

### Web-Oberfläche (Frontend)
- **React**: Moderne JavaScript-Bibliothek für Websites
- **Vite**: Schneller Build-Prozess für die Website
- **CSS**: Schönes Design mit modernen Farben und Layouts

### Server (Backend)  
- **Python**: Programmiersprache für den Server
- **Flask**: Web-Framework für Python APIs
- **Audio-Bibliotheken**: Librosa für das Verarbeiten von Musikdateien

### Installation und Betrieb
- **Docker**: Automatische Installation aller Komponenten
- **nginx**: Web-Server für die Auslieferung
- **Gesundheits-Checks**: Automatische Überwachung der Funktionen

---

## 📋 Was brauche ich?

### Für Docker (Einfach)
- **Computer**: Windows 10/11, Mac oder Linux
- **Arbeitsspeicher**: Mindestens 4GB RAM  
- **Festplatte**: 2GB freier Platz
- **Software**: Docker Desktop (kostenlos)

### Für Entwicklung (Erweitert)
- **Python**: Version 3.11 oder neuer
- **Node.js**: Version 18 oder neuer
- **Git**: Für das Herunterladen des Codes
