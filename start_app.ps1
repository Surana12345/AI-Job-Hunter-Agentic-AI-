# AI Job Hunter Local Launcher Script

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting AI Job Hunter (Backend + Frontend)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Start Backend Server in Background
Write-Host "1. Launching FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
$backendProcess = Start-Process -FilePath "d:\AI Job Hunter (Agentic AI)\venv\Scripts\python.exe" -ArgumentList "-m uvicorn backend.main:app --host 127.0.0.1 --port 8000" -PassThru -NoNewWindow

Start-Sleep -Seconds 3

# Start Streamlit Frontend
Write-Host "2. Launching Streamlit Frontend on http://localhost:8501 ..." -ForegroundColor Green
& "d:\AI Job Hunter (Agentic AI)\venv\Scripts\streamlit.exe" run frontend/app.py
