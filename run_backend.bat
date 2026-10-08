@echo off
title TalentAnalytics - Flask Backend Server (Port 5000)
cd /d "%~dp0"
echo ========================================================
echo  TalentAnalytics - Backend API Server
echo  Connected to MongoDB & Colab Data Mining Models
echo ========================================================
set PYTHONPATH=%cd%
call .\venv\Scripts\activate
python backend/app.py
pause
