# HTTPS Deployment Anleitung für music.ifib.eu

## ✅ Setup abgeschlossen

Die folgenden Dateien wurden erstellt/aktualisiert:
- `Caddyfile` - Caddy Reverse Proxy Konfiguration mit automatischem HTTPS
- `docker-compose.yml` - Integrierter Caddy Service mit SSL-Zertifikat Volumes
- `deploy.ps1` - Aktualisiertes Deployment-Script mit Pre-Checks

## 📋 Deployment Checkliste

### Vor dem Deployment auf dem Server:

1. **DNS-Eintrag prüfen**
   ```bash
   # Prüfen ob music.ifib.eu auf die richtige IP zeigt
   nslookup music.ifib.eu
   ```

2. **Firewall-Ports öffnen** (auf dem Linux-Server)
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw status
   ```

3. **Prüfen ob Port 80/443 frei sind**
   ```bash
   # Wenn nginx oder apache läuft, stoppen:
   sudo systemctl stop nginx
   sudo systemctl disable nginx
   # oder
   sudo systemctl stop apache2
   sudo systemctl disable apache2
   ```

### Deployment durchführen:

```bash
# Auf dem Server
cd /pfad/zu/MuDiKo_KI_Assistant

# Repository aktualisieren
git pull

# Services neu starten
docker-compose down
docker-compose up -d

# Logs überwachen (Caddy holt SSL-Zertifikat)
docker-compose logs -f caddy
```

## 🔍 Nach dem Deployment

### Status prüfen:
```bash
# Services Status
docker-compose ps

# Caddy Logs
docker-compose logs caddy

# SSL-Zertifikat Status
docker exec mudiko-caddy caddy list-certificates
```

### Testen:
1. Öffne im Browser: `https://music.ifib.eu`
2. Prüfe SSL-Zertifikat (sollte von Let's Encrypt sein)
3. HTTP sollte automatisch zu HTTPS umleiten

## 🚀 Was passiert automatisch:

1. **Caddy startet** und liest die Domain `music.ifib.eu` aus dem Caddyfile
2. **Kontaktiert Let's Encrypt** über Port 80 (HTTP Challenge)
3. **Holt SSL-Zertifikat** für `music.ifib.eu`
4. **Startet HTTPS** auf Port 443
5. **Leitet HTTP → HTTPS** um (Port 80 → 443)
6. **Erneuert Zertifikate** automatisch vor Ablauf (alle 60 Tage)

## 🔧 Nützliche Befehle:

```bash
# Alle Services neu starten
docker-compose restart

# Nur Caddy neu starten
docker-compose restart caddy

# Caddy Konfiguration neu laden (ohne Neustart)
docker exec mudiko-caddy caddy reload --config /etc/caddy/Caddyfile

# Access Logs anzeigen
docker exec mudiko-caddy cat /data/access.log

# SSL-Zertifikat manuell erneuern (normalerweise nicht nötig)
docker exec mudiko-caddy caddy renew

# Services stoppen und Volumes entfernen
docker-compose down -v
```

## ⚠️ Troubleshooting

### Problem: SSL-Zertifikat wird nicht geholt
```bash
# Logs prüfen
docker-compose logs caddy

# Häufige Ursachen:
# 1. DNS zeigt nicht auf den Server
# 2. Port 80 ist blockiert (Firewall)
# 3. Anderer Webserver läuft auf Port 80
```

### Problem: "Connection refused" beim Zugriff
```bash
# Prüfen ob alle Services laufen
docker-compose ps

# Backend/Frontend Logs prüfen
docker-compose logs backend
docker-compose logs frontend
```

## 📊 Port-Übersicht

| Service  | Interner Port | Externer Port | Zugriff                    |
|----------|---------------|---------------|----------------------------|
| Backend  | 5000          | -             | Nur intern via Caddy       |
| Frontend | 80            | -             | Nur intern via Caddy       |
| Caddy    | 80, 443       | 80, 443       | Öffentlich (HTTPS)         |

## 🔐 Sicherheit

- ✅ Automatische SSL-Zertifikate von Let's Encrypt
- ✅ Automatische HTTP zu HTTPS Umleitung
- ✅ Security Headers (X-Frame-Options, X-XSS-Protection, etc.)
- ✅ Backend und Frontend nur intern erreichbar
- ✅ 100MB Upload-Limit für Audio-Dateien
- ✅ Request-Logging in JSON-Format

## 📝 Hinweise

- Zertifikate werden in `caddy-data` Volume gespeichert (persistent)
- Logs werden in `caddy-logs` Volume gespeichert
- Bei `docker-compose down -v` werden Zertifikate gelöscht
- Caddy erneuert Zertifikate automatisch 30 Tage vor Ablauf
