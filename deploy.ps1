# MuDiKo Deployment Script for Windows
Write-Host "Deploying MuDiKo AI Assistant with HTTPS..." -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Pre-Deployment Checks
Write-Host ""
Write-Host "Pre-Deployment Checks:" -ForegroundColor Yellow
Write-Host "1. DNS: music.ifib.eu muss auf die Server-IP zeigen" -ForegroundColor White
Write-Host "2. Firewall: Ports 80 und 443 müssen offen sein" -ForegroundColor White
Write-Host "3. Kein anderer Webserver darf auf Port 80/443 laufen" -ForegroundColor White
Write-Host ""

# Build and start services
Write-Host "Building Docker images..." -ForegroundColor Yellow
docker-compose build --no-cache

Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if services are running
$services = docker-compose ps
if ($services -match "Up") {
    Write-Host "MuDiKo AI Assistant is now running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Frontend: https://music.ifib.eu" -ForegroundColor Cyan
    Write-Host "Backend API: https://music.ifib.eu/api" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Caddy Status:" -ForegroundColor Yellow
    Write-Host "  - Caddy holt automatisch SSL-Zertifikat von Let's Encrypt" -ForegroundColor White
    Write-Host "  - HTTP (Port 80) leitet automatisch zu HTTPS (Port 443) um" -ForegroundColor White
    Write-Host "  - Zertifikate werden automatisch erneuert" -ForegroundColor White
    Write-Host ""
    Write-Host "Nützliche Befehle:" -ForegroundColor Yellow
    Write-Host "  docker-compose logs -f caddy      # Caddy Logs anzeigen" -ForegroundColor White
    Write-Host "  docker-compose logs -f            # Alle Logs anzeigen" -ForegroundColor White
    Write-Host "  docker-compose ps                 # Service Status prüfen" -ForegroundColor White
    Write-Host "  docker-compose down               # Services stoppen" -ForegroundColor White
    Write-Host ""
    Write-Host "SSL-Zertifikat Status prüfen:" -ForegroundColor Yellow
    Write-Host "  docker exec mudiko-caddy caddy list-certificates" -ForegroundColor White
} else {
    Write-Host "Failed to start services. Check logs with: docker-compose logs" -ForegroundColor Red
    exit 1
}