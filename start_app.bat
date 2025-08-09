@echo off
echo Starting DP Stock Investment Assistant with UI...

echo.
echo Step 1: Starting Backend API Server...
start "API Server" cmd /k "cd /d %cd% && python src/main.py --mode web"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo Step 2: Starting React Frontend...
start "React Frontend" cmd /k "cd /d %cd%/frontend && npm run start:fast"

echo.
echo ============================================
echo  DP Stock Investment Assistant is starting
echo ============================================
echo Backend API: http://localhost:5000
echo Frontend UI: http://localhost:3000
echo.
echo Both services are starting in separate windows.
echo Close this window when you're done.

pause
