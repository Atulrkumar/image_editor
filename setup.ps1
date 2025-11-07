# Quick Setup Script for AI Image Text Editor
# Run this in PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Image Text Editor - Quick Setup" -ForegroundColor Cyan
Write-Host "100% FREE - No Payment Required" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "[1/4] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.7+ from python.org" -ForegroundColor Red
    exit 1
}

# Step 2: Install Python packages
Write-Host ""
Write-Host "[2/4] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python packages installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install packages" -ForegroundColor Red
    exit 1
}

# Step 3: Check Tesseract
Write-Host ""
Write-Host "[3/4] Checking Tesseract OCR..." -ForegroundColor Yellow
try {
    $tesseractVersion = tesseract --version 2>&1
    Write-Host "✓ Tesseract found: $tesseractVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Tesseract not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Tesseract OCR (FREE):" -ForegroundColor Yellow
    Write-Host "1. Download: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
    Write-Host "2. Run installer (use default options)" -ForegroundColor Cyan
    Write-Host "3. Restart PowerShell and run this script again" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

# Step 4: Check Hugging Face API Key (optional)
Write-Host ""
Write-Host "[4/4] Checking Hugging Face API key (optional)..." -ForegroundColor Yellow
if ($env:HUGGING_FACE_API_KEY) {
    Write-Host "✓ API key found - AI generation enabled!" -ForegroundColor Green
} else {
    Write-Host "⚠ No API key found - using FREE text overlay mode" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To enable AI generation (optional):" -ForegroundColor Cyan
    Write-Host "1. Sign up (free): https://huggingface.co/join" -ForegroundColor Cyan
    Write-Host "2. Get token: https://huggingface.co/settings/tokens" -ForegroundColor Cyan
    Write-Host "3. Run: `$env:HUGGING_FACE_API_KEY='your_token'" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete! 🎉" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting the app..." -ForegroundColor Yellow
Write-Host "Open your browser to: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the app
python app.py
