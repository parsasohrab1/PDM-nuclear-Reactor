$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "=== PdM-Nuclear Setup ===" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[OK] Created .env from .env.example"
} else {
    Write-Host "[SKIP] .env already exists"
}

Write-Host "`n--- Python virtual environment ---"
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "[OK] Created .venv"
}
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Write-Host "[OK] Python dependencies installed"
Write-Host "`n--- Optional: ML stack (TensorFlow ~350MB) ---"
Write-Host "Run manually when ready: pip install -r requirements-ml.txt"

Write-Host "`n--- Frontend dependencies ---"
Push-Location frontend
npm install
Pop-Location
Write-Host "[OK] Frontend dependencies installed"

Write-Host "`n--- InfluxDB (Docker) ---"
docker compose up -d influxdb
Write-Host "[OK] InfluxDB started on http://localhost:8086"

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "Start backend:  `$env:PYTHONPATH='.'; uvicorn backend.app.main:app --reload"
Write-Host "Start frontend: cd frontend; npm run dev"
Write-Host "API docs:       http://localhost:8000/docs"
