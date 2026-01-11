@echo off
title Crystal Game Server

echo ==========================================
echo       Starting Crystal Game Web Server
echo ==========================================
echo.
echo [WARNING] DO NOT CLOSE THIS WINDOW!
echo If you close this window, the game will stop working.
echo.
echo Opening browser...
echo http://localhost:8000/index_v4.html
echo.

start "" "http://localhost:8000/index_v4.html"

:: Check if python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit
)

python -m http.server 8000

pause
