# MuDiKo Deployment Script for Windows
Write-Host "Deploying MuDiKo AI Assistant..." -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

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
    Write-Host "Frontend: http://localhost" -ForegroundColor Cyan
    Write-Host "Backend API: http://localhost:5000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To view logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "To stop: docker-compose down" -ForegroundColor White
} else {
    Write-Host "Failed to start services. Check logs with: docker-compose logs" -ForegroundColor Red
    exit 1
}