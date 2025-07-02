#!/bin/bash
# Build script for DJZ-Speak on Linux/macOS

set -e

echo "Building DJZ-Speak for Linux/macOS..."

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

# Create build directories
mkdir -p dist
mkdir -p build

# Build executable
echo "Creating standalone executable..."
pyinstaller \
    --onefile \
    --name djz-speak \
    --add-data "config:config" \
    --add-data "src:src" \
    --hidden-import pydub \
    --hidden-import soundfile \
    --hidden-import numpy \
    --hidden-import yaml \
    --hidden-import scipy \
    --hidden-import librosa \
    --console \
    main.py

echo "Build completed successfully!"
echo "Executable location: dist/djz-speak"

# Make executable
chmod +x dist/djz-speak

# Test the executable
echo "Testing executable..."
./dist/djz-speak --help

echo ""
echo "Build complete! You can now run: ./dist/djz-speak"
