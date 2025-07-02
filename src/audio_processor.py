"""
Audio processing and effects for DJZ-Speak
"""

import io
import logging
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, Union
import tempfile
import os

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.playback import play
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

try:
    import scipy.signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class AudioProcessor:
    """Handles audio processing, effects, and output for DJZ-Speak."""
    
    def __init__(self, config_manager):
        """Initialize audio processor."""
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.audio_params = config_manager.get_audio_params()
        self.effects_params = config_manager.get_effects_params()
        
        # Check dependencies
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check for required audio processing dependencies."""
        missing_deps = []
        
        if not SOUNDFILE_AVAILABLE:
            missing_deps.append("soundfile")
        if not PYDUB_AVAILABLE:
            missing_deps.append("pydub")
        if not SCIPY_AVAILABLE:
            missing_deps.append("scipy")
        
        if missing_deps:
            self.logger.warning(f"Missing audio dependencies: {', '.join(missing_deps)}")
            self.logger.warning("Some audio features may not be available")
    
    def load_audio_from_wav_data(self, wav_data: bytes) -> Optional[AudioSegment]:
        """Load audio from WAV byte data."""
        if not PYDUB_AVAILABLE:
            self.logger.error("pydub not available for audio loading")
            return None
        
        try:
            # Create AudioSegment from WAV bytes
            audio = AudioSegment.from_wav(io.BytesIO(wav_data))
            return audio
        except Exception as e:
            self.logger.error(f"Error loading audio from WAV data: {e}")
            return None
    
    def save_audio(self, audio_data: Union[bytes, AudioSegment], output_path: str, format: str = 'wav') -> bool:
        """Save audio data to file."""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(audio_data, bytes):
                # Raw WAV bytes - save directly
                if format.lower() == 'wav':
                    with open(output_path, 'wb') as f:
                        f.write(audio_data)
                    return True
                else:
                    # Convert to AudioSegment for format conversion
                    if not PYDUB_AVAILABLE:
                        self.logger.error("pydub required for format conversion")
                        return False
                    
                    audio = AudioSegment.from_wav(io.BytesIO(audio_data))
                    audio.export(output_path, format=format)
                    return True
            
            elif isinstance(audio_data, AudioSegment):
                # AudioSegment object
                audio_data.export(output_path, format=format)
                return True
            
            else:
                self.logger.error(f"Unsupported audio data type: {type(audio_data)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error saving audio to {output_path}: {e}")
            return False
    
    def play_audio(self, audio_data: Union[bytes, AudioSegment]) -> bool:
        """Play audio data."""
        if not PYDUB_AVAILABLE:
            self.logger.error("pydub not available for audio playback")
            return False
        
        try:
            if isinstance(audio_data, bytes):
                audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            elif isinstance(audio_data, AudioSegment):
                audio = audio_data
            else:
                self.logger.error(f"Unsupported audio data type: {type(audio_data)}")
                return False
            
            # Play audio
            play(audio)
            return True
            
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
            return False
    
    def apply_robotic_effects(self, audio_data: Union[bytes, AudioSegment]) -> Optional[AudioSegment]:
        """Apply robotic effects to audio."""
        if not PYDUB_AVAILABLE:
            self.logger.error("pydub not available for effects processing")
            return None
        
        try:
            # Convert to AudioSegment if needed
            if isinstance(audio_data, bytes):
                audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            elif isinstance(audio_data, AudioSegment):
                audio = audio_data
            else:
                self.logger.error(f"Unsupported audio data type: {type(audio_data)}")
                return None
            
            # Apply frequency filtering
            if self.effects_params.get('frequency_filter', {}).get('enable', True):
                audio = self._apply_frequency_filter(audio)
            
            # Apply harmonic enhancement
            enhancement = self.effects_params.get('harmonic_enhancement', 1.0)
            if enhancement != 1.0:
                audio = self._apply_harmonic_enhancement(audio, enhancement)
            
            # Apply mechanical artifacts
            if self.effects_params.get('mechanical_artifacts', True):
                audio = self._apply_mechanical_artifacts(audio)
            
            return audio
            
        except Exception as e:
            self.logger.error(f"Error applying robotic effects: {e}")
            return None
    
    def _apply_frequency_filter(self, audio: AudioSegment) -> AudioSegment:
        """Apply frequency filtering for robotic sound."""
        try:
            filter_params = self.effects_params.get('frequency_filter', {})
            low_cutoff = filter_params.get('low_cutoff', 300)
            high_cutoff = filter_params.get('high_cutoff', 3000)
            
            # Apply high-pass filter (remove low frequencies)
            if low_cutoff > 0:
                audio = audio.high_pass_filter(low_cutoff)
            
            # Apply low-pass filter (remove high frequencies)
            if high_cutoff < 20000:
                audio = audio.low_pass_filter(high_cutoff)
            
            return audio
            
        except Exception as e:
            self.logger.warning(f"Error applying frequency filter: {e}")
            return audio
    
    def _apply_harmonic_enhancement(self, audio: AudioSegment, factor: float) -> AudioSegment:
        """Apply harmonic enhancement for metallic sound."""
        try:
            if not SCIPY_AVAILABLE:
                self.logger.warning("scipy not available for harmonic enhancement")
                return audio
            
            # Convert to numpy array
            samples = np.array(audio.get_array_of_samples())
            
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                # Process each channel
                for i in range(2):
                    channel_samples = samples[:, i]
                    enhanced = self._enhance_harmonics(channel_samples, factor)
                    samples[:, i] = enhanced
                samples = samples.flatten()
            else:
                samples = self._enhance_harmonics(samples, factor)
            
            # Convert back to AudioSegment
            enhanced_audio = audio._spawn(samples.tobytes())
            return enhanced_audio
            
        except Exception as e:
            self.logger.warning(f"Error applying harmonic enhancement: {e}")
            return audio
    
    def _enhance_harmonics(self, samples: np.ndarray, factor: float) -> np.ndarray:
        """Enhance harmonics in audio signal."""
        try:
            # Simple harmonic enhancement using distortion
            # Normalize to prevent clipping
            max_val = np.max(np.abs(samples))
            if max_val > 0:
                normalized = samples / max_val
                
                # Apply soft clipping for harmonic distortion
                enhanced = np.tanh(normalized * factor)
                
                # Scale back
                enhanced = enhanced * max_val * 0.8  # Reduce volume slightly
                
                return enhanced.astype(samples.dtype)
            
            return samples
            
        except Exception as e:
            self.logger.warning(f"Error in harmonic enhancement: {e}")
            return samples
    
    def _apply_mechanical_artifacts(self, audio: AudioSegment) -> AudioSegment:
        """Apply mechanical artifacts for robotic sound."""
        try:
            # Add slight quantization effect
            # Reduce bit depth temporarily to create digital artifacts
            
            # Convert to 8-bit and back to create quantization noise
            temp_audio = audio.set_sample_width(1)  # 8-bit
            temp_audio = temp_audio.set_sample_width(audio.sample_width)  # Back to original
            
            # Mix with original (subtle effect)
            mixed = audio.overlay(temp_audio - 20)  # Reduce volume of artifacts
            
            return mixed
            
        except Exception as e:
            self.logger.warning(f"Error applying mechanical artifacts: {e}")
            return audio
    
    def normalize_audio(self, audio: AudioSegment, target_dBFS: float = -20.0) -> AudioSegment:
        """Normalize audio to target level."""
        try:
            # Calculate current peak level
            current_dBFS = audio.dBFS
            
            # Calculate gain needed
            gain = target_dBFS - current_dBFS
            
            # Apply gain
            normalized = audio + gain
            
            return normalized
            
        except Exception as e:
            self.logger.warning(f"Error normalizing audio: {e}")
            return audio
    
    def adjust_speed(self, audio: AudioSegment, speed_factor: float) -> AudioSegment:
        """Adjust audio playback speed."""
        try:
            if speed_factor == 1.0:
                return audio
            
            # Change frame rate to adjust speed
            new_frame_rate = int(audio.frame_rate * speed_factor)
            
            # Create new audio with adjusted frame rate
            adjusted = audio._spawn(
                audio.raw_data,
                overrides={'frame_rate': new_frame_rate}
            )
            
            # Set back to original frame rate to maintain pitch
            adjusted = adjusted.set_frame_rate(audio.frame_rate)
            
            return adjusted
            
        except Exception as e:
            self.logger.warning(f"Error adjusting audio speed: {e}")
            return audio
    
    def add_reverb(self, audio: AudioSegment, room_size: float = 0.3, damping: float = 0.5) -> AudioSegment:
        """Add simple reverb effect."""
        try:
            # Simple reverb using delayed copies
            delay_ms = int(room_size * 100)  # 0-100ms delay
            decay = 1.0 - damping
            
            # Create delayed copy
            delayed = AudioSegment.silent(duration=delay_ms) + audio
            delayed = delayed - (20 * damping)  # Reduce volume based on damping
            
            # Mix with original
            reverb_audio = audio.overlay(delayed)
            
            return reverb_audio
            
        except Exception as e:
            self.logger.warning(f"Error adding reverb: {e}")
            return audio
    
    def get_audio_info(self, audio: AudioSegment) -> Dict[str, Any]:
        """Get information about audio segment."""
        try:
            return {
                'duration_ms': len(audio),
                'duration_seconds': len(audio) / 1000.0,
                'frame_rate': audio.frame_rate,
                'channels': audio.channels,
                'sample_width': audio.sample_width,
                'frame_count': audio.frame_count(),
                'dBFS': audio.dBFS,
                'max_dBFS': audio.max_dBFS
            }
        except Exception as e:
            self.logger.error(f"Error getting audio info: {e}")
            return {}
    
    def trim_silence(self, audio: AudioSegment, silence_thresh: float = -50.0) -> AudioSegment:
        """Trim silence from beginning and end of audio."""
        try:
            # Trim silence from start and end
            trimmed = audio.strip_silence(silence_thresh=silence_thresh)
            return trimmed
        except Exception as e:
            self.logger.warning(f"Error trimming silence: {e}")
            return audio
    
    def fade_in_out(self, audio: AudioSegment, fade_in_ms: int = 50, fade_out_ms: int = 50) -> AudioSegment:
        """Apply fade in and fade out to audio."""
        try:
            # Apply fade in
            if fade_in_ms > 0:
                audio = audio.fade_in(fade_in_ms)
            
            # Apply fade out
            if fade_out_ms > 0:
                audio = audio.fade_out(fade_out_ms)
            
            return audio
        except Exception as e:
            self.logger.warning(f"Error applying fade: {e}")
            return audio
    
    def convert_format(self, audio_data: bytes, input_format: str, output_format: str) -> Optional[bytes]:
        """Convert audio between formats."""
        if not PYDUB_AVAILABLE:
            self.logger.error("pydub not available for format conversion")
            return None
        
        try:
            # Load audio in input format
            if input_format.lower() == 'wav':
                audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            elif input_format.lower() == 'mp3':
                audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            else:
                self.logger.error(f"Unsupported input format: {input_format}")
                return None
            
            # Export in output format
            output_buffer = io.BytesIO()
            audio.export(output_buffer, format=output_format)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error converting audio format: {e}")
            return None
    
    def create_silence(self, duration_ms: int) -> AudioSegment:
        """Create silent audio segment."""
        try:
            return AudioSegment.silent(duration=duration_ms)
        except Exception as e:
            self.logger.error(f"Error creating silence: {e}")
            return None
    
    def concatenate_audio(self, audio_segments: list) -> Optional[AudioSegment]:
        """Concatenate multiple audio segments."""
        try:
            if not audio_segments:
                return None
            
            result = audio_segments[0]
            for segment in audio_segments[1:]:
                result += segment
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error concatenating audio: {e}")
            return None
