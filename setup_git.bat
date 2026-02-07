@echo off
echo ==========================================
echo SkinIntell Git Setup Script
echo ==========================================

:: Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/download/win
    echo After installing, restart your computer or terminal and run this script again.
    pause
    exit /b
)

echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/username/skinintell.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL provided. Exiting.
    pause
    exit /b
)

echo.
echo [1/5] Initializing Git repository...
git init

echo [2/5] configuring user...
:: Note: user might need to configure this globally if not already set, 
:: but we'll leave global config alone to avoid overwriting user prefs.

echo [3/5] Adding files...
git add .

echo [4/5] Committing files...
git commit -m "Initial commit of SkinIntell application"

echo [5/5] Push to GitHub...
git branch -M main
git remote add origin %REPO_URL%
git push -u origin main

echo.
echo ==========================================
echo Setup Complete!
echo now go to https://dashboard.render.com/ to deploy.
echo ==========================================
pause
