@echo off
echo ================================================
echo    NexPro PDF Installation Script
echo    Prepared by CA Himanshu Majithiya
echo ================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

echo Installing required packages...
echo This may take a few minutes...
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install some packages.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo ================================================
echo    Installation Complete!
echo ================================================
echo.
echo NexPro PDF has been successfully installed.
echo.
echo To start the application, double-click on "RUN_NexPro.bat"
echo.
pause
