# Quick Fix Script - Download missing models and initialize database

Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "Quick Fix - Completing Setup" -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Download missing models
Write-Host "Downloading missing models..." -ForegroundColor Yellow
Write-Host "Note: If downloads fail, you may need to download them manually" -ForegroundColor Gray
Write-Host ""
python scripts/download_models.py

# Initialize database
Write-Host ""
Write-Host "Initializing database..." -ForegroundColor Yellow
$env:PYTHONPATH = "$PWD"
python backend/init_db.py
Write-Host "✓ Database initialized" -ForegroundColor Green
Write-Host ""

# Register students
Write-Host "Would you like to register students from trainset now?" -ForegroundColor Yellow
$response = Read-Host "This may take several minutes. Continue? (Y/N)"

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host "Registering students..." -ForegroundColor Yellow
    python scripts/register_students.py --data_dir trainset
    Write-Host "✓ Students registered" -ForegroundColor Green
}

Write-Host ""
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "✓ Fix Complete!" -ForegroundColor Green
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the system:" -ForegroundColor Yellow
Write-Host "  Backend:  .\run_backend.ps1" -ForegroundColor Cyan
Write-Host "  Frontend: .\run_frontend.ps1" -ForegroundColor Cyan
Write-Host ""
