@echo off
title TalentAnalytics - System Launcher
cd /d "%~dp0"
echo ==============================================================================
echo  Launching Resume Shortlisting & Candidate Analytics System
echo  Data Mining + Data Warehouse + Flask + React + MongoDB
echo ==============================================================================
echo.
echo [1/2] Starting Flask Backend Server (Port 5000)...
start "TalentAnalytics Backend API" cmd /c "run_backend.bat"

echo [2/2] Starting React Vite Frontend Server (Port 3000)...
start "TalentAnalytics Frontend UI" cmd /c "run_frontend.bat"

echo.
echo Waiting 5 seconds for servers to initialize...
timeout /t 5 /nobreak >nul

echo Opening browser at http://localhost:3000...
start http://localhost:3000

echo ==============================================================================
echo  System is running! 
echo  Press any key to close this launcher window (servers will remain running).
echo ==============================================================================
pause
