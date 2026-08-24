# AI Job Hunter DevSecOps Web Server Launcher

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting AI Job Hunter DevSecOps Web Server" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "Launching Unified Web Server & FastAPI API on http://127.0.0.1:8000 ..." -ForegroundColor Green
Write-Host "• Web Application Portal: http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "• 3D Interactive Landing Page: http://127.0.0.1:8000/landing" -ForegroundColor Yellow
Write-Host "• OpenAPI Swagger Docs: http://127.0.0.1:8000/docs" -ForegroundColor Yellow

& "d:\AI Job Hunter (Agentic AI)\venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
