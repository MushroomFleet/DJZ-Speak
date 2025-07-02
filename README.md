# DJZ-Speak rev2: Robotic Text-to-Speech Tool

DJZ-Speak is a high-performance command-line text-to-speech tool that leverages eSpeak-NG's formant synthesis engine to generate authentic machine-like robotic voices. The tool automatically saves all synthesized audio to an organized output directory while providing real-time playback, making it perfect for creating robotic voice content, accessibility applications, and vintage computer sound effects.

## Features

- **8 Distinct Robotic Voice Presets**: Classic Robot, DECtalk Style, Dr. Sbaitso, HAL 9000, C-3PO Style, Vintage Computer, Modern AI, and Robotic Female
- **Automatic Output Management**: All audio automatically saved to `./output/` directory with timestamped filenames
- **Real-Time Synthesis**: RTF < 0.5 for responsive speech generation
- **Interactive Mode**: Real-time parameter adjustment and voice switching
- **Batch Processing**: Process multiple texts efficiently with organized file output
- **Audio Effects**: Robotic enhancement filters and mechanical artifacts
- **Cross-Platform**: Windows, Linux, and macOS support
- **Multiple Output Formats**: WAV and MP3 support
- **Smart Filename Generation**: Automatic timestamped naming based on input text

## Installation

> **⚠️ Important:** DJZ-Speak rev2 includes bug fixes and stability improvements. We **strongly recommend** using a virtual environment to avoid conflicts with your system Python packages.

### Step 1: Set Up Virtual Environment (Recommended)

**Why use a virtual environment?**
- Prevents conflicts between DJZ-Speak dependencies and your system Python packages
- Keeps your system Python environment clean and stable
- Allows easy removal of DJZ-Speak without affecting other projects
- Enables reproducible installations across different systems

#### Create and activate virtual environment:

**Windows:**
```bash
# Create virtual environment
python -m venv djz-speak-env

# Activate virtual environment
djz-speak-env\Scripts\activate

# You should see (djz-speak-env) in your command prompt
```

**Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv djz-speak-env

# Activate virtual environment
source djz-speak-env/bin/activate

# You should see (djz-speak-env) in your terminal prompt
```

> **Note:** You'll need to activate the virtual environment every time you want to use DJZ-Speak. To deactivate, simply run `deactivate`.

### Step 2: Install Prerequisites

1. **Python 3.8 or higher** (should already be available if you created the venv)
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

### Step 3: Install DJZ-Speak

**With virtual environment activated:**
```bash
# Clone the repository
git clone https://github.com/djz-team/djz-speak.git
cd djz-speak

# Install dependencies (in virtual environment)
pip install -r requirements.txt

# Optional: Install in development mode
pip install -e .
```

### Alternative: System-Wide Installation (Advanced Users)

If you prefer to install system-wide (not recommended for most users):

```bash
# Clone the repository
git clone https://github.com/djz-team/djz-speak.git
cd djz-speak

# Install dependencies system-wide
pip install -r requirements.txt

# Optional: Install in development mode
pip install -e .
```

> **Warning:** System-wide installation may cause package conflicts. Use virtual environment installation for better stability.

## Quick Start

### Basic Usage

```bash
# Simple text synthesis (automatically saves to ./output/ + plays audio)
python main.py "Hello, I am a robot"
# Creates: ./output/djz_speak_Hello_I_20250702_203045.wav

# Use a specific voice preset
python main.py "Greetings, human" --voice dectalk
# Creates: ./output/djz_speak_Greetings_human_20250702_203046.wav

# Save to custom location (overrides default output)
python main.py "Test message" --output robot.wav
# Creates: robot.wav (in current directory)

# Apply robotic effects
python main.py "Enhanced voice" --effects
# Creates: ./output/djz_speak_Enhanced_voice_20250702_203047.wav (with effects)

# Synthesis without audio playback
python main.py "Silent generation" --no-play
# Creates: ./output/djz_speak_Silent_generation_20250702_203048.wav (no audio playback)
```

### Output Behavior

**Default Behavior**: DJZ-Speak automatically saves all synthesized audio to the `./output/` directory with timestamped filenames while also playing the audio through your speakers.

- **Automatic saving**: Every synthesis creates a WAV file in `./output/`
- **Smart naming**: Files named like `djz_speak_[text]_[timestamp].wav`
- **Directory creation**: The `./output/` folder is created automatically if it doesn't exist
- **Custom output**: Use `--output filename.wav` to save to a specific location instead
- **Playback control**: Use `--no-play` to disable audio playback (file still saved)

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

### Key Configuration Options

**Output Settings** (`config/settings.yaml`):
```yaml
output:
  default_format: "wav"
  quality: "high"
  normalize_audio: true
  default_output_directory: "output"  # Directory for automatic file saving
