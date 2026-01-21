$ErrorActionPreference = "Stop"
$DockerUser = "nduka99"

Write-Host "--- Docker Hub Deployment ($DockerUser) ---" -ForegroundColor Cyan

# 1. Tag Backend
Write-Host "Tagging Backend..."
docker tag hm_backend:latest "$DockerUser/hm_backend:latest"

# 2. Tag Frontend
Write-Host "Tagging Frontend..."
docker tag hm_frontend:latest "$DockerUser/hm_frontend:latest"

# 3. Push Backend
Write-Host "Pushing Backend to Docker Hub (This may take a minute)..." -ForegroundColor Yellow
docker push "$DockerUser/hm_backend:latest"

# 4. Push Frontend
Write-Host "Pushing Frontend to Docker Hub..." -ForegroundColor Yellow
docker push "$DockerUser/hm_frontend:latest"

Write-Host "--- Success! ---" -ForegroundColor Green
Write-Host "Images are now live at:"
Write-Host " - $DockerUser/hm_backend:latest"
Write-Host " - $DockerUser/hm_frontend:latest"
