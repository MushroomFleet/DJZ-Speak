@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo DJZ-Speak Installation Script
echo ===============================================
echo.

:: Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

:: Display Python version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found: !PYTHON_VERSION!
echo.

:: Check if virtual environment already exists
echo [2/5] Checking virtual environment...
if exist "venv\" (
    echo Virtual environment already exists.
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q "venv"
        if errorlevel 1 (
            echo ERROR: Failed to remove existing virtual environment
            echo Please close any applications using the environment and try again
            pause
            exit /b 1
        )
    ) else (
        echo Skipping virtual environment creation.
        goto :install_deps
    )
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Make sure you have sufficient permissions and disk space
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

:install_deps
:: Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated!
echo.

:: Upgrade pip
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing with installation...
)
echo.

:: Install requirements
echo [5/5] Installing dependencies from requirements.txt...
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    echo Make sure you're running this script from the DJZ-Speak project directory
    pause
    exit /b 1
)

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ===============================================
echo Installation completed successfully!
echo ===============================================
echo.
echo Virtual environment created at: %CD%\venv
echo.
echo To use DJZ-Speak:
echo   1. Run 'run.bat' to activate the environment
echo   2. Use 'python main.py' commands as documented
echo.
echo Example usage:
echo   python main.py "Hello, I am a robot"
echo   python main.py -i
echo.
pause
