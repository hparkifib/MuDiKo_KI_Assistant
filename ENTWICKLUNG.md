# MuDiKo KI Assistant - Entwicklungsumgebungen

## 🚀 Schnellstart

### Lokale Entwicklung mit Docker (empfohlen für Development)
```powershell
# Starten
docker compose -f docker-compose.dev.yml up -d

# App nutzen
# Frontend: http://localhost:3000
# Backend:  http://localhost:5000

# Stoppen
docker compose -f docker-compose.dev.yml down
```

### Produktions-Deployment mit HTTPS
```powershell
# Starten
docker compose up -d

# App nutzen über Caddy (HTTPS)
# https://deine-domain.de

# Stoppen
docker compose down
```

## 📋 Übersicht der Konfigurationen

### `docker-compose.dev.yml` - Lokale Entwicklung
✅ **Vorteile:**
- Direkter Zugriff auf Frontend (Port 3000) und Backend (Port 5000)
- Hot-Reload für Frontend und Backend
- Volume-Mounts für Live-Code-Änderungen
- Kein HTTPS/SSL nötig
- Schnelles Iterieren

**Verwendung:**
- Tägliche Entwicklung
- Testing
- Debugging
- Lokales Arbeiten

### `docker-compose.yml` - Produktion
✅ **Vorteile:**
- Automatisches HTTPS via Caddy
- Reverse Proxy
- Optimierte Production Builds
- SSL-Zertifikate
- Health Checks

**Verwendung:**
- Server-Deployment
- Produktions-Umgebung
- Öffentlicher Zugriff

## 🔧 Entwicklungs-Workflow

1. **Lokale Änderungen machen:**
   ```powershell
   docker compose -f docker-compose.dev.yml up -d
   # Ändere Code in ./Backend/app oder ./Frontend/src
   # Änderungen werden automatisch geladen
   ```

2. **Testen:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api/health

3. **Auf Server deployen:**
   ```powershell
   # Code committen
   git add .
   git commit -m "Deine Änderungen"
   git push

   # Auf Server
   docker compose down
   docker compose build
   docker compose up -d
   ```

## 📁 Dateien-Übersicht

```
MuDiKo_KI_Assistant/
├── docker-compose.yml          # Produktion (mit Caddy/HTTPS)
├── docker-compose.dev.yml      # Entwicklung (ohne Caddy)
├── Frontend/
│   ├── Dockerfile              # Production Build (nginx)
│   └── Dockerfile.dev          # Development (Vite dev server)
└── Backend/
    └── Dockerfile              # Für beide Umgebungen
```

## 🔄 Port-Übersicht

### Development (`docker-compose.dev.yml`)
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`

### Produktion (`docker-compose.yml`)
- Alles über Caddy: `https://deine-domain.de`
- HTTP (Port 80): Automatischer Redirect zu HTTPS
- HTTPS (Port 443): Hauptzugang

## 💡 Tipps

**Bei Problemen mit Dev-Setup:**
```powershell
# Container neu bauen
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.dev.yml up -d

# Logs checken
docker compose -f docker-compose.dev.yml logs -f
```

**Zwischen Umgebungen wechseln:**
```powershell
# Von Dev zu Prod
docker compose -f docker-compose.dev.yml down
docker compose up -d

# Von Prod zu Dev
docker compose down
docker compose -f docker-compose.dev.yml up -d
```
