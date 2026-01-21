$ErrorActionPreference = "Stop"

Write-Host "--- Rebuilding & Relaunching Docker Containers ---" -ForegroundColor Cyan

# 1. Build Backend
Write-Host "Building Backend Image..." -ForegroundColor Yellow
docker build -t nduka99/hm_backend:latest -f hm_recsys_app/backend/Dockerfile hm_recsys_app/backend

# 2. Build Frontend
Write-Host "Building Frontend Image..." -ForegroundColor Yellow
docker build -t nduka99/hm_frontend:latest -f hm_recsys_app/frontend/Dockerfile hm_recsys_app/frontend

# 3. Create Network (if missing)
if (!(docker network ls -q -f name=hm_net)) {
    Write-Host "Creating Docker Network 'hm_net'..."
    docker network create hm_net
}

# 4. Stop & Remove Old Containers
Write-Host "Cleaning up old containers..." -ForegroundColor Magenta
docker rm -f hm_backend hm_frontend 2>$null

# 5. Run Backend
# Map port 8000:8000
Write-Host "Starting Backend..." -ForegroundColor Green
docker run -d --name hm_backend `
    --network hm_net `
    -p 8000:8000 `
    -e ARTIFACT_DIR=artifacts `
    nduka99/hm_backend:latest

# 6. Run Frontend
# Map port 8503:8503 (Updated from 8501)
# Mount local images folder to /data/images so local app can see them
# Set IMAGE_BASE_PATH to /data/images
$LocalImages = "$PWD\data\images"
Write-Host "Starting Frontend (mounting $LocalImages)..." -ForegroundColor Green

docker run -d --name hm_frontend `
    --network hm_net `
    -p 8510:8503 `
    -e API_URL=http://hm_backend:8000 `
    -e IMAGE_BASE_PATH=/data/images `
    -v "$LocalImages`:/data/images" `
    nduka99/hm_frontend:latest

Write-Host "--- Cloud & Local Fix Deployed ---" -ForegroundColor Cyan
Write-Host "Backend (Local): http://localhost:8000/docs"
Write-Host "Frontend (Local): http://localhost:8510"
Write-Host "Note: Frontend is mapped to 8510 locally to distinguish from Streamlit default."
