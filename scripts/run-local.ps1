# Simple runner for local development without Docker
# Usage:
# 1. Create and activate virtual environment
#    python -m venv .venv
#    .\.venv\Scripts\Activate.ps1
# 2. Install dependencies from requirements.txt
#    pip install -r requirements.txt
# 3. Run this script
Write-Host "Starting local server (requests to http://localhost:8000)..." -ForegroundColor Cyan
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000