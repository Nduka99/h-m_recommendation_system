$ErrorActionPreference = "Stop"

# Get Absolute Paths
$Root = Get-Location
$VenvPython = "$Root\.hnm\Scripts\python.exe"
$BackendDir = "$Root\hm_recsys_app\backend"
$FrontendDir = "$Root\hm_recsys_app\frontend"

Write-Host "--- H&M Recommender System Launcher ---" -ForegroundColor Cyan

# 1. Start Backend (Port 8000)
Write-Host "Launching Backend (The Brain) on Port 8000..." -ForegroundColor Green
$BackendCmd = "cd '$BackendDir'; & '$VenvPython' -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$BackendCmd"

Write-Host "Waiting 5 seconds for Backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 2. Start Frontend (Port 8503)
Write-Host "Launching Frontend (The Face) on Port 8503..." -ForegroundColor Green
# We set API_URL env var for the frontend session
# We als set IMAGE_BASE_PATH to the local data/images folder
$ImagesPath = "$Root\data\images"
$FrontendCmd = "cd '$FrontendDir'; $env:API_URL='http://localhost:8000'; $env:IMAGE_BASE_PATH='$ImagesPath'; & '$VenvPython' -m streamlit run app.py --server.port 8503"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$FrontendCmd"

Write-Host "--- Systems Launched! ---" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:8503"
