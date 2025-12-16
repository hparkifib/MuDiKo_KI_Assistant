# Test Script für MP3-to-MIDI Plugin
Write-Host "MP3-to-MIDI Plugin Test" -ForegroundColor Cyan

# Test API Health
Write-Host "`nTest API Health..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "http://localhost:5000/api/health"
Write-Host "Status: $($health.status), Plugins: $($health.plugins)" -ForegroundColor Green

Write-Host "`nAlle Tests abgeschlossen!" -ForegroundColor Green
