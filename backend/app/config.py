"""
Configuration module for the Kalshi Trading Dashboard application.

This module handles loading and validating configuration from environment variables,
configuration files, and secure storage (macOS Keychain).
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("config")

# Default configuration values
DEFAULT_CONFIG = {
    "api": {
        "base_url": "https://api.kalshi.com/trade-api/v2",
        "demo_mode": False,
        "max_retries": 3,
        "retry_delay": 1
    },
    "server": {
        "host": "127.0.0.1",
        "port": 5000,
        "debug": False,
        "reload": False
    },
    "ai": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "cache_recommendations": True,
        "cache_ttl_minutes": 30
    },
    "app": {
        "offline_mode": False,
        "cache_dir": "./cache",
        "data_dir": "./data",
        "log_level": "INFO"
    }
}

class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config = DEFAULT_CONFIG.copy()
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration from file if provided
        if config_path:
            self._load_from_file(config_path)
            
        # Override with environment variables
        self._load_from_env()
        
        # Validate required configuration
        self._validate_config()
        
        logger.info("Configuration loaded successfully")
        
    def _load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                
            # Update config with file values (deep merge)
            self._deep_update(self.config, file_config)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load configuration from {config_path}: {str(e)}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # API configuration
        if os.getenv("KALSHI_API_URL"):
            self.config["api"]["base_url"] = os.getenv("KALSHI_API_URL")
        
        if os.getenv("KALSHI_DEMO_MODE"):
            self.config["api"]["demo_mode"] = os.getenv("KALSHI_DEMO_MODE").lower() == "true"
        
        # Server configuration
        if os.getenv("SERVER_HOST"):
            self.config["server"]["host"] = os.getenv("SERVER_HOST")
        
        if os.getenv("SERVER_PORT"):
            self.config["server"]["port"] = int(os.getenv("SERVER_PORT"))
        
        if os.getenv("SERVER_DEBUG"):
            self.config["server"]["debug"] = os.getenv("SERVER_DEBUG").lower() == "true"
        
        # AI configuration
        if os.getenv("AI_PROVIDER"):
            self.config["ai"]["provider"] = os.getenv("AI_PROVIDER")
        
        if os.getenv("AI_MODEL"):
            self.config["ai"]["model"] = os.getenv("AI_MODEL")
        
        if os.getenv("OPENAI_API_KEY"):
            self.config["ai"]["api_key"] = os.getenv("OPENAI_API_KEY")
        
        # App configuration
        if os.getenv("OFFLINE_MODE"):
            self.config["app"]["offline_mode"] = os.getenv("OFFLINE_MODE").lower() == "true"
        
        if os.getenv("CACHE_DIR"):
            self.config["app"]["cache_dir"] = os.getenv("CACHE_DIR")
        
        if os.getenv("DATA_DIR"):
            self.config["app"]["data_dir"] = os.getenv("DATA_DIR")
        
        if os.getenv("LOG_LEVEL"):
            self.config["app"]["log_level"] = os.getenv("LOG_LEVEL")
        
        logger.debug("Loaded configuration from environment variables")
    
    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Deep update a nested dictionary.
        
        Args:
            target: Target dictionary to update
            source: Source dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def _validate_config(self) -> None:
        """Validate the configuration and ensure required values are present."""
        # Create cache directory if it doesn't exist
        cache_dir = Path(self.config["app"]["cache_dir"])
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created cache directory: {cache_dir}")
        
        # Set log level
        log_level = self.config["app"]["log_level"]
        logging.getLogger().setLevel(log_level)
        
        # Check for AI API key if using OpenAI
        if self.config["ai"]["provider"] == "openai" and "api_key" not in self.config["ai"]:
            logger.warning("OpenAI API key not found in configuration")
    
    def get(self, section: str, key: Optional[str] = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key (optional)
            
        Returns:
            Configuration value or section
        """
        if section not in self.config:
            logger.warning(f"Configuration section '{section}' not found")
            return None
        
        if key is None:
            return self.config[section]
        
        if key not in self.config[section]:
            logger.warning(f"Configuration key '{key}' not found in section '{section}'")
            return None
        
        return self.config[section][key]
    
    def get_api_credentials(self) -> Dict[str, str]:
        """
        Get API credentials from secure storage or environment.
        
        For macOS, this would ideally use the Keychain.
        For this implementation, we'll use environment variables.
        
        Returns:
            Dictionary containing API credentials
        """
        api_key_id = os.getenv("KALSHI_API_KEY_ID")
        private_key_path = os.getenv("KALSHI_PRIVATE_KEY_PATH")
        
        if not api_key_id:
            logger.warning("KALSHI_API_KEY_ID not found in environment")
        
        if not private_key_path:
            logger.warning("KALSHI_PRIVATE_KEY_PATH not found in environment")
        
        return {
            "api_key_id": api_key_id,
            "private_key_path": private_key_path
        }

# Create a singleton instance
config = Config()
