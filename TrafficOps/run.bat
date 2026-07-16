@echo off
REM run.bat — double-click this instead of remembering the venv/python commands.
REM Must live in the TrafficOps root folder, next to requirements.txt.

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found at .venv — run setup first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python -m app.main

REM Keep the window open if the app crashes on startup, so the error is readable.
if errorlevel 1 (
    echo.
    echo TrafficOps exited with an error — see above.
    pause
)
