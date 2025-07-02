#!/usr/bin/env python3
"""
Basic functionality test for DJZ-Speak
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from src.config_manager import ConfigManager
        from src.voice_manager import VoiceManager
        from src.audio_processor import AudioProcessor
        from src.tts_engine import TTSEngine
        from src.utils import validate_text_input, normalize_text
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("Testing configuration...")
    
    try:
        from src.config_manager import ConfigManager
        config = ConfigManager()
        
        # Test basic config access
        speed = config.get('synthesis', 'speed', 140)
        voice = config.get('synthesis', 'voice', 'classic_robot')
        
        print(f"✓ Configuration loaded - Speed: {speed}, Voice: {voice}")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_voice_manager():
    """Test voice management."""
    print("Testing voice manager...")
    
    try:
        from src.config_manager import ConfigManager
        from src.voice_manager import VoiceManager
        
        config = ConfigManager()
        voice_manager = VoiceManager(config)
        
        # Test voice listing
        voices = voice_manager.list_voices()
        print(f"✓ Found {len(voices)} voice presets: {', '.join(voices[:3])}...")
        
        # Test voice setting
        if voice_manager.set_voice('classic_robot'):
            current = voice_manager.get_current_voice_name()
            print(f"✓ Set voice to: {current}")
        
        return True
    except Exception as e:
        print(f"✗ Voice manager error: {e}")
        return False

def test_text_validation():
    """Test text validation utilities."""
    print("Testing text validation...")
    
    try:
        from src.utils import validate_text_input, normalize_text
        
        # Test valid text
        valid_texts = [
            "Hello world",
            "This is a test.",
            "Numbers 123 and symbols!",
        ]
        
        for text in valid_texts:
            if not validate_text_input(text):
                print(f"✗ Valid text rejected: {text}")
                return False
        
        # Test text normalization
        normalized = normalize_text("  Multiple   spaces  ")
        if "Multiple spaces" not in normalized:
            print(f"✗ Text normalization failed: {normalized}")
            return False
        
        print("✓ Text validation working correctly")
        return True
    except Exception as e:
        print(f"✗ Text validation error: {e}")
        return False

def test_audio_processor():
    """Test audio processor initialization."""
    print("Testing audio processor...")
    
    try:
        from src.config_manager import ConfigManager
        from src.audio_processor import AudioProcessor
        
        config = ConfigManager()
        processor = AudioProcessor(config)
        
        print("✓ Audio processor initialized")
        return True
    except Exception as e:
        print(f"✗ Audio processor error: {e}")
        return False

def main():
    """Run basic tests."""
    print("DJZ-Speak Basic Functionality Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_configuration,
        test_voice_manager,
        test_text_validation,
        test_audio_processor,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            print()
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All basic tests passed!")
        print("\nDJZ-Speak appears to be correctly installed.")
        print("Try running: python main.py --list-voices")
        return 0
    else:
        print("✗ Some tests failed.")
        print("Check the error messages above and ensure all dependencies are installed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
