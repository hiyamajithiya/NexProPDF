@echo off
REM NexPro PDF Launcher
REM Quick launch script for Windows

echo.
echo ========================================
echo   NexPro PDF - Professional PDF Editor
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Launching NexPro PDF...
echo.

REM Run the application
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo Check logs directory for error details
    pause
)

exit /b 0
