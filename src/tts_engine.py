"""
Core TTS engine for DJZ-Speak using eSpeak-NG
"""

import io
import logging
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any, Union
import os
import shutil

try:
    import espeak_ng
    ESPEAK_NG_PYTHON_AVAILABLE = True
except ImportError:
    ESPEAK_NG_PYTHON_AVAILABLE = False

from src.config_manager import ConfigManager
from src.voice_manager import VoiceManager
from src.audio_processor import AudioProcessor
from src.utils import normalize_text, clamp


class TTSEngine:
    """Core text-to-speech engine using eSpeak-NG."""
    
    def __init__(self, config_manager: ConfigManager, voice_manager: VoiceManager):
        """Initialize TTS engine."""
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.voice_manager = voice_manager
        self.audio_processor = AudioProcessor(config_manager)
        
        # Engine state
        self.current_speed = config_manager.get('synthesis', 'speed', 140)
        self.current_pitch = config_manager.get('synthesis', 'pitch', 35)
        self.current_amplitude = config_manager.get('synthesis', 'amplitude', 100)
        self.current_gap = config_manager.get('synthesis', 'gap', 8)
        
        # Performance tracking
        self.synthesis_stats = {
            'total_syntheses': 0,
            'total_time': 0.0,
            'average_rtf': 0.0
        }
        
        # Initialize eSpeak-NG
        self._initialize_espeak()
    
    def _initialize_espeak(self):
        """Initialize eSpeak-NG engine."""
        self.espeak_method = None
        self.espeak_path = None
        
        # Try Python library first
        if ESPEAK_NG_PYTHON_AVAILABLE:
            try:
                espeak_ng.initialize()
                self.espeak_method = 'python'
                self.logger.info("Initialized eSpeak-NG Python library")
                return
            except Exception as e:
                self.logger.warning(f"Failed to initialize eSpeak-NG Python library: {e}")
        
        # Fall back to subprocess
        self.espeak_path = self._find_espeak_executable()
        if self.espeak_path:
            self.espeak_method = 'subprocess'
            self.logger.info(f"Using eSpeak-NG executable: {self.espeak_path}")
        else:
            self.logger.error("eSpeak-NG not found. Please install eSpeak-NG.")
            raise RuntimeError("eSpeak-NG not available")
    
    def _find_espeak_executable(self) -> Optional[str]:
        """Find eSpeak-NG executable."""
        # Check config first
        config_path = self.config_manager.get_espeak_path()
        if config_path and Path(config_path).exists():
            return config_path
        
        # Common executable names
        executable_names = ['espeak-ng', 'espeak']
        
        # Check if in PATH
        for name in executable_names:
            path = shutil.which(name)
            if path:
                return path
        
        # Check common installation paths
        common_paths = [
            '/usr/bin/espeak-ng',
            '/usr/local/bin/espeak-ng',
            '/opt/espeak-ng/bin/espeak-ng',
            'C:\\Program Files\\eSpeak NG\\espeak-ng.exe',
            'C:\\Program Files (x86)\\eSpeak NG\\espeak-ng.exe',
        ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
        
        return None
    
    def synthesize(self, text: str) -> Optional[bytes]:
        """Synthesize text to audio."""
        if not text or not text.strip():
            self.logger.warning("Empty text provided for synthesis")
            return None
        
        start_time = time.time()
        
        try:
            # Normalize text
            normalized_text = normalize_text(text)
            
            # Get voice parameters
            voice_params = self.voice_manager.get_espeak_parameters()
            
            # Synthesize audio
            if self.espeak_method == 'python':
                audio_data = self._synthesize_python(normalized_text, voice_params)
            elif self.espeak_method == 'subprocess':
                audio_data = self._synthesize_subprocess(normalized_text, voice_params)
            else:
                self.logger.error("No eSpeak-NG method available")
                return None
            
            # Update statistics
            synthesis_time = time.time() - start_time
            self._update_stats(synthesis_time, len(normalized_text))
            
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Error during synthesis: {e}")
            return None
    
    def _synthesize_python(self, text: str, voice_params: Dict[str, Any]) -> Optional[bytes]:
        """Synthesize using eSpeak-NG Python library."""
        try:
            # Set voice parameters
            espeak_ng.set_parameter("voice", voice_params.get('voice', 'en'))
            espeak_ng.set_parameter("speed", voice_params.get('speed', 140))
            espeak_ng.set_parameter("pitch", voice_params.get('pitch', 35))
            espeak_ng.set_parameter("amplitude", voice_params.get('amplitude', 100))
            espeak_ng.set_parameter("gap", voice_params.get('gap', 8))
            
            # Set variant if specified
            variant = voice_params.get('variant')
            if variant:
                espeak_ng.set_parameter("variant", variant)
            
            # Synthesize to WAV data
            audio_data = espeak_ng.synth_wav(text)
            
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Error in Python synthesis: {e}")
            return None
    
    def _synthesize_subprocess(self, text: str, voice_params: Dict[str, Any]) -> Optional[bytes]:
        """Synthesize using eSpeak-NG subprocess."""
        try:
            # Build command
            cmd = [
                self.espeak_path,
                '-v', f"{voice_params.get('voice', 'en')}+{voice_params.get('variant', 'm3')}",
                '-s', str(voice_params.get('speed', 140)),
                '-p', str(voice_params.get('pitch', 35)),
                '-a', str(voice_params.get('amplitude', 100)),
                '-g', str(voice_params.get('gap', 8)),
                '--stdout'
            ]
            
            # Add text
            cmd.append(text)
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                check=True
            )
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            self.logger.error("eSpeak-NG synthesis timed out")
            return None
        except subprocess.CalledProcessError as e:
            self.logger.error(f"eSpeak-NG process failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error in subprocess synthesis: {e}")
            return None
    
    def _update_stats(self, synthesis_time: float, text_length: int):
        """Update synthesis performance statistics."""
        self.synthesis_stats['total_syntheses'] += 1
        self.synthesis_stats['total_time'] += synthesis_time
        
        # Calculate Real-Time Factor (RTF)
        # Estimate audio duration (rough calculation)
        estimated_audio_duration = text_length / (self.current_speed / 60.0 * 5)  # ~5 chars per word
        rtf = synthesis_time / max(estimated_audio_duration, 0.1)
        
        # Update average RTF
        total_syntheses = self.synthesis_stats['total_syntheses']
        current_avg = self.synthesis_stats['average_rtf']
        self.synthesis_stats['average_rtf'] = (current_avg * (total_syntheses - 1) + rtf) / total_syntheses
        
        self.logger.debug(f"Synthesis time: {synthesis_time:.3f}s, RTF: {rtf:.3f}")
    
    def set_speed(self, speed: int):
        """Set speech speed in words per minute."""
        self.current_speed = clamp(speed, 80, 300)
        self.voice_manager.update_parameter('speed', self.current_speed)
        self.logger.debug(f"Set speed to {self.current_speed} WPM")
    
    def set_pitch(self, pitch: int):
        """Set pitch level (0-99)."""
        self.current_pitch = clamp(pitch, 0, 99)
        self.voice_manager.update_parameter('pitch', self.current_pitch)
        self.logger.debug(f"Set pitch to {self.current_pitch}")
    
    def set_amplitude(self, amplitude: int):
        """Set amplitude/volume level (0-200)."""
        self.current_amplitude = clamp(amplitude, 0, 200)
        self.voice_manager.update_parameter('amplitude', self.current_amplitude)
        self.logger.debug(f"Set amplitude to {self.current_amplitude}")
    
    def set_gap(self, gap: int):
        """Set word gap in 10ms units."""
        self.current_gap = clamp(gap, 0, 100)
        self.voice_manager.update_parameter('gap', self.current_gap)
        self.logger.debug(f"Set gap to {self.current_gap}")
    
    def play_audio(self, audio_data: bytes) -> bool:
        """Play audio data."""
        return self.audio_processor.play_audio(audio_data)
    
    def save_audio(self, audio_data: bytes, output_path: str, format: str = 'wav') -> bool:
        """Save audio data to file."""
        return self.audio_processor.save_audio(audio_data, output_path, format)
    
    def apply_robotic_effects(self, audio_data: bytes):
        """Apply robotic effects to audio."""
        audio_segment = self.audio_processor.apply_robotic_effects(audio_data)
        if audio_segment:
            # Convert back to bytes
            output_buffer = io.BytesIO()
            audio_segment.export(output_buffer, format='wav')
            return output_buffer.getvalue()
        return audio_data
    
    def synthesize_to_file(self, text: str, output_path: str, format: str = 'wav', apply_effects: bool = False) -> bool:
        """Synthesize text directly to file."""
        try:
            # Synthesize audio
            audio_data = self.synthesize(text)
            if not audio_data:
                return False
            
            # Apply effects if requested
            if apply_effects:
                audio_data = self.apply_robotic_effects(audio_data)
            
            # Save to file
            return self.save_audio(audio_data, output_path, format)
            
        except Exception as e:
            self.logger.error(f"Error synthesizing to file: {e}")
            return False
    
    def batch_synthesize(self, texts: list, output_dir: str, format: str = 'wav', apply_effects: bool = False) -> Dict[str, bool]:
        """Synthesize multiple texts to files."""
        results = {}
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for i, text in enumerate(texts):
            try:
                filename = f"synthesis_{i+1:03d}.{format}"
                file_path = output_path / filename
                
                success = self.synthesize_to_file(text, str(file_path), format, apply_effects)
                results[filename] = success
                
                if success:
                    self.logger.debug(f"Synthesized: {filename}")
                else:
                    self.logger.warning(f"Failed to synthesize: {filename}")
                    
            except Exception as e:
                self.logger.error(f"Error in batch synthesis for text {i+1}: {e}")
                results[f"synthesis_{i+1:03d}.{format}"] = False
        
        return results
    
    def get_synthesis_info(self) -> Dict[str, Any]:
        """Get information about synthesis engine."""
        return {
            'method': self.espeak_method,
            'espeak_path': self.espeak_path,
            'current_voice': self.voice_manager.get_current_voice_name(),
            'parameters': {
                'speed': self.current_speed,
                'pitch': self.current_pitch,
                'amplitude': self.current_amplitude,
                'gap': self.current_gap
            },
            'statistics': self.synthesis_stats.copy(),
            'available_voices': self.voice_manager.list_voices()
        }
    
    def test_synthesis(self) -> bool:
        """Test synthesis functionality."""
        test_text = "Hello, this is a test of the DJZ-Speak synthesis engine."
        
        try:
            audio_data = self.synthesize(test_text)
            if audio_data and len(audio_data) > 0:
                self.logger.info("Synthesis test successful")
                return True
            else:
                self.logger.error("Synthesis test failed: no audio data")
                return False
                
        except Exception as e:
            self.logger.error(f"Synthesis test failed: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.synthesis_stats
        
        return {
            'total_syntheses': stats['total_syntheses'],
            'total_time': stats['total_time'],
            'average_rtf': stats['average_rtf'],
            'performance_rating': self._get_performance_rating(stats['average_rtf']),
            'target_rtf': self.config_manager.get('performance', 'real_time_factor_target', 0.5)
        }
    
    def _get_performance_rating(self, rtf: float) -> str:
        """Get performance rating based on RTF."""
        if rtf < 0.1:
            return "Excellent"
        elif rtf < 0.3:
            return "Very Good"
        elif rtf < 0.5:
            return "Good"
        elif rtf < 1.0:
            return "Acceptable"
        else:
            return "Poor"
    
    def reset_statistics(self):
        """Reset synthesis statistics."""
        self.synthesis_stats = {
            'total_syntheses': 0,
            'total_time': 0.0,
            'average_rtf': 0.0
        }
        self.logger.info("Reset synthesis statistics")
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            if self.espeak_method == 'python' and ESPEAK_NG_PYTHON_AVAILABLE:
                espeak_ng.terminate()
            self.logger.debug("TTS engine cleanup completed")
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor."""
        self.cleanup()
