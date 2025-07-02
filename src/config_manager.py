"""
Configuration management system for DJZ-Speak
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from src.utils import get_project_root


class ConfigManager:
    """Manages configuration settings for DJZ-Speak."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager."""
        self.logger = logging.getLogger(__name__)
        self.project_root = get_project_root()
        
        # Default configuration file
        if config_file is None:
            config_file = self.project_root / "config" / "settings.yaml"
        
        self.config_file = Path(config_file)
        self.config = {}
        self.user_config_dir = Path.home() / ".djz-speak"
        
        # Load configuration
        self._load_default_config()
        self._load_user_config()
        self._apply_environment_overrides()
        
        # Validate configuration
        self._validate_config()
    
    def _load_default_config(self):
        """Load default configuration from YAML file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                self.logger.debug(f"Loaded configuration from {self.config_file}")
            else:
                self.logger.warning(f"Configuration file not found: {self.config_file}")
                self.config = self._get_fallback_config()
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.config = self._get_fallback_config()
    
    def _load_user_config(self):
        """Load user-specific configuration overrides."""
        user_config_file = self.user_config_dir / "config.yaml"
        
        if user_config_file.exists():
            try:
                with open(user_config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                
                # Merge user config with default config
                self._deep_merge(self.config, user_config)
                self.logger.debug(f"Loaded user configuration from {user_config_file}")
            except Exception as e:
                self.logger.warning(f"Error loading user configuration: {e}")
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides."""
        env_mappings = {
            'DJZ_SPEAK_SPEED': ('synthesis', 'speed'),
            'DJZ_SPEAK_PITCH': ('synthesis', 'pitch'),
            'DJZ_SPEAK_VOICE': ('synthesis', 'voice'),
            'DJZ_SPEAK_OUTPUT_FORMAT': ('output', 'default_format'),
            'DJZ_SPEAK_LOG_LEVEL': ('logging', 'level'),
            'DJZ_SPEAK_ESPEAK_PATH': ('system', 'espeak_path'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if section not in self.config:
                    self.config[section] = {}
                
                # Convert to appropriate type
                if key in ['speed', 'pitch', 'amplitude', 'gap']:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                elif key in ['enable_by_default', 'normalize_audio']:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                
                self.config[section][key] = value
                self.logger.debug(f"Applied environment override: {env_var}={value}")
    
    def _validate_config(self):
        """Validate configuration values."""
        # Validate synthesis parameters
        synthesis = self.config.get('synthesis', {})
        
        if 'speed' in synthesis:
            synthesis['speed'] = max(80, min(300, synthesis['speed']))
        
        if 'pitch' in synthesis:
            synthesis['pitch'] = max(0, min(99, synthesis['pitch']))
        
        if 'amplitude' in synthesis:
            synthesis['amplitude'] = max(0, min(200, synthesis['amplitude']))
        
        if 'gap' in synthesis:
            synthesis['gap'] = max(0, min(100, synthesis['gap']))
        
        # Validate audio settings
        audio = self.config.get('audio', {})
        
        if 'sample_rate' in audio:
            valid_rates = [8000, 11025, 16000, 22050, 44100, 48000]
            if audio['sample_rate'] not in valid_rates:
                audio['sample_rate'] = 22050
        
        if 'channels' in audio:
            audio['channels'] = max(1, min(2, audio['channels']))
        
        # Validate performance settings
        performance = self.config.get('performance', {})
        
        if 'max_text_length' in performance:
            performance['max_text_length'] = max(1, min(100000, performance['max_text_length']))
        
        if 'cache_size' in performance:
            performance['cache_size'] = max(1, min(1000, performance['cache_size']))
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get fallback configuration if file loading fails."""
        return {
            'audio': {
                'sample_rate': 22050,
                'channels': 1,
                'bit_depth': 16,
                'buffer_size': 1024
            },
            'synthesis': {
                'speed': 140,
                'pitch': 35,
                'amplitude': 100,
                'gap': 8,
                'voice': 'classic_robot'
            },
            'effects': {
                'enable_by_default': False,
                'frequency_filter': {
                    'low_cutoff': 300,
                    'high_cutoff': 3000
                },
                'harmonic_enhancement': 1.2,
                'mechanical_artifacts': True
            },
            'output': {
                'default_format': 'wav',
                'quality': 'high',
                'normalize_audio': True
            },
            'performance': {
                'max_text_length': 10000,
                'synthesis_timeout': 30,
                'cache_size': 50,
                'real_time_factor_target': 0.5
            },
            'logging': {
                'level': 'INFO',
                'file_logging': False
            },
            'system': {
                'espeak_path': None,
                'temp_directory': None,
                'max_memory_usage': 100
            }
        }
    
    def _deep_merge(self, base: Dict, override: Dict):
        """Deep merge two dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """Get configuration value."""
        if key is None:
            return self.config.get(section, default)
        
        section_config = self.config.get(section, {})
        return section_config.get(key, default)
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value."""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        self.logger.debug(f"Set config: {section}.{key} = {value}")
    
    def get_synthesis_params(self) -> Dict[str, Any]:
        """Get synthesis parameters."""
        return self.config.get('synthesis', {})
    
    def get_audio_params(self) -> Dict[str, Any]:
        """Get audio parameters."""
        return self.config.get('audio', {})
    
    def get_effects_params(self) -> Dict[str, Any]:
        """Get effects parameters."""
        return self.config.get('effects', {})
    
    def get_output_params(self) -> Dict[str, Any]:
        """Get output parameters."""
        return self.config.get('output', {})
    
    def get_performance_params(self) -> Dict[str, Any]:
        """Get performance parameters."""
        return self.config.get('performance', {})
    
    def get_espeak_path(self) -> Optional[str]:
        """Get eSpeak-NG executable path."""
        return self.get('system', 'espeak_path')
    
    def get_voice_presets_path(self) -> Path:
        """Get path to voice presets file."""
        presets_path = self.get('paths', 'voice_presets', 'config/default_voices.json')
        
        if not os.path.isabs(presets_path):
            presets_path = self.project_root / presets_path
        
        return Path(presets_path)
    
    def get_user_presets_path(self) -> Path:
        """Get path to user voice presets file."""
        user_presets = self.get('paths', 'user_presets', '~/.djz-speak/voices.json')
        return Path(user_presets).expanduser()
    
    def get_cache_directory(self) -> Path:
        """Get cache directory path."""
        cache_dir = self.get('paths', 'cache_directory', '~/.djz-speak/cache')
        cache_path = Path(cache_dir).expanduser()
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path
    
    def get_default_output_directory(self) -> Path:
        """Get default output directory path."""
        output_dir = self.get('output', 'default_output_directory', 'output')
        
        if not os.path.isabs(output_dir):
            output_dir = self.project_root / output_dir
        else:
            output_dir = Path(output_dir)
        
        # Resolve to absolute path to avoid any ambiguity
        output_dir = output_dir.resolve()
        
        # Create directory if it doesn't exist
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Default output directory: {output_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create output directory {output_dir}: {e}")
            raise
        
        return output_dir
    
    def save_user_config(self):
        """Save current configuration to user config file."""
        try:
            self.user_config_dir.mkdir(parents=True, exist_ok=True)
            user_config_file = self.user_config_dir / "config.yaml"
            
            with open(user_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Saved user configuration to {user_config_file}")
        except Exception as e:
            self.logger.error(f"Error saving user configuration: {e}")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self._get_fallback_config()
        self._validate_config()
        self.logger.info("Configuration reset to defaults")
    
    def export_config(self, file_path: Union[str, Path]):
        """Export current configuration to file."""
        try:
            file_path = Path(file_path)
            
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration exported to {file_path}")
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
    
    def import_config(self, file_path: Union[str, Path]):
        """Import configuration from file."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {file_path}")
            
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_config = json.load(f)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_config = yaml.safe_load(f)
            
            # Merge imported config
            self._deep_merge(self.config, imported_config)
            self._validate_config()
            
            self.logger.info(f"Configuration imported from {file_path}")
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        return {
            'voice': self.get('synthesis', 'voice'),
            'speed': self.get('synthesis', 'speed'),
            'pitch': self.get('synthesis', 'pitch'),
            'amplitude': self.get('synthesis', 'amplitude'),
            'format': self.get('output', 'default_format'),
            'sample_rate': self.get('audio', 'sample_rate'),
            'effects_enabled': self.get('effects', 'enable_by_default'),
            'espeak_path': self.get_espeak_path() or 'auto-detect'
        }
