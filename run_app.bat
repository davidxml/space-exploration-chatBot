@echo off
TITLE Royce Mission Control

echo ===================================================
echo   ROCKET IGNITION SEQUENCE INITIATED
echo ===================================================

echo [1/2] Launching Neural Core (Backend)...
start "Royce Backend" cmd /k "python -m app.main"

echo [2/2] Launching Flight Deck (Frontend)...
timeout /t 5 /nobreak >nul
start "Royce Frontend" cmd /k "streamlit run frontend/main.py"

echo ===================================================
echo   SYSTEMS ONLINE. GOOD LUCK, EXPLORER.
echo ===================================================
pause