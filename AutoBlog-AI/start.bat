@echo off
title AutoBlog AI v3
color 0A
echo.
echo  ╔══════════════════════════════════╗
echo  ║       AutoBlog AI v3             ║
echo  ║   AI Writing Engine              ║
echo  ╚══════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found.
    echo.
    echo  Install Python 3.12 from https://python.org
    echo  IMPORTANT: Check "Add Python to PATH" during install.
    echo.
    pause
    exit /b
)

echo  [OK] Python found.

:: Install dependencies
echo  Installing dependencies...
pip install flask flask-cors requests google-generativeai groq anthropic --quiet --break-system-packages 2>nul || pip install flask flask-cors requests google-generativeai groq anthropic --quiet

echo  [OK] Dependencies ready.
echo.
echo  Starting AutoBlog AI...
echo  Dashboard: http://localhost:5000
echo.

:: Open browser after 2 seconds
start /b cmd /c "timeout /t 2 >nul && start http://localhost:5000"

:: Run app
python app.py

pause
