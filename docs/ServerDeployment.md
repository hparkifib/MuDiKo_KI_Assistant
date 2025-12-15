# 🌐 MuDiKo KI Assistant - Server Deployment Guide

## Produktions-Setup für Linux-Server

### Überblick
Diese Anleitung zeigt, wie Sie MuDiKo auf einem Linux-Server (Ubuntu/Debian) in Produktion betreiben.

---

## 🖥️ Server-Vorbereitung

### Minimum-Anforderungen
- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- 4GB RAM (8GB empfohlen)
- 20GB freier Speicherplatz
- Root-Zugriff oder sudo-Berechtigung

### Empfohlene VPS-Anbieter
- DigitalOcean (Droplet 4GB)
- AWS EC2 (t3.medium)
- Hetzner Cloud (CX21)
- Vultr (High Frequency 4GB)

---

## 🔧 System-Setup

### 1. Server aktualisieren
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install curl wget git nano htop -y
```

### 2. Docker installieren
```bash
# Docker Engine installieren
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Benutzer zur Docker-Gruppe hinzufügen
sudo usermod -aG docker $USER

# Docker Compose installieren
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Neustart für Gruppenmitgliedschaft
sudo reboot
```

### 3. Nach Neustart testen
```bash
docker --version
docker-compose --version
docker run hello-world
```

---

## 📥 MuDiKo Installation

### 1. Repository klonen
```bash
cd /opt
sudo git clone https://github.com/hparkifib/MuDiKo_KI_Assistant.git
sudo chown -R $USER:$USER MuDiKo_KI_Assistant
cd MuDiKo_KI_Assistant
```

### 2. Konfiguration anpassen
```bash
# Umgebungsvariablen setzen (optional)
cp .env.example .env
nano .env
```

### 3. MuDiKo starten
```bash
docker-compose up -d
```

### 4. Status prüfen
```bash
docker-compose ps
docker-compose logs
```

---

## 🔒 Sicherheit & Reverse Proxy

### 1. Nginx installieren
```bash
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 2. Nginx-Konfiguration
```bash
sudo nano /etc/nginx/sites-available/mudiko
```

Inhalt:
```nginx
server {
    listen 80;
    server_name ihre-domain.de www.ihre-domain.de;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=mudiko:10m rate=10r/s;
    limit_req zone=mudiko burst=20 nodelay;

    # Main Location
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Upload Size
        client_max_body_size 50M;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API Location (zusätzliche Sicherheit)
    location /api/ {
        proxy_pass http://localhost:80/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Größere Upload-Limits für Audio
        client_max_body_size 100M;
    }
}
```

### 3. Nginx aktivieren
```bash
sudo ln -s /etc/nginx/sites-available/mudiko /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔐 SSL-Zertifikat (Let's Encrypt)

### 1. Certbot installieren
```bash
sudo apt install snapd -y
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

### 2. SSL-Zertifikat erhalten
```bash
sudo certbot --nginx -d ihre-domain.de -d www.ihre-domain.de
```

### 3. Auto-Renewal testen
```bash
sudo certbot renew --dry-run
```

---

## 🚀 Systemd Service (Auto-Start)

### 1. Service-Datei erstellen
```bash
sudo nano /etc/systemd/system/mudiko.service
```

Inhalt:
```ini
[Unit]
Description=MuDiKo KI Assistant
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
User=root
WorkingDirectory=/opt/MuDiKo_KI_Assistant
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
ExecReload=/usr/local/bin/docker-compose restart
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
```

### 2. Service aktivieren
```bash
sudo systemctl daemon-reload
sudo systemctl enable mudiko.service
sudo systemctl start mudiko.service
sudo systemctl status mudiko.service
```

---

## 📊 Monitoring & Logging

### 1. Log-Rotation einrichten
```bash
sudo nano /etc/logrotate.d/mudiko
```

Inhalt:
```
/opt/MuDiKo_KI_Assistant/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
```

