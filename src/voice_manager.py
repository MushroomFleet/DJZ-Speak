"""
Voice management system for DJZ-Speak
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.config_manager import ConfigManager


class VoiceManager:
    """Manages voice presets and voice parameter configuration."""
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize voice manager."""
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.voice_presets = {}
        self.current_voice = None
        self.current_parameters = {}
        
        # Load voice presets
        self._load_voice_presets()
        
        # Set default voice
        default_voice = config_manager.get('synthesis', 'voice', 'classic_robot')
        self.set_voice(default_voice)
    
    def _load_voice_presets(self):
        """Load voice presets from configuration files."""
        # Load default voice presets
        default_presets_path = self.config_manager.get_voice_presets_path()
        self._load_presets_file(default_presets_path, is_default=True)
        
        # Load user voice presets
        user_presets_path = self.config_manager.get_user_presets_path()
        if user_presets_path.exists():
            self._load_presets_file(user_presets_path, is_default=False)
    
    def _load_presets_file(self, file_path: Path, is_default: bool = False):
        """Load voice presets from a JSON file."""
        try:
            if not file_path.exists():
                if is_default:
                    self.logger.warning(f"Default voice presets file not found: {file_path}")
                    self._create_fallback_presets()
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            voices = data.get('voices', {})
            for voice_id, voice_config in voices.items():
                self.voice_presets[voice_id] = voice_config
                voice_config['_source'] = 'default' if is_default else 'user'
            
            self.logger.debug(f"Loaded {len(voices)} voice presets from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading voice presets from {file_path}: {e}")
            if is_default:
                self._create_fallback_presets()
    
    def _create_fallback_presets(self):
        """Create fallback voice presets if loading fails."""
        self.voice_presets = {
            'classic_robot': {
                'name': 'Classic Robot',
                'description': 'Standard computer robot voice',
                'espeak_voice': 'en',
                'speed': 140,
                'pitch': 35,
                'amplitude': 100,
                'gap': 8,
                'variant': 'm3',
                'effects': {
                    'frequency_filter': True,
                    'harmonic_enhancement': 1.1,
                    'mechanical_artifacts': True
                },
                '_source': 'fallback'
            }
        }
        self.logger.warning("Using fallback voice presets")
    
    def list_voices(self) -> List[str]:
        """Get list of available voice preset names."""
        return list(self.voice_presets.keys())
    
    def get_voice(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get voice preset configuration."""
        return self.voice_presets.get(voice_id)
    
    def set_voice(self, voice_id: str) -> bool:
        """Set current voice preset."""
        if voice_id not in self.voice_presets:
            self.logger.warning(f"Voice preset '{voice_id}' not found")
            return False
        
        self.current_voice = voice_id
        self.current_parameters = self.voice_presets[voice_id].copy()
        
        # Remove metadata
        self.current_parameters.pop('_source', None)
        
        self.logger.debug(f"Set voice to: {voice_id}")
        return True
    
    def get_current_voice(self) -> Dict[str, Any]:
        """Get current voice configuration."""
        if self.current_voice is None:
            return {}
        
        return {
            'id': self.current_voice,
            **self.current_parameters
        }
    
    def get_current_voice_name(self) -> str:
        """Get current voice preset name."""
        if self.current_voice is None:
            return 'Unknown'
        
        return self.current_parameters.get('name', self.current_voice)
    
    def update_parameter(self, parameter: str, value: Any) -> bool:
        """Update a voice parameter for the current voice."""
        if self.current_voice is None:
            return False
        
        # Validate parameter
        if not self._validate_parameter(parameter, value):
            return False
        
        self.current_parameters[parameter] = value
        self.logger.debug(f"Updated {parameter} to {value} for voice {self.current_voice}")
        return True
    
    def _validate_parameter(self, parameter: str, value: Any) -> bool:
        """Validate voice parameter value."""
        validation_rules = {
            'speed': lambda x: isinstance(x, int) and 80 <= x <= 300,
            'pitch': lambda x: isinstance(x, int) and 0 <= x <= 99,
            'amplitude': lambda x: isinstance(x, int) and 0 <= x <= 200,
            'gap': lambda x: isinstance(x, int) and 0 <= x <= 100,
            'espeak_voice': lambda x: isinstance(x, str) and len(x) > 0,
            'variant': lambda x: isinstance(x, str),
        }
        
        if parameter in validation_rules:
            return validation_rules[parameter](value)
        
        return True  # Allow unknown parameters
    
    def get_espeak_parameters(self) -> Dict[str, Any]:
        """Get eSpeak-NG specific parameters from current voice."""
        if not self.current_parameters:
            return {}
        
        return {
            'voice': self.current_parameters.get('espeak_voice', 'en'),
            'speed': self.current_parameters.get('speed', 140),
            'pitch': self.current_parameters.get('pitch', 35),
            'amplitude': self.current_parameters.get('amplitude', 100),
            'gap': self.current_parameters.get('gap', 8),
            'variant': self.current_parameters.get('variant', 'm3')
        }
    
    def get_effects_parameters(self) -> Dict[str, Any]:
        """Get audio effects parameters from current voice."""
        if not self.current_parameters:
            return {}
        
        return self.current_parameters.get('effects', {})
    
    def create_custom_voice(self, voice_id: str, name: str, base_voice: str = None, **parameters) -> bool:
        """Create a custom voice preset."""
        if voice_id in self.voice_presets:
            self.logger.warning(f"Voice preset '{voice_id}' already exists")
            return False
        
        # Start with base voice if specified
        if base_voice and base_voice in self.voice_presets:
            voice_config = self.voice_presets[base_voice].copy()
            voice_config.pop('_source', None)
        else:
            voice_config = {
                'espeak_voice': 'en',
                'speed': 140,
                'pitch': 35,
                'amplitude': 100,
                'gap': 8,
                'variant': 'm3',
                'effects': {
                    'frequency_filter': True,
                    'harmonic_enhancement': 1.1,
                    'mechanical_artifacts': True
                }
            }
        
        # Update with custom parameters
        voice_config['name'] = name
        voice_config['description'] = f"Custom voice: {name}"
        voice_config.update(parameters)
        voice_config['_source'] = 'custom'
        
        # Validate parameters
        for param, value in parameters.items():
            if not self._validate_parameter(param, value):
                self.logger.error(f"Invalid parameter {param}={value} for custom voice")
                return False
        
        self.voice_presets[voice_id] = voice_config
        self.logger.info(f"Created custom voice: {voice_id}")
        return True
    
    def delete_voice(self, voice_id: str) -> bool:
        """Delete a voice preset (only custom voices)."""
        if voice_id not in self.voice_presets:
            return False
        
        voice_config = self.voice_presets[voice_id]
        if voice_config.get('_source') not in ['custom', 'user']:
            self.logger.warning(f"Cannot delete default voice preset: {voice_id}")
            return False
        
        del self.voice_presets[voice_id]
        
        # If this was the current voice, switch to default
        if self.current_voice == voice_id:
            self.set_voice('classic_robot')
        
        self.logger.info(f"Deleted voice preset: {voice_id}")
        return True
    
    def save_user_presets(self):
        """Save user and custom voice presets to user config file."""
        try:
            user_presets_path = self.config_manager.get_user_presets_path()
            user_presets_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Filter user and custom voices
            user_voices = {
                voice_id: config for voice_id, config in self.voice_presets.items()
                if config.get('_source') in ['user', 'custom']
            }
            
            # Remove source metadata for saving
            clean_voices = {}
            for voice_id, config in user_voices.items():
                clean_config = config.copy()
                clean_config.pop('_source', None)
                clean_voices[voice_id] = clean_config
            
            data = {'voices': clean_voices}
            
            with open(user_presets_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved {len(clean_voices)} user voice presets")
            
        except Exception as e:
            self.logger.error(f"Error saving user voice presets: {e}")
    
    def get_voice_categories(self) -> Dict[str, List[str]]:
        """Get voice presets organized by categories."""
        categories = {
            'retro': [],
            'cinematic': [],
            'modern': [],
            'experimental': [],
            'custom': []
        }
        
        # Load categories from default presets file if available
        try:
            default_presets_path = self.config_manager.get_voice_presets_path()
            if default_presets_path.exists():
                with open(default_presets_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                preset_categories = data.get('voice_categories', {})
                for category, voices in preset_categories.items():
                    if category in categories:
                        categories[category].extend(voices)
        except Exception as e:
            self.logger.debug(f"Could not load voice categories: {e}")
        
        # Add custom voices
        for voice_id, config in self.voice_presets.items():
            if config.get('_source') == 'custom':
                categories['custom'].append(voice_id)
        
        # Add uncategorized voices
        all_categorized = set()
        for voice_list in categories.values():
            all_categorized.update(voice_list)
        
        uncategorized = set(self.voice_presets.keys()) - all_categorized
        if uncategorized:
            categories['other'] = list(uncategorized)
        
        # Remove empty categories
        return {cat: voices for cat, voices in categories.items() if voices}
    
    def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """Get detailed information about a voice preset."""
        if voice_id not in self.voice_presets:
            return {}
        
        config = self.voice_presets[voice_id]
        
        return {
            'id': voice_id,
            'name': config.get('name', voice_id),
            'description': config.get('description', 'No description'),
            'characteristics': config.get('characteristics', 'Standard robotic voice'),
            'source': config.get('_source', 'unknown'),
            'parameters': {
                'speed': config.get('speed', 140),
                'pitch': config.get('pitch', 35),
                'amplitude': config.get('amplitude', 100),
                'gap': config.get('gap', 8),
                'espeak_voice': config.get('espeak_voice', 'en'),
                'variant': config.get('variant', 'm3')
            },
            'effects': config.get('effects', {})
        }
    
    def clone_voice(self, source_voice_id: str, new_voice_id: str, new_name: str) -> bool:
        """Clone an existing voice preset."""
        if source_voice_id not in self.voice_presets:
            self.logger.error(f"Source voice '{source_voice_id}' not found")
            return False
        
        if new_voice_id in self.voice_presets:
            self.logger.error(f"Voice '{new_voice_id}' already exists")
            return False
        
        # Clone the voice configuration
        source_config = self.voice_presets[source_voice_id].copy()
        source_config.pop('_source', None)
        source_config['name'] = new_name
        source_config['description'] = f"Clone of {source_config.get('name', source_voice_id)}"
        source_config['_source'] = 'custom'
        
        self.voice_presets[new_voice_id] = source_config
        self.logger.info(f"Cloned voice '{source_voice_id}' to '{new_voice_id}'")
        return True
    
    def reset_voice_parameters(self):
        """Reset current voice to its preset defaults."""
        if self.current_voice:
            self.current_parameters = self.voice_presets[self.current_voice].copy()
            self.current_parameters.pop('_source', None)
            self.logger.debug(f"Reset voice parameters for {self.current_voice}")
