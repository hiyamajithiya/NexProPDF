"""
Configuration manager for NexPro PDF
"""

import yaml
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    """Manage application configuration"""

    def __init__(self, config_file="config/config.yaml"):
        """
        Initialize configuration manager

        Args:
            config_file: Path to configuration file
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return self._get_default_config()

    def _get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            'app': {
                'name': 'NexPro PDF',
                'version': '1.0.0',
                'company': 'NexPro Technologies'
            },
            'ui': {
                'theme': 'professional',
                'primary_color': '#2C3E50',
                'accent_color': '#27AE60',
                'window_title': 'NexPro PDF - Professional PDF Editor',
                'window_size': {'width': 1400, 'height': 900}
            },
            'performance': {
                'max_pages_memory': 500,
                'worker_threads': 4,
                'cache_size_mb': 200
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            key: Configuration key (e.g., 'app.name')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation

        Args:
            key: Configuration key
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {e}")
