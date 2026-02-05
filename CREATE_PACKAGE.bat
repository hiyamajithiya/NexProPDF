@echo off
echo ================================================
echo    NexPro PDF - Create Distribution Package
echo    Prepared by CA Himanshu Majithiya
echo ================================================
echo.

set OUTPUT_NAME=NexPro_PDF_v1.0.0.zip
set OUTPUT_DIR=..\

echo Cleaning up temporary files...
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "src\__pycache__" rmdir /s /q "src\__pycache__"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
if exist "*.pyc" del /q "*.pyc"

echo.
echo Creating distribution package...
echo This may take a moment...
echo.

:: Create the zip file (using PowerShell since it's built into Windows)
powershell -command "Compress-Archive -Path '.' -DestinationPath '%OUTPUT_DIR%%OUTPUT_NAME%' -Force -CompressionLevel Optimal"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create package!
    pause
    exit /b 1
)

echo.
echo ================================================
echo    Package Created Successfully!
echo ================================================
echo.
echo Package location: %OUTPUT_DIR%%OUTPUT_NAME%
echo.
echo You can now upload this file to your website.
echo.
pause
