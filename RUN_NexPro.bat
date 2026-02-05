@echo off
title NexPro PDF - Professional PDF Editor
cd /d "%~dp0"

echo Starting NexPro PDF...
echo.

python main_connected.py

if errorlevel 1 (
    echo.
    echo An error occurred while running NexPro PDF.
    echo.
    echo If this is your first time running the application,
    echo please run INSTALL.bat first to install dependencies.
    echo.
    pause
)
