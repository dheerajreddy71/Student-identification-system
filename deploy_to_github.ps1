# GitHub Setup and Deployment Script
# Run this script to prepare and push your project to GitHub

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Student Identification System" -ForegroundColor Cyan
Write-Host "GitHub Setup Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command($command) {
    try {
        if (Get-Command $command -ErrorAction Stop) {
            return $true
        }
    }
    catch {
        return $false
    }
}

# Check Git installation
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
if (-not (Test-Command "git")) {
    Write-Host "❌ Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Git installed" -ForegroundColor Green

# Get GitHub repository URL
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please create a new repository on GitHub:" -ForegroundColor Yellow
Write-Host "1. Go to: https://github.com/new" -ForegroundColor White
Write-Host "2. Repository name: student-identification-system" -ForegroundColor White
Write-Host "3. Description: AI-Powered Student Identification System with GFPGAN + AdaFace + FAISS" -ForegroundColor White
Write-Host "4. Choose: Public or Private" -ForegroundColor White
Write-Host "5. DO NOT initialize with README (we already have one)" -ForegroundColor White
Write-Host ""

$repoUrl = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/student-identification-system.git)"

if ([string]::IsNullOrWhiteSpace($repoUrl)) {
    Write-Host "❌ Repository URL is required!" -ForegroundColor Red
    exit 1
}

# Configure Git user (if not configured)
Write-Host ""
Write-Host "Configuring Git..." -ForegroundColor Yellow

$gitUserName = git config user.name
if ([string]::IsNullOrWhiteSpace($gitUserName)) {
    $userName = Read-Host "Enter your name for Git commits"
    git config --global user.name $userName
}

$gitUserEmail = git config user.email
if ([string]::IsNullOrWhiteSpace($gitUserEmail)) {
    $userEmail = Read-Host "Enter your email for Git commits"
    git config --global user.email $userEmail
}

Write-Host "✓ Git configured" -ForegroundColor Green

# Initialize Git repository
Write-Host ""
Write-Host "Initializing Git repository..." -ForegroundColor Yellow

if (-not (Test-Path ".git")) {
    git init
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✓ Git repository already initialized" -ForegroundColor Green
}

# Check if remote exists
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Host "Remote 'origin' already exists. Removing..." -ForegroundColor Yellow
    git remote remove origin
}

# Add remote
git remote add origin $repoUrl
Write-Host "✓ Remote repository added" -ForegroundColor Green

# Check files to be committed
Write-Host ""
Write-Host "Checking files to commit..." -ForegroundColor Yellow
$status = git status --short
if ($status) {
    $fileCount = ($status | Measure-Object).Count
    Write-Host "Found $fileCount files to commit" -ForegroundColor Cyan
} else {
    Write-Host "No changes to commit" -ForegroundColor Yellow
}

# Show what will be ignored
Write-Host ""
Write-Host "Files that will be IGNORED (not uploaded to GitHub):" -ForegroundColor Yellow
Write-Host "- venv/ (Python virtual environment)" -ForegroundColor Gray
Write-Host "- models/*.ckpt (AdaFace model - 365 MB)" -ForegroundColor Gray
Write-Host "- models/*.pth (GFPGAN models - 297 MB)" -ForegroundColor Gray
Write-Host "- trainset/ (training images)" -ForegroundColor Gray
Write-Host "- data/ (FAISS index and metadata)" -ForegroundColor Gray
Write-Host "- *.db (SQLite database)" -ForegroundColor Gray
Write-Host "- .env (environment variables)" -ForegroundColor Gray
Write-Host "- frontend/node_modules/ (Node.js packages)" -ForegroundColor Gray
Write-Host "- frontend/.next/ (Next.js build)" -ForegroundColor Gray
Write-Host ""
Write-Host "Users will need to download models separately (see MANUAL_DOWNLOAD.md)" -ForegroundColor Cyan

# Stage all files
Write-Host ""
Write-Host "Staging files..." -ForegroundColor Yellow
git add .
Write-Host "✓ Files staged" -ForegroundColor Green

# Create commit
Write-Host ""
$commitMessage = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Initial commit: AI-Powered Student Identification System with GFPGAN + AdaFace + FAISS"
}

git commit -m $commitMessage
Write-Host "✓ Commit created" -ForegroundColor Green

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "You may be prompted for your GitHub username and password/token" -ForegroundColor Cyan
Write-Host ""

$branch = git branch --show-current
if ([string]::IsNullOrWhiteSpace($branch)) {
    $branch = "main"
    git branch -M main
}

try {
    git push -u origin $branch
    Write-Host ""
    Write-Host "=================================" -ForegroundColor Green
    Write-Host "✓ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your repository is now available at:" -ForegroundColor Cyan
    Write-Host $repoUrl.Replace(".git", "") -ForegroundColor White
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Add repository description on GitHub" -ForegroundColor White
    Write-Host "2. Add topics/tags: machine-learning, face-recognition, ai, computer-vision" -ForegroundColor White
    Write-Host "3. Add a LICENSE file (e.g., MIT License)" -ForegroundColor White
    Write-Host "4. Update README.md with your specific details" -ForegroundColor White
    Write-Host "5. Enable GitHub Pages (optional)" -ForegroundColor White
    Write-Host ""
    Write-Host "See DEPLOYMENT.md for deployment instructions" -ForegroundColor Cyan
}
catch {
    Write-Host ""
    Write-Host "❌ Failed to push to GitHub" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Authentication failed: Use Personal Access Token instead of password" -ForegroundColor White
    Write-Host "   - Go to: https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "   - Create new token with 'repo' scope" -ForegroundColor White
    Write-Host "   - Use token as password" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Repository doesn't exist: Create it on GitHub first" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Permission denied: Check repository URL and access rights" -ForegroundColor White
    Write-Host ""
    Write-Host "Retry with: git push -u origin $branch" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
