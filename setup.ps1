# Student Identification System - First Run Script
# This script will guide you through the complete setup process

Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "Student Identification System - Automated Setup" -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Step 1: Checking Python installation..." -ForegroundColor Yellow
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCheck) {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
}
else {
    Write-Host "✗ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Step 2: Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}
else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Step 3: Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host ""
Write-Host "Step 4: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ Pip upgraded" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Step 5: Installing dependencies (this may take 5-10 minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
}
else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Setup configuration
Write-Host ""
Write-Host "Step 6: Setting up configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ Configuration file already exists" -ForegroundColor Green
}
else {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Configuration file created" -ForegroundColor Green
}

# Create directories
Write-Host ""
Write-Host "Step 7: Creating directories..." -ForegroundColor Yellow
$directories = @("data", "models", "photos", "logs", "temp")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}
Write-Host "✓ Directories created" -ForegroundColor Green

# Check for models
Write-Host ""
Write-Host "Step 8: Checking pretrained models..." -ForegroundColor Yellow
$models = @(
    "models/GFPGANv1.4.pth",
    "models/RealESRGAN_x4plus.pth",
    "models/adaface_ir101_webface12m.ckpt"
)

$modelsExist = $true
foreach ($model in $models) {
    if (!(Test-Path $model)) {
        $modelsExist = $false
        Write-Host "✗ Missing: $model" -ForegroundColor Red
    }
}

if ($modelsExist) {
    Write-Host "✓ All models found" -ForegroundColor Green
}

if (!$modelsExist) {
    Write-Host ""
    Write-Host "Downloading models (this may take 10-15 minutes)..." -ForegroundColor Yellow
    python scripts/download_models.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to download models" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Models downloaded" -ForegroundColor Green
}

# Initialize database
Write-Host ""
Write-Host "Step 9: Initializing database..." -ForegroundColor Yellow
python backend/init_db.py
Write-Host "✓ Database initialized" -ForegroundColor Green
Write-Host "   Default admin user created:" -ForegroundColor Cyan
Write-Host "   Username: admin" -ForegroundColor Cyan
Write-Host "   Password: admin123" -ForegroundColor Cyan
Write-Host "   ⚠ Change this password after first login!" -ForegroundColor Yellow

# Register students
Write-Host ""
Write-Host "Step 10: Would you like to register students from trainset now?" -ForegroundColor Yellow
$response = Read-Host "This may take several minutes. Continue? (Y/N)"

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host "Registering students..." -ForegroundColor Yellow
    python scripts/register_students.py --data_dir trainset
    Write-Host "✓ Students registered" -ForegroundColor Green
}

if ($response -ne "Y" -and $response -ne "y") {
    Write-Host "⊙ Skipped student registration" -ForegroundColor Gray
    Write-Host "  Run later with: python scripts/register_students.py --data_dir trainset" -ForegroundColor Gray
}

# Complete
Write-Host ""
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Start the backend server:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Cyan
Write-Host "   uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Test identification:" -ForegroundColor White
Write-Host "   python scripts/test_identification.py `"trainset/0001/0001_0000255/0000001.jpg`"" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Access API documentation:" -ForegroundColor White
Write-Host "   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. (Optional) Start frontend:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Cyan
Write-Host "   npm install" -ForegroundColor Cyan
Write-Host "   npm run dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more information, see:" -ForegroundColor White
Write-Host "- QUICKSTART.md (10-minute guide)" -ForegroundColor Cyan
Write-Host "- SETUP_GUIDE.md (detailed documentation)" -ForegroundColor Cyan
Write-Host "- PROJECT_SUMMARY.md (complete overview)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Happy identifying! 🎉" -ForegroundColor Green
