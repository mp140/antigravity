@echo off
title ANTIGRAVITY v3.0 — AI Trading Intelligence
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║     ANTIGRAVITY v3.0 — Trading Engine        ║
echo  ║     AI-Powered Market Intelligence           ║
echo  ╚══════════════════════════════════════════════╝
echo.
cd /d "%~dp0"

REM Use venv if it exists, otherwise fall back to system Python
if exist ".venv\Scripts\activate.bat" (
    echo [*] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [*] No venv found, using system Python...
)

echo [*] Starting server on http://localhost:8000
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
