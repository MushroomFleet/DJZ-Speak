# DJZ-Speak v0: Robotic Text-to-Speech Tool

DJZ-Speak is a high-performance command-line text-to-speech tool that leverages eSpeak-NG's formant synthesis engine to generate authentic machine-like robotic voices. The tool is optimized for speed while maintaining the characteristic mechanical sound of vintage computer speech systems.

## Features

- **8 Distinct Robotic Voice Presets**: Classic Robot, DECtalk Style, Dr. Sbaitso, HAL 9000, C-3PO Style, Vintage Computer, Modern AI, and Robotic Female
- **Real-Time Synthesis**: RTF < 0.5 for responsive speech generation
- **Interactive Mode**: Real-time parameter adjustment and voice switching
- **Batch Processing**: Process multiple texts efficiently
- **Audio Effects**: Robotic enhancement filters and mechanical artifacts
- **Cross-Platform**: Windows, Linux, and macOS support
- **Multiple Output Formats**: WAV and MP3 support

## Installation

### Prerequisites

1. **Python 3.8 or higher**
2. **eSpeak-NG text-to-speech engine**

#### Installing eSpeak-NG

**Windows:**
- Download and install from [eSpeak-NG releases](https://github.com/espeak-ng/espeak-ng/releases)
- Or use chocolatey: `choco install espeak`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install espeak-ng espeak-ng-data
```

**macOS:**
```bash
brew install espeak-ng
```

### Install DJZ-Speak

```bash
# Clone the repository
git clone https://github.com/djz-team/djz-speak.git
cd djz-speak

# Install dependencies
pip install -r requirements.txt

# Optional: Install in development mode
pip install -e .
```

## Quick Start

### Basic Usage

```bash
# Simple text synthesis
python main.py "Hello, I am a robot"

# Use a specific voice preset
python main.py "Greetings, human" --voice dectalk

# Save to file
python main.py "Test message" --output robot.wav

# Apply robotic effects
python main.py "Enhanced voice" --effects --output enhanced.wav
```

### Interactive Mode

```bash
python main.py -i
```

Interactive commands:
- `!voice <preset>` - Change voice preset
- `!speed <wpm>` - Set speech speed (80-300)
- `!pitch <level>` - Set pitch level (0-99)
- `!help` - Show available commands
- `!quit` - Exit interactive mode

### Voice Presets

| Preset | Description |
|--------|-------------|
| `classic_robot` | Standard computer robot voice |
| `dectalk` | Stephen Hawking-inspired synthesis |
| `sbaitso` | 1986 retro computer TTS |
| `hal9000` | Deep, slow computer voice |
| `c3po` | Protocol droid characteristics |
| `vintage_computer` | 1980s home computer TTS |
| `modern_ai` | Contemporary assistant voice |
| `robotic_female` | Female robotic synthesis |

### Advanced Usage

```bash
# List available voices
python main.py --list-voices

# Get voice information
python main.py --voice-info dectalk

# Batch processing
python main.py --text-file input.txt --batch-output ./audio/

# Custom parameters
python main.py "Custom voice" --speed 120 --pitch 25 --amplitude 90

# Read from stdin
echo "Hello world" | python main.py --stdin

# File input
python main.py --text-file story.txt --output story.wav
```

## Configuration

DJZ-Speak uses YAML configuration files for settings:

- `config/settings.yaml` - Main configuration
- `config/default_voices.json` - Voice presets
- `~/.djz-speak/config.yaml` - User overrides

### Environment Variables

- `DJZ_SPEAK_SPEED` - Default speech speed
- `DJZ_SPEAK_PITCH` - Default pitch level
- `DJZ_SPEAK_VOICE` - Default voice preset
- `DJZ_SPEAK_ESPEAK_PATH` - Custom eSpeak-NG path

## Building Standalone Executable

### Windows
```bash
cd build
build.bat
```

### Linux/macOS
```bash
cd build
chmod +x build.sh
./build.sh
```

The executable will be created in the `dist/` directory.

## Performance

DJZ-Speak is optimized for speed with the following performance targets:

- **Real-Time Factor**: < 0.5 (synthesis faster than playback)
- **Memory Usage**: < 100MB during operation
- **Synthesis Latency**: < 1 second for short phrases
- **Audio Quality**: 22kHz sample rate with clear robotic output

## Technical Details

### Architecture

```
DJZ-Speak/
├── main.py                 # CLI entry point
├── src/
│   ├── tts_engine.py      # Core TTS engine
│   ├── voice_manager.py   # Voice presets
│   ├── audio_processor.py # Audio effects
│   ├── config_manager.py  # Configuration
│   └── utils.py           # Utilities
├── config/                # Configuration files
├── build/                 # Build scripts
└── requirements.txt       # Dependencies
```

### Voice Synthesis

DJZ-Speak uses eSpeak-NG's formant synthesis engine, which:

- Generates inherently robotic speech through simplified spectral modeling
- Provides consistent mechanical characteristics
- Achieves high-speed synthesis (RTF < 0.1)
- Supports extensive parameter customization

### Robotic Effects

The audio processor applies several effects for authentic robotic sound:

- **Frequency Filtering**: 300Hz-3kHz bandpass for vintage sound
- **Harmonic Enhancement**: Metallic timbre enhancement
- **Mechanical Artifacts**: Quantization and digital artifacts
- **Amplitude Normalization**: Consistent volume levels

## Troubleshooting

### Common Issues

1. **eSpeak-NG not found**
   - Ensure eSpeak-NG is installed and in PATH
   - Set `DJZ_SPEAK_ESPEAK_PATH` environment variable

2. **Audio playback problems**
   - Install pydub: `pip install pydub`
   - Check system audio configuration

3. **Import errors**
   - Install all dependencies: `pip install -r requirements.txt`
   - Use Python 3.8 or higher

4. **Performance issues**
   - Reduce text length for faster synthesis
   - Check available system memory

### Debug Mode

```bash
python main.py "test" --debug
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ main.py
flake8 src/ main.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- eSpeak-NG project for the formant synthesis engine
- Stephen Hawking and DECtalk for inspiration
- Vintage computer TTS systems for authentic robotic characteristics

## Support

- GitHub Issues: [Report bugs](https://github.com/djz-team/djz-speak/issues)
- Documentation: [Read the docs](https://djz-speak.readthedocs.io/)
- Email: dev@djz-speak.com

---

**DJZ-Speak v0** - Bringing authentic robotic voices to the command line.
