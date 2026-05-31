# PdM-Nuclear Development Setup

## Prerequisites
- Python 3.10+
- Node.js 20+
- Docker Desktop

## Quick Start (Windows)

```powershell
.\scripts\setup.ps1
```

## Quick Start (Linux/macOS)

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

## Manual Steps

### 1. Environment
```powershell
Copy-Item .env.example .env
```

### 2. InfluxDB
Docker Desktop must be running first.

```powershell
docker compose up -d influxdb
```

If Docker is unavailable, the backend falls back to in-memory alert storage.

### 3. Backend
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "."
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend
```powershell
cd frontend
npm install
npm run dev
```

## URLs
| Service | URL |
|---------|-----|
| API Docs (Swagger) | http://localhost:8000/docs |
| Dashboard | http://localhost:5173 |
| InfluxDB UI | http://localhost:8086 |

## First Run Workflow
1. Install ML stack (optional, ~350MB): `pip install -r requirements-ml.txt`
2. Generate synthetic data: `POST /api/v1/data/generate`
3. Train model: `POST /api/v1/model/retrain`
4. Open dashboard and monitor live charts

## Project Structure
```
backend/app/          # FastAPI application
  api/v1/             # REST endpoints
  services/           # Business logic (generator, ML, InfluxDB)
  models/             # LSTM Autoencoder
  schemas/            # Pydantic models
frontend/src/         # React dashboard
data/raw/             # Generated CSV files
data/models/          # Trained .h5 models
docker/               # Dockerfiles
```
