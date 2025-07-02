@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo DJZ-Speak Runtime Environment
echo ===============================================
echo.

:: Check if virtual environment exists
echo Checking virtual environment...
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run 'install.bat' first to set up the environment.
    echo This will create the virtual environment and install dependencies.
    echo.
    pause
    exit /b 1
)

:: Check if activation script exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment appears to be corrupted
    echo The activation script is missing.
    echo.
    echo Please run 'install.bat' to recreate the environment.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo.
    echo The virtual environment may be corrupted.
    echo Please run 'install.bat' to recreate it.
    echo.
    pause
    exit /b 1
)

:: Verify Python and required packages
echo Verifying installation...
python -c "import sys; print(f'Python {sys.version}')" 2>nul
if errorlevel 1 (
    echo ERROR: Python not available in virtual environment
    echo Please run 'install.bat' to fix the installation.
    pause
    exit /b 1
)

:: Quick dependency check
python -c "import pydub, soundfile, numpy" 2>nul
if errorlevel 1 (
    echo WARNING: Some dependencies may be missing
    echo Consider running 'install.bat' to reinstall dependencies.
    echo.
)

:: Display environment ready message
echo.
echo ===============================================
echo Environment Ready!
echo ===============================================
echo.
echo Virtual environment is active: %VIRTUAL_ENV%
echo.
echo DJZ-Speak Commands:
echo   python main.py "Your text here"          - Basic text-to-speech
echo   python main.py -i                        - Interactive mode
echo   python main.py --help                    - Show all options
echo   python main.py --list-voices             - List available voices
echo.
echo Examples:
echo   python main.py "Hello, I am a robot"
echo   python main.py "Testing robotic voice" --voice classic_robot
echo   python main.py -i
echo.
echo Type 'deactivate' to exit the virtual environment
echo Type 'exit' to close this command prompt
echo.

:: Keep the command prompt open with activated environment
cmd /k
