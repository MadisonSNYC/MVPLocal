"""
Dependencies for FastAPI routes.

This module provides dependency injection functions for FastAPI routes.
"""

import logging
import os
from app.kalshi_api_client import KalshiApiClient
from app.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dependencies")

# Create a config instance
config = Config()

def get_kalshi_client() -> KalshiApiClient:
    """
    Get a Kalshi API client instance.
    
    Returns:
        KalshiApiClient instance
    """
    try:
        # Get credentials from environment or keychain
        api_credentials = config.get_api_credentials()
        
        # Check if we're in demo mode
        demo_mode = os.getenv("DEMO_MODE", "False").lower() in ("true", "1", "yes")
        
        # Create the client
        return KalshiApiClient(
            api_key_id=api_credentials.get("api_key_id", ""),
            api_key_secret=api_credentials.get("api_key_secret", ""),
            base_url=config.get("api", "base_url"),
            demo_mode=demo_mode
        )
    except Exception as e:
        logger.error(f"Failed to initialize Kalshi API client: {str(e)}")
        # Return a demo client as fallback
        return KalshiApiClient(demo_mode=True) 