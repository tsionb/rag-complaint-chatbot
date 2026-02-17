"""Environment configuration loader with validation."""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Load and validate configuration from environment."""
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self._load_env_file()
    
    def _load_env_file(self) -> None:
        if Path(self.env_file).exists():
            load_dotenv(self.env_file)
            logger.info(f"Loaded environment from {self.env_file}")
        else:
            logger.warning(f"No {self.env_file} found, using system environment")
    
    def get(self, key: str, default: str = None) -> str:
        """Get environment variable with default."""
        return os.getenv(key, default)
    
    def get_int(self, key: str, default: int = None) -> int:
        """Get integer environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.error(f"Invalid integer for {key}: {value}")
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def get_path(self, key: str, default: str = "") -> Path:
        """Get path environment variable."""
        path_str = self.get(key, default)
        path = Path(path_str)
        
        # Create parent directories if needed
        if path.suffix:  # It's a file
            path.parent.mkdir(parents=True, exist_ok=True)
        else:  # It's a directory
            path.mkdir(parents=True, exist_ok=True)
        
        return path