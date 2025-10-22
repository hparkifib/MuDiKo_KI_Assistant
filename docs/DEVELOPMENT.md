# ⚙️ Development Setup

Anleitung für Entwickler zur lokalen Einrichtung der MuDiKo KI Assistant Entwicklungsumgebung.

---

## 🔧 Voraussetzungen

### Required Software
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)

### Optional (für Docker-Development)
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop)

---

## 📥 Repository Setup

### 1. Repository klonen
```bash
git clone https://github.com/hparkifib/MuDiKo_KI_Assistant.git
cd MuDiKo_KI_Assistant
```

### 2. Environment-Variablen konfigurieren
```bash
# .env-Datei erstellen
cp .env.example .env

# OpenAI API Key eintragen (optional)
nano .env
```

---

## 🐍 Backend Development

### 1. Python Virtual Environment
```bash
cd Backend

# Virtual Environment erstellen
python -m venv venv

# Aktivieren
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 3. Backend starten
```bash
cd app
python main.py
```

✅ **Backend läuft auf:** http://localhost:5000
✅ **API Health Check:** http://localhost:5000/api/health

### 4. Backend Testing
```bash
# API testen
curl http://localhost:5000/api/health

# Upload-Endpoint testen
curl -X POST http://localhost:5000/api/upload-audio \
  -F "referenz=@test.mp3" \
  -F "schueler=@test2.mp3"
```

---

## ⚛️ Frontend Development

### 1. Dependencies installieren
```bash
cd Frontend
npm install
```

### 2. Development Server starten
```bash
npm run dev
```

✅ **Frontend läuft auf:** http://localhost:5173 (oder 5174 wenn 5173 belegt)
✅ **API-Proxy aktiv:** Requests zu `/api/*` werden an Backend weitergeleitet

### 3. Frontend Building
```bash
# Production Build
npm run build

# Build-Vorschau
npm run preview
```

---

## 🐳 Docker Development

### 1. Einzelne Services
```bash
# Nur Backend
docker-compose up backend

# Nur Frontend
docker-compose up frontend
```

### 2. Development mit Live-Reload
```bash
# Backend mit Volume-Mounting für Live-Reload
docker-compose -f docker-compose.dev.yml up
```

### 3. Production-ähnliches Testing
```bash
# Komplettes System
docker-compose up -d

# Logs verfolgen
docker-compose logs -f
```

---

## 📁 Projektstruktur (Development)

```
MuDiKo_KI_Assistant/
├── Backend/
│   ├── app/
│   │   ├── main.py              # Flask Application Entry
│   │   ├── AudioManager.py      # Audio File Handling
│   │   └── AudioFeedbackPipeline.py # AI Processing
│   ├── requirements.txt         # Python Dependencies
│   ├── Dockerfile              # Container Config
│   └── uploads/                # Audio Files Storage
├── Frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React Component
│   │   ├── AudioUpload_Page.jsx # Upload Interface
│   │   ├── PromptPage.jsx      # Feedback Display
│   │   └── [other components]  # Additional Pages
│   ├── public/                 # Static Assets
│   ├── package.json           # Node Dependencies
│   ├── vite.config.js         # Build Configuration
│   └── Dockerfile             # Container Config
├── docs/                      # Documentation
├── docker-compose.yml         # Container Orchestration
├── .env.example              # Environment Template
└── README.md                 # Project Overview
```

---

## 🔄 Development Workflow

### 1. Feature Development
```bash
# Neuen Branch erstellen
git checkout -b feature/neue-funktion

# Backend Änderungen - Auto-Reload aktiv
cd Backend/app
python main.py

# Frontend Änderungen - HMR aktiv
cd Frontend
npm run dev
```

### 2. Testing
```bash
# Backend Tests
cd Backend
python -m pytest

# Frontend Tests (falls implementiert)
cd Frontend
npm test
```

### 3. Docker Testing
```bash
# Lokale Images bauen
docker-compose build

# Funktionalität testen
docker-compose up -d
curl http://localhost/api/health
```

---

## 🐛 Debugging

### Backend Debugging
```python
# In main.py Debug-Modus aktivieren
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Frontend Debugging
```bash
# Browser DevTools verwenden
# React DevTools Extension installieren
# Vite gibt detaillierte Fehlermeldungen aus
```

### Docker Debugging
```bash
# Container-Logs
docker-compose logs backend
docker-compose logs frontend

# In Container einsteigen
docker exec -it mudiko-backend bash
docker exec -it mudiko-frontend sh
```

---

## 🚀 Performance Optimization

### Backend
- **Caching**: Redis für API-Responses implementieren
- **Async Processing**: Celery für Audio-Verarbeitung
- **Database**: PostgreSQL für Metadaten

### Frontend
- **Bundle Analysis**: `npm run build -- --analyze`
- **Code Splitting**: React.lazy() für große Komponenten
- **Image Optimization**: WebP für Assets

---

## 📦 Dependency Management

### Python (Backend)
```bash
# Neue Dependencies hinzufügen
pip install neue-bibliothek
pip freeze > requirements.txt

# Dependencies updaten
pip install -r requirements.txt --upgrade
```

### Node.js (Frontend)
```bash
# Neue Dependencies hinzufügen
npm install neue-bibliothek

# Dev Dependencies
npm install -D entwicklungs-tool

# Dependencies updaten
npm update
```

---

## 🔍 Code Quality

### Linting & Formatting
```bash
# Python (Backend)
pip install black flake8
black app/
flake8 app/

# JavaScript (Frontend)
npm run lint
npm run format
```

### Pre-commit Hooks
```bash
# Pre-commit installieren
pip install pre-commit
pre-commit install

# Hooks konfigurieren in .pre-commit-config.yaml
```

---

## 📊 Monitoring & Logging

### Development Logging
```python
# Backend Logging Setup
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks
```bash
# Backend Health
curl http://localhost:5000/api/health

# Frontend Health
curl http://localhost:5173

# Docker Health
docker-compose ps
```

---

## 🤝 Contributing Guidelines

### Code Style
- **Python**: PEP 8, Black Formatting
- **JavaScript**: ESLint + Prettier
- **Commits**: Conventional Commits Format

### Branch Strategy
```bash
main           # Production-ready code
develop        # Integration branch
feature/*      # Feature development
hotfix/*       # Critical fixes
```

### Pull Request Process
1. Feature Branch erstellen
2. Änderungen implementieren
3. Tests hinzufügen/updaten
4. Docker Build testen
5. Pull Request erstellen

---

## 📞 Development Support

### Häufige Probleme

#### "Module not found" (Python)
```bash
# Virtual Environment aktivieren
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dependencies neu installieren
pip install -r requirements.txt
```

#### "npm install fails"
```bash
# Node Version prüfen
node --version  # Sollte 18+ sein

# Cache leeren
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### "API Calls fail"
- **Development**: Vite-Proxy überprüfen (vite.config.js)
- **Docker**: nginx-Konfiguration prüfen
- **CORS**: Backend CORS-Settings überprüfen

### Debug Commands
```bash
# Umfassende Systemprüfung
python --version
node --version
npm --version
docker --version
docker-compose --version

# Port-Konflikte prüfen
netstat -tulpn | grep :5000
netstat -tulpn | grep :5173
```

**Happy Coding! 🎵**