### 2. System-Monitoring
```bash
# Disk Space überwachen
df -h

# Memory Usage
free -h

# Docker Stats
docker stats

# MuDiKo Logs
docker-compose logs --tail=100
```

### 3. Health Check Script
```bash
nano /opt/health-check.sh
```

Inhalt:
```bash
#!/bin/bash
# MuDiKo Health Check

# API Test
if curl -f http://localhost/api/health > /dev/null 2>&1; then
    echo "$(date): MuDiKo API healthy"
else
    echo "$(date): MuDiKo API unhealthy - restarting"
    cd /opt/MuDiKo_KI_Assistant
    docker-compose restart
fi
```

```bash
chmod +x /opt/health-check.sh

# Crontab hinzufügen (alle 5 Minuten)
crontab -e
```

Crontab-Eintrag:
```
*/5 * * * * /opt/health-check.sh >> /var/log/mudiko-health.log 2>&1
```

---

## 🔄 Updates & Wartung

### 1. MuDiKo aktualisieren
```bash
cd /opt/MuDiKo_KI_Assistant
git pull origin main
docker-compose build --no-cache
docker-compose up -d
```

### 2. System-Updates
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### 3. Docker-Cleanup
```bash
# Ungenutzte Images entfernen
docker system prune -f

# Volumes bereinigen
docker volume prune -f
```

---

## 🔧 Backup-Strategie

### 1. Backup-Script
```bash
nano /opt/backup-mudiko.sh
```

Inhalt:
```bash
#!/bin/bash
BACKUP_DIR="/backup/mudiko"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Code-Backup
tar -czf $BACKUP_DIR/mudiko_code_$DATE.tar.gz /opt/MuDiKo_KI_Assistant

# Docker-Volumes Backup
docker run --rm -v mudiko_ki_assistant_uploads:/backup alpine tar czf - /backup > $BACKUP_DIR/uploads_$DATE.tar.gz

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### 2. Automatisches Backup
```bash
chmod +x /opt/backup-mudiko.sh

# Tägliches Backup um 2 Uhr
crontab -e
```

Crontab-Eintrag:
```
0 2 * * * /opt/backup-mudiko.sh >> /var/log/mudiko-backup.log 2>&1
```

---

## 🛡️ Firewall-Konfiguration

### UFW (Ubuntu/Debian)
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status
```

### Fail2Ban (Brute-Force Schutz)
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📈 Performance-Optimierung

### 1. Docker-Limits setzen
```yaml
# In docker-compose.yml hinzufügen
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
  frontend:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

### 2. Nginx-Optimierung
```nginx
# In nginx.conf
worker_processes auto;
worker_connections 1024;

# Gzip Compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/css application/javascript application/json;
```

---

## 📞 Troubleshooting

### Häufige Probleme

#### "Out of disk space"
```bash
# Speicherplatz prüfen
df -h

# Docker cleanup
docker system prune -a -f
```

#### "Container won't start"
```bash
# Logs prüfen
docker-compose logs backend
docker-compose logs frontend

# Neustart
docker-compose down
docker-compose up -d
```

#### "SSL certificate error"
```bash
# Zertifikat erneuern
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

### Support-Kommandos
```bash
# Systemstatus
systemctl status mudiko
docker-compose ps
docker stats --no-stream

# Logs sammeln
docker-compose logs > mudiko-logs.txt
journalctl -u mudiko.service > systemd-logs.txt
```

---

## ✅ Go-Live Checkliste

- [ ] Server aktualisiert und gesichert
- [ ] Docker und Docker-Compose installiert
- [ ] MuDiKo erfolgreich gestartet
- [ ] Nginx Reverse Proxy konfiguriert
- [ ] SSL-Zertifikat installiert
- [ ] Systemd Service aktiviert
- [ ] Firewall konfiguriert
- [ ] Monitoring eingerichtet
- [ ] Backup-System aktiviert
- [ ] Health-Checks funktionieren
- [ ] Performance-Tests durchgeführt

**🎵 MuDiKo ist produktionsbereit!**