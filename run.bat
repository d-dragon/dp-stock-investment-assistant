@echo off
echo Starting DP Stock-Investment Assistant...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements if needed
if not exist "venv\installed" (
    echo Installing requirements...
    pip install -r requirements.txt
    echo. > venv\installed
)

REM Run the application
echo Starting application...
python src\main.py

pause
