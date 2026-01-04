@echo off
TITLE Royce Mission Control

echo ===================================================
echo   ROCKET IGNITION SEQUENCE INITIATED
echo ===================================================

:: 1. ACTIVATE THE VIRTUAL ENVIRONMENT FIRST
call UrbanSpace\Scripts\activate.bat

echo [1/2] Launching Neural Core (Backend)...
:: Use "start" to open a new window, but keep the environment active
start "Royce Backend" cmd /k "UrbanSpace\Scripts\python.exe -m app.main"

echo [2/2] Launching Flight Deck (Frontend)...
timeout /t 5 /nobreak >nul
start "Royce Frontend" cmd /k "UrbanSpace\Scripts\streamlit.exe run frontend/main.py"

echo ===================================================
echo   SYSTEMS ONLINE. GOOD LUCK, EXPLORER.
echo ===================================================
pause