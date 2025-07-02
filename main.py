#!/usr/bin/env python3
"""
DJZ-Speak v0: Command-line TTS tool with robotic voice synthesis
"""

import sys
import argparse
import os
from pathlib import Path
from typing import Optional

# Import core modules
from src.tts_engine import TTSEngine
from src.config_manager import ConfigManager
from src.voice_manager import VoiceManager
from src.utils import setup_logging, validate_text_input, generate_timestamped_filename


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="DJZ-Speak: Robotic Text-to-Speech Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Hello, I am a robot"
  python main.py -i
  python main.py "Text" --voice dectalk --speed 120 --output robot.wav
  python main.py --text-file input.txt --batch-output ./audio/
        """
    )
    
    # Input options
    parser.add_argument('text', nargs='?', help='Text to synthesize')
    parser.add_argument('-i', '--interactive', action='store_true', 
                       help='Interactive mode')
    parser.add_argument('--text-file', help='Read text from file')
    parser.add_argument('--stdin', action='store_true', 
                       help='Read text from stdin')
    
    # Voice and synthesis options
    parser.add_argument('--voice', default='classic_robot', 
                       help='Voice preset (default: classic_robot)')
    parser.add_argument('--speed', type=int, default=140, 
                       help='Speech speed WPM (80-300, default: 140)')
    parser.add_argument('--pitch', type=int, default=35, 
                       help='Pitch level (0-99, default: 35)')
    parser.add_argument('--amplitude', type=int, default=100, 
                       help='Volume level (0-200, default: 100)')
    parser.add_argument('--gap', type=int, default=8, 
                       help='Word gap in 10ms units (default: 8)')
    
    # Output options
    parser.add_argument('--output', '-o', help='Output WAV file path')
    parser.add_argument('--batch-output', help='Directory for batch file output')
    parser.add_argument('--play', action='store_true', default=True,
                       help='Play audio (default: enabled)')
    parser.add_argument('--no-play', dest='play', action='store_false',
                       help='Disable audio playback')
    parser.add_argument('--format', choices=['wav', 'mp3'], default='wav',
                       help='Audio format (default: wav)')
    
    # Configuration options
    parser.add_argument('--config', help='Custom configuration file')
    parser.add_argument('--list-voices', action='store_true',
                       help='List available voice presets')
    parser.add_argument('--voice-info', help='Show voice preset details')
    
    # Advanced options
    parser.add_argument('--effects', action='store_true',
                       help='Apply robotic audio effects')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress all output except errors')
    
    return parser


def interactive_mode(engine: TTSEngine, voice_manager: VoiceManager):
    """Run interactive TTS session."""
    print("DJZ-Speak Interactive Mode")
    print("Commands: !voice <preset>, !speed <wpm>, !pitch <level>, !quit")
    print("Enter text to synthesize, or type !quit to exit\n")
    
    current_voice = voice_manager.get_current_voice()
    print(f"Current voice: {current_voice['name']}")
    
    try:
        while True:
            try:
                text = input("DJZ> ").strip()
                
                if not text:
                    continue
                
                # Handle commands
                if text.startswith('!'):
                    handle_interactive_command(text, engine, voice_manager)
                    continue
                
                # Synthesize text
                if validate_text_input(text):
                    audio_data = engine.synthesize(text)
                    engine.play_audio(audio_data)
                else:
                    print("Invalid text input")
                    
            except KeyboardInterrupt:
                print("\nUse !quit to exit")
            except EOFError:
                break
                
    except Exception as e:
        print(f"Interactive mode error: {e}")
    
    print("\nGoodbye!")


def handle_interactive_command(command: str, engine: TTSEngine, voice_manager: VoiceManager):
    """Handle interactive commands."""
    parts = command[1:].split()
    cmd = parts[0].lower()
    
    if cmd == 'quit' or cmd == 'exit':
        sys.exit(0)
    elif cmd == 'voice' and len(parts) > 1:
        voice_name = parts[1]
        if voice_manager.set_voice(voice_name):
            print(f"Voice changed to: {voice_name}")
        else:
            print(f"Voice '{voice_name}' not found")
            print("Available voices:", ", ".join(voice_manager.list_voices()))
    elif cmd == 'speed' and len(parts) > 1:
        try:
            speed = int(parts[1])
            if 80 <= speed <= 300:
                engine.set_speed(speed)
                print(f"Speed set to: {speed} WPM")
            else:
                print("Speed must be between 80-300 WPM")
        except ValueError:
            print("Invalid speed value")
    elif cmd == 'pitch' and len(parts) > 1:
        try:
            pitch = int(parts[1])  
            if 0 <= pitch <= 99:
                engine.set_pitch(pitch)
                print(f"Pitch set to: {pitch}")
            else:
                print("Pitch must be between 0-99")
        except ValueError:
            print("Invalid pitch value")
    elif cmd == 'help':
        print("Commands:")
        print("  !voice <preset>  - Change voice preset")
        print("  !speed <wpm>     - Set speech speed (80-300)")
        print("  !pitch <level>   - Set pitch level (0-99)")
        print("  !quit            - Exit interactive mode")
    else:
        print(f"Unknown command: {cmd}")


def process_batch_files(engine: TTSEngine, text_file: str, output_dir: str):
    """Process multiple texts from file."""
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with open(text_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        for i, text in enumerate(lines, 1):
            if validate_text_input(text):
                print(f"Processing line {i}/{len(lines)}: {text[:50]}...")
                audio_data = engine.synthesize(text)
                
                output_file = output_path / f"line_{i:03d}.wav"
                engine.save_audio(audio_data, str(output_file))
                print(f"Saved: {output_file}")
            else:
                print(f"Skipping invalid text on line {i}")
                
        print(f"Batch processing complete. {len(lines)} files processed.")
        
    except Exception as e:
        print(f"Batch processing error: {e}")
        sys.exit(1)


def main():
    """Main application entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    log_level = 'DEBUG' if args.debug else 'INFO'
    if args.quiet:
        log_level = 'ERROR'
    setup_logging(log_level)
    
    try:
        # Initialize components
        config_manager = ConfigManager(args.config)
        voice_manager = VoiceManager(config_manager)
        engine = TTSEngine(config_manager, voice_manager)
        
        # Handle special commands
        if args.list_voices:
            voices = voice_manager.list_voices()
            print("Available voice presets:")
            for voice in voices:
                preset = voice_manager.get_voice(voice)
                print(f"  {voice}: {preset.get('description', 'Custom robotic voice')}")
            return
        
        if args.voice_info:
            preset = voice_manager.get_voice(args.voice_info)
            if preset:
                print(f"Voice preset: {args.voice_info}")
                for key, value in preset.items():
                    print(f"  {key}: {value}")
            else:
                print(f"Voice preset '{args.voice_info}' not found")
            return
        
        # Set voice and parameters
        if not voice_manager.set_voice(args.voice):
            print(f"Warning: Voice '{args.voice}' not found, using default")
        
        engine.set_speed(args.speed)
        engine.set_pitch(args.pitch)
        engine.set_amplitude(args.amplitude)
        engine.set_gap(args.gap)
        
        # Determine input source
        text_input = None
        
        if args.interactive:
            interactive_mode(engine, voice_manager)
            return
        elif args.text:
            text_input = args.text
        elif args.text_file:
            if args.batch_output:
                process_batch_files(engine, args.text_file, args.batch_output)
                return
            else:
                with open(args.text_file, 'r', encoding='utf-8') as f:
                    text_input = f.read().strip()
        elif args.stdin:
            text_input = sys.stdin.read().strip()
        else:
            print("Error: No text input provided. Use -h for help.")
            sys.exit(1)
        
        # Validate and process text
        if not validate_text_input(text_input):
            print("Error: Invalid text input")
            sys.exit(1)
        
        print(f"Synthesizing: {text_input[:100]}{'...' if len(text_input) > 100 else ''}")
        
        # Generate audio
        audio_data = engine.synthesize(text_input)
        
        # Apply effects if requested
        if args.effects:
            audio_data = engine.apply_robotic_effects(audio_data)
        
        # Handle output - always save to default directory if no output specified
        output_path = args.output
        if not output_path:
            # Generate default output path
            default_output_dir = config_manager.get_default_output_directory()
            filename = generate_timestamped_filename(text_input, args.format)
            output_path = default_output_dir / filename
            
            # Ensure the output directory exists and is writable
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                if not args.quiet:
                    print(f"Using default output directory: {output_path.parent}")
            except PermissionError:
                print(f"Error: Cannot create output directory {output_path.parent}")
                print("Check permissions or specify a different output path with --output")
                sys.exit(1)
        else:
            # User specified output path - ensure directory exists
            output_path = Path(output_path)
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                print(f"Error: Cannot create directory {output_path.parent}")
                print("Check permissions or choose a different output path")
                sys.exit(1)
        
        # Validate output path is not in temp directory
        temp_indicators = ['temp', 'tmp', 'AppData\\Local\\Temp', 'AppData/Local/Temp']
        output_str = str(output_path).lower()
        if any(indicator in output_str for indicator in temp_indicators):
            print(f"Warning: Output path appears to be in temp directory: {output_path}")
            print("This might indicate a configuration issue.")
        
        # Save audio file
        success = engine.save_audio(audio_data, str(output_path), args.format)
        if success:
            # Verify file was actually created at the expected location
            if output_path.exists():
                print(f"Audio saved to: {output_path.resolve()}")
            else:
                print(f"Warning: Audio save reported success but file not found at: {output_path}")
        else:
            print(f"Error: Failed to save audio to {output_path}")
            sys.exit(1)
        
        if args.play:
            engine.play_audio(audio_data)
        
        print("Synthesis complete!")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
