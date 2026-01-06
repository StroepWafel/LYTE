"""
Settings - Static class for application configuration.
Thread-safe, JSON-backed settings that can be accessed as Settings.field.
"""
import json
import threading
from pathlib import Path
from typing import Optional


class Settings:
    """Static settings class Saved to a JSON file."""
    
    _lock = threading.RLock()
    _path: Optional[Path] = None
    
    # Configuration fields with defaults
    YOUTUBE_VIDEO_ID: str = ""
    RATE_LIMIT_SECONDS: int = 3000
    TOAST_NOTIFICATIONS: bool = True
    PREFIX: str = "!"
    QUEUE_COMMAND: str = "queue"
    VOLUME: int = 100
    THEME: str = "dark_theme"
    ALLOW_URLS: bool = False
    REQUIRE_MEMBERSHIP: bool = False
    REQUIRE_SUPERCHAT: bool = False
    MINIMUM_SUPERCHAT: int = 3
    ENFORCE_ID_WHITELIST: bool = False
    ENFORCE_USER_WHITELIST: bool = False
    AUTOREMOVE_SONGS: bool = True
    AUTOBAN_USERS: bool = False
    
    @classmethod
    def set_path(cls, path: str) -> None:
        """Set the path to the config.json file."""
        cls._path = Path(path)
    
    @classmethod
    def load(cls) -> None:
        """Load settings from JSON file."""
        if cls._path is None:
            raise ValueError("Settings path not set. Call Settings.set_path() first.")
        
        if not cls._path.exists():
            cls.save()
            return
        
        with cls._lock:
            with open(cls._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Load each field, handling type conversions
            for key, value in data.items():
                if hasattr(cls, key):
                    # Handle boolean fields that might be stored as strings
                    if key in ("TOAST_NOTIFICATIONS", "ALLOW_URLS", "REQUIRE_MEMBERSHIP", 
                              "REQUIRE_SUPERCHAT", "ENFORCE_ID_WHITELIST", 
                              "ENFORCE_USER_WHITELIST", "AUTOREMOVE_SONGS", "AUTOBAN_USERS"):
                        if isinstance(value, str):
                            setattr(cls, key, value.lower() == "true")
                        else:
                            setattr(cls, key, bool(value))
                    else:
                        setattr(cls, key, value)
            
            # Handle migration from DARK_MODE to THEME if needed
            if "DARK_MODE" in data and not hasattr(cls, "_theme_migrated"):
                dark_mode = data.get("DARK_MODE", "True")
                if isinstance(dark_mode, str):
                    cls.THEME = "dark_theme" if dark_mode.lower() == "true" else "light_theme"
                else:
                    cls.THEME = "dark_theme" if dark_mode else "light_theme"
                cls._theme_migrated = True
    
    @classmethod
    def save(cls) -> None:
        """Save current settings to JSON file."""
        if cls._path is None:
            raise ValueError("Settings path not set. Call Settings.set_path() first.")
        
        with cls._lock:
            with open(cls._path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "YOUTUBE_VIDEO_ID": cls.YOUTUBE_VIDEO_ID,
                        "RATE_LIMIT_SECONDS": cls.RATE_LIMIT_SECONDS,
                        "TOAST_NOTIFICATIONS": str(cls.TOAST_NOTIFICATIONS),
                        "PREFIX": cls.PREFIX,
                        "QUEUE_COMMAND": cls.QUEUE_COMMAND,
                        "VOLUME": cls.VOLUME,
                        "THEME": cls.THEME,
                        "ALLOW_URLS": str(cls.ALLOW_URLS),
                        "REQUIRE_MEMBERSHIP": str(cls.REQUIRE_MEMBERSHIP),
                        "REQUIRE_SUPERCHAT": str(cls.REQUIRE_SUPERCHAT),
                        "MINIMUM_SUPERCHAT": cls.MINIMUM_SUPERCHAT,
                        "ENFORCE_ID_WHITELIST": str(cls.ENFORCE_ID_WHITELIST),
                        "ENFORCE_USER_WHITELIST": str(cls.ENFORCE_USER_WHITELIST),
                        "AUTOREMOVE_SONGS": str(cls.AUTOREMOVE_SONGS),
                        "AUTOBAN_USERS": str(cls.AUTOBAN_USERS),
                    },
                    f,
                    indent=4
                )
    
    @classmethod
    def to_dict(cls) -> dict:
        """Convert settings to dictionary (for backward compatibility)."""
        return {
            "YOUTUBE_VIDEO_ID": cls.YOUTUBE_VIDEO_ID,
            "RATE_LIMIT_SECONDS": cls.RATE_LIMIT_SECONDS,
            "TOAST_NOTIFICATIONS": str(cls.TOAST_NOTIFICATIONS),
            "PREFIX": cls.PREFIX,
            "QUEUE_COMMAND": cls.QUEUE_COMMAND,
            "VOLUME": cls.VOLUME,
            "THEME": cls.THEME,
            "ALLOW_URLS": str(cls.ALLOW_URLS),
            "REQUIRE_MEMBERSHIP": str(cls.REQUIRE_MEMBERSHIP),
            "REQUIRE_SUPERCHAT": str(cls.REQUIRE_SUPERCHAT),
            "MINIMUM_SUPERCHAT": cls.MINIMUM_SUPERCHAT,
            "ENFORCE_ID_WHITELIST": str(cls.ENFORCE_ID_WHITELIST),
            "ENFORCE_USER_WHITELIST": str(cls.ENFORCE_USER_WHITELIST),
            "AUTOREMOVE_SONGS": str(cls.AUTOREMOVE_SONGS),
            "AUTOBAN_USERS": str(cls.AUTOBAN_USERS),
        }

