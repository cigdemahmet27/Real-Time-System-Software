@echo off
echo ========================================
echo  Real-Time Scheduling System - UI
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check and install dependencies
echo Checking dependencies...
pip show matplotlib >nul 2>&1
if errorlevel 1 (
    echo Installing matplotlib...
    pip install matplotlib
)

REM Run the UI
echo.
echo Starting Real-Time Scheduling UI...
echo.
python "%~dp0app.py"

pause

