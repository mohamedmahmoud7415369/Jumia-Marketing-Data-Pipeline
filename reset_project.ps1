# Stop and remove containers, networks, and volumes
Write-Host "Stopping Docker containers..."
docker-compose down -v

# Remove local data directory
Write-Host "Cleaning up local data..."
if (Test-Path "data") {
    Remove-Item -Path "data" -Recurse -Force
    Write-Host "Data directory removed."
}

# Rebuild images
Write-Host "Rebuilding Docker images..."
docker-compose build --no-cache

Write-Host "Reset complete! Run 'docker-compose up -d' to start fresh."
