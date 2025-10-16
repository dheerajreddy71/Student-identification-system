# Pre-Deployment Verification Script
# Run this before pushing to GitHub to ensure everything is ready

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Pre-Deployment Verification" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Check 1: Required files exist
Write-Host "[1/10] Checking required files..." -ForegroundColor Yellow
$requiredFiles = @(
    "README.md",
    "requirements.txt",
    "setup.ps1",
    ".gitignore",
    "LICENSE",
    "DEPLOYMENT.md",
    "MANUAL_DOWNLOAD.md",
    "backend\main.py",
    "backend\config.py",
    "frontend\package.json",
    "Dockerfile.backend",
    "Dockerfile.frontend",
    "docker-compose.yml"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file - MISSING" -ForegroundColor Red
        $allPassed = $false
    }
}

# Check 2: .gitignore is properly configured
Write-Host ""
Write-Host "[2/10] Checking .gitignore configuration..." -ForegroundColor Yellow
$gitignoreContent = Get-Content ".gitignore" -Raw
$criticalIgnores = @("venv/", "*.db", "models/*.ckpt", "models/*.pth", "trainset/", ".env")
foreach ($ignore in $criticalIgnores) {
    if ($gitignoreContent -match [regex]::Escape($ignore)) {
        Write-Host "  ✓ $ignore is ignored" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $ignore is NOT ignored - will upload large files!" -ForegroundColor Red
        $allPassed = $false
    }
}

# Check 3: Environment variables
Write-Host ""
Write-Host "[3/10] Checking environment files..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env exists (will be ignored by Git)" -ForegroundColor Green
} else {
    Write-Host "  ⚠ .env not found - create from .env.example" -ForegroundColor Yellow
}

if (Test-Path ".env.example") {
    Write-Host "  ✓ .env.example exists (will be uploaded)" -ForegroundColor Green
} else {
    Write-Host "  ✗ .env.example missing - users need this" -ForegroundColor Red
    $allPassed = $false
}

# Check 4: Model files (should NOT be uploaded)
Write-Host ""
Write-Host "[4/10] Checking model files..." -ForegroundColor Yellow
$modelFiles = @(
    "models\GFPGANv1.4.pth",
    "models\RealESRGAN_x4plus.pth",
    "models\adaface_ir101_webface12m.ckpt"
)
$modelsExist = 0
foreach ($model in $modelFiles) {
    if (Test-Path $model) {
        $modelsExist++
        $size = [math]::Round((Get-Item $model).Length / 1MB, 2)
        Write-Host "  ✓ $model exists ($size MB) - will be ignored" -ForegroundColor Green
    }
}
if ($modelsExist -eq 0) {
    Write-Host "  ⚠ No models found - users will need to download" -ForegroundColor Yellow
}

# Check 5: Database files (should NOT be uploaded)
Write-Host ""
Write-Host "[5/10] Checking database files..." -ForegroundColor Yellow
if (Test-Path "*.db") {
    Write-Host "  ✓ Database exists - will be ignored" -ForegroundColor Green
} else {
    Write-Host "  ⚠ No database - will be created on setup" -ForegroundColor Yellow
}

# Check 6: Virtual environment (should NOT be uploaded)
Write-Host ""
Write-Host "[6/10] Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ✓ venv exists - will be ignored" -ForegroundColor Green
} else {
    Write-Host "  ⚠ venv not found - will be created on setup" -ForegroundColor Yellow
}

# Check 7: Frontend dependencies
Write-Host ""
Write-Host "[7/10] Checking frontend..." -ForegroundColor Yellow
if (Test-Path "frontend\node_modules") {
    Write-Host "  ✓ node_modules exists - will be ignored" -ForegroundColor Green
} else {
    Write-Host "  ⚠ node_modules not found - will be installed on setup" -ForegroundColor Yellow
}

if (Test-Path "frontend\.next") {
    Write-Host "  ✓ .next build exists - will be ignored" -ForegroundColor Green
} else {
    Write-Host "  ⚠ .next not found - will be built on setup" -ForegroundColor Yellow
}

