@echo off
title Crystal Game Server

echo ==========================================
echo       Starting Crystal Game Web Server
echo ==========================================
echo.

:: 1. Check if python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python is not installed or not in PATH.
    echo Please install Python 3 from https://www.python.org/
    pause
    exit /b 1
)

:: 2. Find a free port (start from 8000, +1 if occupied)
set PORT=8000
:findport
netstat -an | findstr "LISTENING" | findstr /C:":%PORT% " >nul 2>&1
if %errorlevel% EQU 0 (
    set /a PORT+=1
    goto findport
)

echo [INFO] Using port %PORT%
echo [WARNING] DO NOT CLOSE THIS WINDOW!
echo If you close this window, the game will stop working.
echo.

:: 3. Open the browser AFTER the server is ready.
::    A helper process polls the port, opens the browser, then exits by itself.
start "" cmd /c "powershell -NoProfile -Command $t=0; while($t -lt 30){ try { $c=New-Object Net.Sockets.TcpClient('127.0.0.1', %PORT%); $c.Close(); break } catch { Start-Sleep -Milliseconds 500 }; $t++ }; Start-Process 'http://localhost:%PORT%/index.html'"

:: 4. Start the server in THIS window (foreground: closing the window stops the game)
echo Opening browser...
echo http://localhost:%PORT%/index.html
echo.
python -m http.server %PORT%

pause
