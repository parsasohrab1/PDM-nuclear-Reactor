#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== PdM-Nuclear Setup ==="

if [ ! -f .env ]; then
  cp .env.example .env
  echo "[OK] Created .env from .env.example"
else
  echo "[SKIP] .env already exists"
fi

echo ""
echo "--- Python virtual environment ---"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  echo "[OK] Created .venv"
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r requirements.txt
echo "[OK] Python dependencies installed"
echo ""
echo "--- Optional: ML stack (TensorFlow ~350MB) ---"
echo "Run manually when ready: pip install -r requirements-ml.txt"

echo ""
echo "--- Frontend dependencies ---"
(cd frontend && npm install)
echo "[OK] Frontend dependencies installed"

echo ""
echo "--- InfluxDB (Docker) ---"
docker compose up -d influxdb
echo "[OK] InfluxDB started on http://localhost:8086"

echo ""
echo "=== Setup Complete ==="
echo "Start backend:  PYTHONPATH=. uvicorn backend.app.main:app --reload"
echo "Start frontend: cd frontend && npm run dev"
echo "API docs:       http://localhost:8000/docs"
