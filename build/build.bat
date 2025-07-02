@echo off
REM Build script for DJZ-Speak on Windows

echo Building DJZ-Speak for Windows...

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Create build directory
if not exist "dist" mkdir dist
if not exist "build" mkdir build

REM Build executable
echo Creating standalone executable...
pyinstaller ^
    --onefile ^
    --name djz-speak ^
    --add-data "config;config" ^
    --add-data "src;src" ^
    --hidden-import pydub ^
    --hidden-import soundfile ^
    --hidden-import numpy ^
    --hidden-import yaml ^
    --hidden-import scipy ^
    --hidden-import librosa ^
    --console ^
    main.py

if errorlevel 1 (
    echo Build failed!
    exit /b 1
)

echo Build completed successfully!
echo Executable location: dist\djz-speak.exe

REM Test the executable
echo Testing executable...
dist\djz-speak.exe --help

echo.
echo Build complete! You can now run: dist\djz-speak.exe
pause
