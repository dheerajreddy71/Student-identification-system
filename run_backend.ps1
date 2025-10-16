# Run backend server
# This script ensures the Python path is set correctly

$env:PYTHONPATH = "$PWD"
Write-Host "Starting backend server..." -ForegroundColor Green
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
