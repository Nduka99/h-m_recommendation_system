$ErrorActionPreference = "Stop"

Write-Host "--- 1. Building Docker Image ---" -ForegroundColor Cyan
# Build from the backend directory context
docker build -t hm_backend:test ./hm_recsys_app/backend

Write-Host "--- 2. Running Docker Container ---" -ForegroundColor Cyan
# We mount the artifacts directory into the container.
# Local Path: $PWD/hm_recsys_app/artifacts
# Container Path: /app/artifacts
# We set ARTIFACT_DIR to /app/artifacts so main.py finds it.
$localArtifacts = "$(Get-Location)/hm_recsys_app/artifacts"
docker run -d -p 8000:8000 --name hm_test_container `
    -v "${localArtifacts}:/app/artifacts" `
    -e ARTIFACT_DIR="/app/artifacts" `
    hm_backend:test

Write-Host "--- 3. Waiting for Service to Start (10s) ---" -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host "--- 4. Testing Endpoints ---" -ForegroundColor Cyan

try {
    # Health Check
    $health = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get
    Write-Host "Health Check: $($health | ConvertTo-Json -Depth 1)" -ForegroundColor Green
    
    if ($health.model_loaded -ne $true) {
        throw "Model not loaded!"
    }

    # Prediction
    $payload = @{
        customer_id = 123456
        top_k = 5
    } | ConvertTo-Json

    $pred = Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $payload -ContentType "application/json"
    Write-Host "Prediction Result: $($pred | ConvertTo-Json -Depth 2)" -ForegroundColor Green
    
    if ($pred.recommendations.Count -eq 0) {
        Write-Warning "No recommendations returned."
    }

} catch {
    Write-Error "Verification Failed: $_"
    # Print logs on failure
    docker logs hm_test_container
} finally {
    Write-Host "--- 5. Cleaning Up ---" -ForegroundColor Cyan
    docker stop hm_test_container
    docker rm hm_test_container
}
