# 🖥️ MuDiKo KI Assistant - Windows Setup für Einsteiger

## Schritt-für-Schritt Anleitung für Windows-Benutzer

### Was Sie benötigen
- Windows 10/11 Computer
- Internetverbindung
- Etwa 30 Minuten Zeit

---

## 🔧 Schritt 1: Docker Desktop installieren

### 1.1 Docker Desktop herunterladen
- Gehen Sie zu: https://www.docker.com/products/docker-desktop
- Klicken Sie auf "Download for Windows"
- Starten Sie die heruntergeladene Datei

### 1.2 Docker Desktop installieren
- Folgen Sie dem Installationsassistenten
- ✅ **Wichtig**: Aktivieren Sie "Use WSL 2 instead of Hyper-V"
- Neustart des Computers erforderlich

### 1.3 Docker Desktop starten
- Öffnen Sie Docker Desktop
- Warten Sie, bis "Docker Desktop is running" angezeigt wird
- Das Docker-Symbol sollte in der Taskleiste erscheinen

---

## 📥 Schritt 2: MuDiKo herunterladen

### 2.1 ZIP-Datei herunterladen
- Gehen Sie zu: https://github.com/hparkifib/MuDiKo_KI_Assistant
- Klicken Sie auf den grünen "Code" Button
- Wählen Sie "Download ZIP"

### 2.2 Entpacken
- Rechtsklick auf die ZIP-Datei
- "Alle extrahieren..." wählen
- Entpacken Sie nach `C:\MuDiKo` (oder einen Ordner Ihrer Wahl)

---

## 🚀 Schritt 3: MuDiKo starten

### 3.1 PowerShell öffnen
- Drücken Sie `Windows + R`
- Tippen Sie `powershell` und drücken Enter
- Ein blaues Terminal-Fenster öffnet sich

### 3.2 Zum MuDiKo-Ordner navigieren
```powershell
cd C:\MuDiKo\MuDiKo_KI_Assistant-main
```

### 3.3 MuDiKo starten
```powershell
docker-compose up -d
```

### 3.4 Warten
- Der erste Start dauert 5-10 Minuten
- Docker lädt alle benötigten Dateien herunter
- Sie sehen verschiedene Download-Fortschritte

---

## 🌐 Schritt 4: MuDiKo nutzen

### 4.1 Browser öffnen
- Öffnen Sie Ihren Webbrowser (Chrome, Edge, Firefox)
- Gehen Sie zu: http://localhost
- Die MuDiKo-Anwendung sollte erscheinen

### 4.2 Test durchführen
- Sie sollten das MuDiKo-Logo sehen
- Navigieren Sie durch die verschiedenen Seiten
- Testen Sie einen Audio-Upload

---

## ⚙️ Schritt 5: MuDiKo verwalten

### MuDiKo stoppen
```powershell
docker-compose down
```

### MuDiKo neustarten
```powershell
docker-compose restart
```

### Status prüfen
```powershell
docker-compose ps
```

---

## 📋 Tägliche Nutzung

### MuDiKo starten (nach Computer-Neustart)
1. Docker Desktop öffnen (wartet bis es läuft)
2. PowerShell öffnen (`Windows + R`, dann `powershell`)
3. Zum Ordner navigieren: `cd C:\MuDiKo\MuDiKo_KI_Assistant-main`
4. Starten: `docker-compose up -d`
5. Browser öffnen: http://localhost

### MuDiKo beenden
1. PowerShell öffnen
2. Zum Ordner navigieren: `cd C:\MuDiKo\MuDiKo_KI_Assistant-main`
3. Stoppen: `docker-compose down`
4. Docker Desktop schließen

---

## 🆘 Hilfe bei Problemen

### Problem: "Docker nicht gefunden"
**Lösung:**
- Docker Desktop neu starten
- Warten bis "Docker is running" angezeigt wird
- PowerShell neu öffnen

### Problem: "Port 80 bereits verwendet"
**Lösung:**
```powershell
docker-compose down
docker-compose up -d
```

### Problem: "Seite lädt nicht"
**Lösung:**
- Warten Sie 2-3 Minuten nach dem Start
- Browser-Seite aktualisieren (F5)
- Überprüfen: http://localhost/api/health

### Problem: "Sehr langsam"
**Ursachen:**
- Erster Start: Docker lädt Dateien herunter (normal)
- Wenig RAM: Schließen Sie andere Programme
- Antivirus: Docker Desktop zur Ausnahmeliste hinzufügen

---

## 🎯 Automatisches Starten (Optional)

### Autostart-Skript erstellen
1. Erstellen Sie eine neue Datei: `start_mudiko.bat`
2. Fügen Sie folgenden Inhalt ein:
```batch
@echo off
cd /d C:\MuDiKo\MuDiKo_KI_Assistant-main
docker-compose up -d
echo MuDiKo wird gestartet...
timeout /t 10
start http://localhost
```
3. Doppelklick auf die Datei startet MuDiKo automatisch

---

## ✅ Erfolgskontrolle

### Alles funktioniert, wenn:
- ✅ Docker Desktop läuft ohne Fehler
- ✅ http://localhost zeigt die MuDiKo-Startseite
- ✅ Das Logo wird korrekt angezeigt
- ✅ Sie können durch die Seiten navigieren
- ✅ Audio-Upload-Seite ist erreichbar

### Bei Problemen:
1. Computer neu starten
2. Docker Desktop neu installieren
3. Antivirus temporär deaktivieren
4. Als Administrator ausführen

---

## 📞 Weitere Hilfe

### Systemanforderungen prüfen
- Windows 10 Version 2004 oder höher
- 4 GB RAM (8 GB empfohlen)
- Hyper-V und WSL 2 Unterstützung

### Erweiterte Anleitung
- Siehe `SETUP_ANLEITUNG.md` für technische Details
- Siehe `README.md` für Entwickler-Informationen

**🎵 Viel Erfolg mit MuDiKo KI Assistant!**