```

**Synthesis Parameters**:
```yaml
synthesis:
  speed: 140          # Words per minute (80-300)
  pitch: 35           # Pitch level (0-99)
  amplitude: 100      # Volume level (0-200)
  gap: 8              # Word gap in 10ms units
  voice: "classic_robot"
```

### Environment Variables

- `DJZ_SPEAK_SPEED` - Default speech speed
- `DJZ_SPEAK_PITCH` - Default pitch level
- `DJZ_SPEAK_VOICE` - Default voice preset
- `DJZ_SPEAK_ESPEAK_PATH` - Custom eSpeak-NG path

### Customizing Output Directory

To change the default output directory, edit `config/settings.yaml`:

```yaml
output:
  default_output_directory: "my_audio_files"  # Relative to project root
  # Or use absolute path:
  # default_output_directory: "/home/user/audio"
```

The directory will be created automatically if it doesn't exist.

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
│   ├── config_manager.py  # Configuration & output management
│   └── utils.py           # Utilities & filename generation
├── config/                # Configuration files
├── output/                # Default audio output directory (auto-created)
├── build/                 # Build scripts
└── requirements.txt       # Dependencies
```

### Output Management System

DJZ-Speak implements automatic file management with the following components:

**ConfigManager** (`src/config_manager.py`):
- `get_default_output_directory()` - Returns configured output directory path
- Automatic directory creation with `mkdir(parents=True, exist_ok=True)`
- Supports both relative and absolute paths
- Configurable via `config/settings.yaml`

**Filename Generation** (`src/utils.py`):
- `generate_timestamped_filename()` - Creates unique filenames with timestamps
- Format: `djz_speak_[text_words]_YYYYMMDD_HHMMSS.wav`
- Text sanitization for cross-platform compatibility
- Automatic truncation for long text inputs

**CLI Integration** (`main.py`):
- Default behavior: Always save to output directory + play audio
- Override behavior: `--output` parameter bypasses default directory
- Playback control: `--no-play` disables audio while preserving file saving

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

5. **Output directory issues**
   - Check write permissions for the project directory
   - Verify `default_output_directory` setting in `config/settings.yaml`
   - Use absolute paths if relative paths cause issues
   - Check available disk space

### Debug Mode

```bash
python main.py "test" --debug
```

## Developer Notes

### Key Implementation Details

**Automatic Output Management**:
- Every synthesis operation creates a file, even without explicit `--output`
- The `ConfigManager.get_default_output_directory()` method handles path resolution
- Directory creation is automatic and safe with `mkdir(parents=True, exist_ok=True)`
- Filename generation uses sanitized text + timestamp for uniqueness

**Backward Compatibility**:
- Existing `--output` parameter behavior is preserved
- No breaking changes to CLI interface
- Configuration files maintain existing structure

**File Naming Strategy**:
- Pattern: `djz_speak_[sanitized_text]_YYYYMMDD_HHMMSS.wav`
- Text is limited to first 2 words, max 20 characters
- Cross-platform filename sanitization removes invalid characters
- Timestamp ensures uniqueness even for identical text

**Configuration Integration**:
- New `default_output_directory` setting in `output` section
- Supports both relative (to project root) and absolute paths
- Environment variable overrides available for automation
- User config files can override defaults

### Extending the Output System

To modify output behavior:

1. **Custom filename patterns**: Edit `generate_timestamped_filename()` in `src/utils.py`
2. **Different default directory**: Modify `config/settings.yaml` or use environment variables
3. **Additional output formats**: Extend the format handling in `src/tts_engine.py`
4. **Metadata embedding**: Add file metadata in the audio processor

### Testing Output Functionality

```bash
# Test default output
python main.py "Test message"
ls output/  # Should show djz_speak_Test_message_*.wav

# Test custom output (should not use default directory)
python main.py "Custom test" --output custom.wav
ls custom.wav  # Should exist in current directory

# Test directory creation
rm -rf output/
python main.py "Directory test"  # Should recreate output/ directory
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

**DJZ-Speak rev2** - Bringing authentic robotic voices to the command line.
