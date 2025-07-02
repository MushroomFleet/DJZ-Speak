"""
Utility functions for DJZ-Speak TTS tool
"""

import logging
import re
import sys
from pathlib import Path
from typing import Optional


def setup_logging(level: str = 'INFO'):
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def validate_text_input(text: str) -> bool:
    """Validate text input for TTS synthesis."""
    if not text or not isinstance(text, str):
        return False
    
    # Remove whitespace and check if empty
    text = text.strip()
    if not text:
        return False
    
    # Check for reasonable length (max 10000 characters)
    if len(text) > 10000:
        return False
    
    # Check for valid characters (allow letters, numbers, punctuation, whitespace)
    if not re.match(r'^[\w\s\.,!?;:\'"()\-\[\]{}@#$%^&*+=<>/\\|`~]*$', text):
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility."""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure not empty
    if not filename:
        filename = 'output'
    
    return filename


def ensure_directory(path: str) -> Path:
    """Ensure directory exists, create if necessary."""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max."""
    return max(min_val, min(value, max_val))


def normalize_text(text: str) -> str:
    """Normalize text for better TTS synthesis."""
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Ensure proper sentence endings
    text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
    
    # Add period if text doesn't end with punctuation
    if text and not text[-1] in '.!?':
        text += '.'
    
    return text.strip()


def parse_time_string(time_str: str) -> Optional[float]:
    """Parse time string (e.g., '1.5s', '500ms') to seconds."""
    if not time_str:
        return None
    
    time_str = time_str.lower().strip()
    
    # Parse milliseconds
    if time_str.endswith('ms'):
        try:
            return float(time_str[:-2]) / 1000
        except ValueError:
            return None
    
    # Parse seconds
    if time_str.endswith('s'):
        try:
            return float(time_str[:-1])
        except ValueError:
            return None
    
    # Parse as plain number (assume seconds)
    try:
        return float(time_str)
    except ValueError:
        return None


def get_audio_info(audio_data: bytes) -> dict:
    """Get basic information about audio data."""
    return {
        'size_bytes': len(audio_data),
        'size_kb': len(audio_data) / 1024,
        'estimated_duration': len(audio_data) / (44100 * 2 * 2)  # Rough estimate for 16-bit stereo
    }


class ProgressBar:
    """Simple progress bar for batch operations."""
    
    def __init__(self, total: int, width: int = 50):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, increment: int = 1):
        """Update progress bar."""
        self.current += increment
        self._display()
    
    def _display(self):
        """Display current progress."""
        if self.total == 0:
            return
        
        percent = self.current / self.total
        filled = int(self.width * percent)
        bar = '█' * filled + '░' * (self.width - filled)
        
        print(f'\r[{bar}] {percent:.1%} ({self.current}/{self.total})', end='', flush=True)
        
        if self.current >= self.total:
            print()  # New line when complete


def check_system_requirements() -> dict:
    """Check system requirements for DJZ-Speak."""
    requirements = {
        'python_version': sys.version_info >= (3, 8),
        'platform': sys.platform,
        'available_memory': True,  # Simplified check
        'audio_support': True      # Simplified check
    }
    
    return requirements


def get_default_output_path(text: str, format: str = 'wav') -> str:
    """Generate default output filename from text."""
    # Take first few words and sanitize
    words = text.split()[:3]
    filename = '_'.join(words)
    filename = sanitize_filename(filename)
    
    # Limit length
    if len(filename) > 30:
        filename = filename[:30]
    
    return f"{filename}.{format}"


def generate_timestamped_filename(text: str = None, format: str = 'wav') -> str:
    """Generate timestamped filename for audio output."""
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if text:
        # Use first few words from text
        words = text.split()[:2]
        text_part = '_'.join(words)
        text_part = sanitize_filename(text_part)
        
        # Limit length
        if len(text_part) > 20:
            text_part = text_part[:20]
        
        return f"djz_speak_{text_part}_{timestamp}.{format}"
    else:
        return f"djz_speak_{timestamp}.{format}"
