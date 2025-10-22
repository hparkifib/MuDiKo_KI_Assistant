# 🎵 MuDiKo KI Assistant

**Webbasierte Audio-Upload-Anwendung für die Musikpädagogik**

Ein einfaches System zum Hochladen und Verwalten von Musikaufnahmen mit moderner Web-Oberfläche und Audio-Verarbeitung.

---

## 🚀 Einfacher Start

### Option 1: Mit Docker (Empfohlen - Alles automatisch)
```powershell
# Projekt herunterladen
git clone https://github.com/hparkifib/MuDiKo_KI_Assistant.git
cd MuDiKo_KI_Assistant

# Alles starten (dauert beim ersten Mal etwas länger)
docker-compose up -d
```
**➜ Dann öffnen:** http://localhost

### Option 2: Lokal entwickeln (Für Programmierer)
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

---

## 🎯 Was kann die Anwendung?

### Grundfunktionen
- **🎼 Audio-Dateien hochladen**: MP3, WAV und MP4 Dateien unterstützt
- **📁 Datei-Verwaltung**: Hochgeladene Dateien sicher speichern
- **🎨 Moderne Oberfläche**: Einfach zu bedienen auf Computer und Tablet
- **🌐 Web-basiert**: Läuft im Browser - keine Installation nötig
- **📱 Responsive**: Funktioniert auf verschiedenen Bildschirmgrößen

### Für Musikpädagogik gedacht
- **👨‍🏫 Lehrkräfte**: Schüleraufnahmen einfach sammeln
- **👨‍🎓 Schüler**: Eigene Aufnahmen unkompliziert hochladen  
- **🏫 Schulen**: Zentrale Plattform für Audio-Material
- **🎼 Instrumente**: Alle Instrumente - Klavier, Gitarre, Gesang, etc.

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
- **Audio-Bibliotheken**: Für das Verarbeiten von Musikdateien

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

---

## 🎓 Wie benutze ich es?

### Schritt-für-Schritt
1. **Anwendung öffnen**: http://localhost im Browser
2. **Audio-Datei auswählen**: MP3, WAV oder MP4 von Computer auswählen
3. **Hochladen**: Auf "Upload" klicken und warten
4. **Bestätigung**: Erfolgsmeldung erscheint wenn fertig
5. **Wiederholen**: Weitere Dateien hochladen nach Bedarf

### Tipps für die Nutzung
- **Datei-Größe**: Bis zu 50MB pro Datei möglich
- **Dateiformate**: .mp3, .wav, .mp4 funktionieren am besten
- **Internet**: Stabiles WLAN für größere Dateien empfohlen
- **Browser**: Chrome, Firefox, Safari oder Edge verwenden

---

## 📊 Aktueller Stand

- ✅ **Web-Oberfläche**: Komplett fertig und getestet
- ✅ **Audio-Upload**: Funktioniert mit allen gängigen Formaten
- ✅ **Server-API**: Läuft stabil und sicher
- ✅ **Docker-Setup**: Einfache Installation möglich
- ✅ **Anleitungen**: Umfassende Dokumentation vorhanden
- 🔄 **KI-Features**: Vorbereitung für zukünftige Erweiterungen

---

## 🛠️ Hilfe bei Problemen

### Schnelle Lösungen
```powershell
# Alles neustarten
docker-compose restart

# Status der Container prüfen  
docker-compose ps

# Fehlermeldungen anschauen
docker-compose logs
```

### Häufige Probleme
- **"Port bereits belegt"**: Anderen Browser-Tab schließen oder Computer neustarten
- **"Docker-Fehler"**: Docker Desktop neustarten
- **"Seite lädt nicht"**: 1-2 Minuten warten, Container brauchen Zeit zum Starten
- **"Upload funktioniert nicht"**: Backend-Logs mit `docker-compose logs backend` prüfen

### Wo finde ich mehr Hilfe?
- [Windows-Anleitung](docs/WINDOWS_SETUP.md) für detaillierte Schritte
- [Entwickler-Guide](docs/DEVELOPMENT.md) für technische Probleme
- GitHub Issues für Fehler-Meldungen

---

**🎵 Einfach Musik hochladen und verwalten!**