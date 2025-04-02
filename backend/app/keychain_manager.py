"""
macOS Keychain integration for secure credential storage.

This module provides functions to securely store and retrieve API credentials
using the macOS Keychain.
"""

import logging
import subprocess
import json
import os
from typing import Dict, Optional, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("keychain_manager")

class KeychainManager:
    """
    Manager for securely storing and retrieving API credentials using macOS Keychain.
    """
    
    # Service names for different credentials
    KALSHI_SERVICE_NAME = "KalshiTradingDashboard-KalshiAPI"
    OPENAI_SERVICE_NAME = "KalshiTradingDashboard-OpenAI"
    
    def __init__(self):
        """
        Initialize the keychain manager.
        """
        self.is_macos = self._check_is_macos()
        logger.info(f"Initialized keychain manager (macOS available: {self.is_macos})")
    
    def store_kalshi_credentials(self, api_key_id: str, api_key_secret: str) -> bool:
        """
        Store Kalshi API credentials in the keychain.
        
        Args:
            api_key_id: Kalshi API Key ID
            api_key_secret: Kalshi API Key Secret
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_macos:
            logger.warning("macOS Keychain not available, cannot store credentials securely")
            return False
        
        # Store API Key ID
        success_id = self._store_password(
            service=self.KALSHI_SERVICE_NAME,
            account="api_key_id",
            password=api_key_id
        )
        
        # Store API Key Secret
        success_secret = self._store_password(
            service=self.KALSHI_SERVICE_NAME,
            account="api_key_secret",
            password=api_key_secret
        )
        
        return success_id and success_secret
    
    def get_kalshi_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get Kalshi API credentials from the keychain.
        
        Returns:
            Tuple of (api_key_id, api_key_secret), or (None, None) if not found
        """
        if not self.is_macos:
            logger.warning("macOS Keychain not available, cannot retrieve credentials")
            return None, None
        
        # Get API Key ID
        api_key_id = self._get_password(
            service=self.KALSHI_SERVICE_NAME,
            account="api_key_id"
        )
        
        # Get API Key Secret
        api_key_secret = self._get_password(
            service=self.KALSHI_SERVICE_NAME,
            account="api_key_secret"
        )
        
        return api_key_id, api_key_secret
    
    def store_openai_api_key(self, api_key: str) -> bool:
        """
        Store OpenAI API key in the keychain.
        
        Args:
            api_key: OpenAI API Key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_macos:
            logger.warning("macOS Keychain not available, cannot store credentials securely")
            return False
        
        return self._store_password(
            service=self.OPENAI_SERVICE_NAME,
            account="api_key",
            password=api_key
        )
    
    def get_openai_api_key(self) -> Optional[str]:
        """
        Get OpenAI API key from the keychain.
        
        Returns:
            API key, or None if not found
        """
        if not self.is_macos:
            logger.warning("macOS Keychain not available, cannot retrieve credentials")
            return None
        
        return self._get_password(
            service=self.OPENAI_SERVICE_NAME,
            account="api_key"
        )
    
    def delete_all_credentials(self) -> bool:
        """
        Delete all stored credentials from the keychain.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_macos:
            logger.warning("macOS Keychain not available, cannot delete credentials")
            return False
        
        # Delete Kalshi credentials
        success_kalshi_id = self._delete_password(
            service=self.KALSHI_SERVICE_NAME,
            account="api_key_id"
        )
        
        success_kalshi_secret = self._delete_password(
            service=self.KALSHI_SERVICE_NAME,
            account="api_key_secret"
        )
        
        # Delete OpenAI credentials
        success_openai = self._delete_password(
            service=self.OPENAI_SERVICE_NAME,
            account="api_key"
        )
        
        return success_kalshi_id and success_kalshi_secret and success_openai
    
    def _check_is_macos(self) -> bool:
        """
        Check if running on macOS.
        
        Returns:
            True if running on macOS, False otherwise
        """
        try:
            return os.uname().sysname == "Darwin"
        except:
            return False
    
    def _store_password(self, service: str, account: str, password: str) -> bool:
        """
        Store a password in the keychain.
        
        Args:
            service: Service name
            account: Account name
            password: Password to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use security command-line tool to add password
            cmd = [
                "security",
                "add-generic-password",
                "-s", service,
                "-a", account,
                "-w", password,
                "-U"  # Update if exists
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to store password: {result.stderr}")
                return False
            
            logger.info(f"Successfully stored password for {service}/{account}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing password: {str(e)}")
            return False
    
    def _get_password(self, service: str, account: str) -> Optional[str]:
        """
        Get a password from the keychain.
        
        Args:
            service: Service name
            account: Account name
            
        Returns:
            Password, or None if not found
        """
        try:
            # Use security command-line tool to find password
            cmd = [
                "security",
                "find-generic-password",
                "-s", service,
                "-a", account,
                "-w"  # Output only the password
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Password not found for {service}/{account}")
                return None
            
            # Return password (strip newline)
            return result.stdout.strip()
            
        except Exception as e:
            logger.error(f"Error retrieving password: {str(e)}")
            return None
    
    def _delete_password(self, service: str, account: str) -> bool:
        """
        Delete a password from the keychain.
        
        Args:
            service: Service name
            account: Account name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use security command-line tool to delete password
            cmd = [
                "security",
                "delete-generic-password",
                "-s", service,
                "-a", account
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Return code 44 means item not found, which is fine for deletion
            if result.returncode != 0 and result.returncode != 44:
                logger.error(f"Failed to delete password: {result.stderr}")
                return False
            
            logger.info(f"Successfully deleted password for {service}/{account}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting password: {str(e)}")
            return False


class FallbackCredentialManager:
    """
    Fallback credential manager for non-macOS platforms.
    
    This class provides a fallback for storing credentials in a local file
    when macOS Keychain is not available.
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the fallback credential manager.
        
        Args:
            config_dir: Directory to store credentials file
        """
        self.config_dir = config_dir or os.path.expanduser("~/.kalshi-dashboard")
        self.credentials_file = os.path.join(self.config_dir, "credentials.json")
        
        # Create config directory if it doesn't exist
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        logger.info(f"Initialized fallback credential manager")
    
    def store_kalshi_credentials(self, api_key_id: str, api_key_secret: str) -> bool:
        """
        Store Kalshi API credentials in the credentials file.
        
        Args:
            api_key_id: Kalshi API Key ID
            api_key_secret: Kalshi API Key Secret
            
        Returns:
            True if successful, False otherwise
        """
        credentials = self._load_credentials()
        
        if "kalshi" not in credentials:
            credentials["kalshi"] = {}
        
        credentials["kalshi"]["api_key_id"] = api_key_id
        credentials["kalshi"]["api_key_secret"] = api_key_secret
        
        return self._save_credentials(credentials)
    
    def get_kalshi_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get Kalshi API credentials from the credentials file.
        
        Returns:
            Tuple of (api_key_id, api_key_secret), or (None, None) if not found
        """
        credentials = self._load_credentials()
        
        if "kalshi" not in credentials:
            return None, None
        
        return (
            credentials["kalshi"].get("api_key_id"),
            credentials["kalshi"].get("api_key_secret")
        )
    
    def store_openai_api_key(self, api_key: str) -> bool:
        """
        Store OpenAI API key in the credentials file.
        
        Args:
            api_key: OpenAI API Key
            
        Returns:
            True if successful, False otherwise
        """
        credentials = self._load_credentials()
        
        if "openai" not in credentials:
            credentials["openai"] = {}
        
        credentials["openai"]["api_key"] = api_key
        
        return self._save_credentials(credentials)
    
    def get_openai_api_key(self) -> Optional[str]:
        """
        Get OpenAI API key from the credentials file.
        
        Returns:
            API key, or None if not found
        """
        credentials = self._load_credentials()
        
        if "openai" not in credentials:
            return None
        
        return credentials["openai"].get("api_key")
    
    def delete_all_credentials(self) -> bool:
        """
        Delete all stored credentials from the credentials file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(self.credentials_file):
                os.remove(self.credentials_file)
            
            logger.info("Successfully deleted all credentials")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting credentials: {str(e)}")
            return False
    
    def _load_credentials(self) -> Dict[str, Any]:
        """
        Load credentials from the credentials file.
        
        Returns:
            Dictionary with credentials
        """
        if not os.path.exists(self.credentials_file):
            return {}
        
        try:
            with open(self.credentials_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return {}
    
    def _save_credentials(self, credentials: Dict[str, Any]) -> bool:
        """
        Save credentials to the credentials file.
        
        Args:
            credentials: Dictionary with credentials
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.credentials_file, "w") as f:
                json.dump(credentials, f, indent=2)
            
            # Set file permissions to user read/write only
            os.chmod(self.credentials_file, 0o600)
            
            logger.info("Successfully saved credentials")
            return True
            
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
            return False


class CredentialManager:
    """
    Unified credential manager that uses macOS Keychain when available,
    and falls back to file-based storage when not.
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the credential manager.
        
        Args:
            config_dir: Directory to store credentials file (for fallback)
        """
        self.keychain_manager = KeychainManager()
        self.fallback_manager = FallbackCredentialManager(config_dir)
        
        self.is_macos = self.keychain_manager.is_macos
        logger.info(f"Initialized credential manager (using {'Keychain' if self.is_macos else 'fallback storage'})")
    
    def store_kalshi_credentials(self, api_key_id: str, api_key_secret: str) -> bool:
        """
        Store Kalshi API credentials.
        
        Args:
            api_key_id: Kalshi API Key ID
            api_key_secret: Kalshi API Key Secret
            
        Returns:
            True if successful, False otherwise
        """
        if self.is_macos:
            return self.keychain_manager.store_kalshi_credentials(api_key_id, api_key_secret)
        else:
            return self.fallback_manager.store_kalshi_credentials(api_key_id, api_key_secret)
    
    def get_kalshi_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get Kalshi API credentials.
        
        Returns:
            Tuple of (api_key_id, api_key_secret), or (None, None) if not found
        """
        if self.is_macos:
            return self.keychain_manager.get_kalshi_credentials()
        else:
            return self.fallback_manager.get_kalshi_credentials()
    
    def store_openai_api_key(self, api_key: str) -> bool:
        """
        Store OpenAI API key.
        
        Args:
            api_key: OpenAI API Key
            
        Returns:
            True if successful, False otherwise
        """
        if self.is_macos:
            return self.keychain_manager.store_openai_api_key(api_key)
        else:
            return self.fallback_manager.store_openai_api_key(api_key)
    
    def get_openai_api_key(self) -> Optional[str]:
        """
        Get OpenAI API key.
        
        Returns:
            API key, or None if not found
        """
        if self.is_macos:
            return self.keychain_manager.get_openai_api_key()
        else:
            return self.fallback_manager.get_openai_api_key()
    
    def delete_all_credentials(self) -> bool:
        """
        Delete all stored credentials.
        
        Returns:
            True if successful, False otherwise
        """
        if self.is_macos:
            return self.keychain_manager.delete_all_credentials()
        else:
            return self.fallback_manager.delete_all_credentials()
    
    def has_credentials(self) -> bool:
        """
        Check if credentials are stored.
        
        Returns:
            True if credentials are stored, False otherwise
        """
        kalshi_id, kalshi_secret = self.get_kalshi_credentials()
        openai_key = self.get_openai_api_key()
        
        return kalshi_id is not None and kalshi_secret is not None and openai_key is not None
