"""
Setup configuration for DJZ-Speak TTS tool
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="djz-speak",
    version="0.1.0",
    author="DJZ Development Team",
    author_email="dev@djz-speak.com",
    description="Command-line TTS tool with robotic voice synthesis using eSpeak-NG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/djz-team/djz-speak",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "build": [
            "pyinstaller>=5.0.0",
            "setuptools>=60.0.0",
            "wheel>=0.37.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "djz-speak=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.json", "config/*.yaml"],
    },
    data_files=[
        ("config", ["config/default_voices.json", "config/settings.yaml"]),
    ],
    keywords=[
        "tts", "text-to-speech", "espeak", "robotic", "voice", "synthesis",
        "formant", "cli", "audio", "speech", "robot", "vintage", "retro"
    ],
    project_urls={
        "Bug Reports": "https://github.com/djz-team/djz-speak/issues",
        "Source": "https://github.com/djz-team/djz-speak",
        "Documentation": "https://djz-speak.readthedocs.io/",
    },
)
