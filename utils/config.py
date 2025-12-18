"""Configuration management for the application."""
import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class AppConfig:
    """Application configuration settings."""
    # Detection settings
    sensitivity: float = 0.15  # Distance threshold (0.0-1.0, lower = more sensitive)
    trigger_time: float = 3.0  # Seconds before warning
    cooldown_time: float = 10.0  # Seconds between warnings

    # Alert settings
    sound_enabled: bool = True
    popup_enabled: bool = True
    fullscreen_alert: bool = True  # Fullscreen alert for stronger feedback

    # App settings
    auto_start: bool = False
    start_minimized: bool = False
    auto_start_detection: bool = False  # Automatically start detection when app launches
    frame_skip: int = 2  # Process every Nth frame for performance

    # Window settings
    window_width: int = 1050
    window_height: int = 700

    # Language settings
    language: str = ""  # Empty string means auto-detect from system


class Config:
    """Configuration manager with file persistence."""

    DEFAULT_CONFIG_DIR = Path.home() / ".dont-touch"
    CONFIG_FILE = "config.json"

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or self.DEFAULT_CONFIG_DIR
        self.config_path = self.config_dir / self.CONFIG_FILE
        self.settings = AppConfig()
        self._ensure_config_dir()
        self.load()

    def _ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Update only existing fields
                    for key, value in data.items():
                        if hasattr(self.settings, key):
                            setattr(self.settings, key, value)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Failed to load config: {e}")

    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=2)
        except IOError as e:
            print(f"Failed to save config: {e}")

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.settings = AppConfig()
        self.save()

    def get(self, key: str, default=None):
        """Get a configuration value."""
        return getattr(self.settings, key, default)

    def set(self, key: str, value) -> None:
        """Set a configuration value."""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
            self.save()