# Check 8: Documentation completeness
Write-Host ""
Write-Host "[8/10] Checking documentation..." -ForegroundColor Yellow
$docs = @(
    "README.md",
    "DEPLOYMENT.md",
    "QUICKSTART.md",
    "SETUP_GUIDE.md",
    "PROJECT_SUMMARY.md",
    "MANUAL_DOWNLOAD.md"
)
foreach ($doc in $docs) {
    if (Test-Path $doc) {
        $size = (Get-Item $doc).Length
        if ($size -gt 100) {
            Write-Host "  ✓ $doc ($size bytes)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ $doc is very small ($size bytes)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ✗ $doc - MISSING" -ForegroundColor Red
        $allPassed = $false
    }
}

# Check 9: Test .gitignore effectiveness
Write-Host ""
Write-Host "[9/10] Testing Git ignore effectiveness..." -ForegroundColor Yellow
$gitStatus = git status --porcelain 2>$null
if ($gitStatus) {
    $filesToCommit = ($gitStatus | Where-Object { $_ -match "^\?\?" -or $_ -match "^M" }).Count
    $ignoredLargeFiles = @()
    
    # Check if large files are being tracked
    if ($gitStatus -match "models.*\.(pth|ckpt)") {
        Write-Host "  ✗ WARNING: Model files detected in git status!" -ForegroundColor Red
        $allPassed = $false
    } else {
        Write-Host "  ✓ Model files properly ignored" -ForegroundColor Green
    }
    
    if ($gitStatus -match "venv") {
        Write-Host "  ✗ WARNING: venv detected in git status!" -ForegroundColor Red
        $allPassed = $false
    } else {
        Write-Host "  ✓ venv properly ignored" -ForegroundColor Green
    }
    
    if ($gitStatus -match "\.db$") {
        Write-Host "  ✗ WARNING: Database files detected in git status!" -ForegroundColor Red
        $allPassed = $false
    } else {
        Write-Host "  ✓ Database files properly ignored" -ForegroundColor Green
    }
    
    Write-Host "  ℹ Total files to commit: $filesToCommit" -ForegroundColor Cyan
} else {
    Write-Host "  ⚠ No git repository or no changes to commit" -ForegroundColor Yellow
}

# Check 10: Sensitive data check
Write-Host ""
Write-Host "[10/10] Checking for sensitive data..." -ForegroundColor Yellow
$sensitivePatterns = @(
    "password\s*=\s*['\"][^'\"]+['\"]",
    "api_key\s*=\s*['\"][^'\"]+['\"]",
    "secret_key\s*=\s*['\"][^'\"]+['\"]",
    "aws_access_key",
    "private_key"
)

$foundSensitive = $false
Get-ChildItem -Recurse -Include *.py,*.js,*.ts,*.tsx,*.env.example -Exclude venv,node_modules | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    foreach ($pattern in $sensitivePatterns) {
        if ($content -match $pattern) {
            if ($_.Name -ne ".env.example") {
                Write-Host "  ⚠ Potential sensitive data in: $($_.Name)" -ForegroundColor Yellow
                $foundSensitive = $true
            }
        }
    }
}

if (-not $foundSensitive) {
    Write-Host "  ✓ No sensitive data detected" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Verification Summary" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

if ($allPassed) {
    Write-Host ""
    Write-Host "✓ ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your project is ready for deployment!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Run: .\deploy_to_github.ps1" -ForegroundColor White
    Write-Host "2. Or manually:" -ForegroundColor White
    Write-Host "   git add ." -ForegroundColor Gray
    Write-Host "   git commit -m 'Initial commit'" -ForegroundColor Gray
    Write-Host "   git push -u origin main" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "✗ SOME CHECKS FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please fix the issues above before deploying" -ForegroundColor Yellow
    Write-Host "Check the red (✗) items and resolve them" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
