@echo off
REM NexPro PDF Setup Script
REM Automated installation of dependencies

echo.
echo ========================================
echo   NexPro PDF - Setup & Installation
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check Python version
python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11 or higher is required
    echo Your Python version:
    python --version
    pause
    exit /b 1
)

echo [1/4] Upgrading pip...
python -m pip install --upgrade pip
echo.

echo [2/4] Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)
echo.

echo [3/4] Creating necessary directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp
if not exist "resources\icons" mkdir resources\icons
echo.

echo [4/4] Setup complete!
echo.
echo ========================================
echo   Installation Successful!
echo ========================================
echo.
echo You can now run NexPro PDF using:
echo   - run.bat
echo   - python main.py
echo.
echo For more information, see:
echo   - README.md (General information)
echo   - QUICKSTART.md (Quick start guide)
echo   - DEVELOPMENT.md (Development guide)
echo.

pause
