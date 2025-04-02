#!/usr/bin/env python3
"""
Script to store credentials securely using the keychain_manager.
"""
import sys
import os
from app.keychain_manager import CredentialManager

def store_credentials(key_type, key_value):
    """
    Store credentials in the secure keychain.
    
    Args:
        key_type: The type of key to store (KALSHI_API_KEY_ID, KALSHI_PRIVATE_KEY, or OPENAI_API_KEY)
        key_value: The value of the key to store
    """
    credential_manager = CredentialManager()
    
    if key_type == 'KALSHI_API_KEY_ID':
        # Store the API Key ID, but we need the private key for the full credentials
        # We'll temporarily store this and use it when the private key is provided
        os.environ['TEMP_KALSHI_API_KEY_ID'] = key_value
        print(f"Stored {key_type} temporarily")
        
    elif key_type == 'KALSHI_PRIVATE_KEY':
        # Get the API Key ID from the environment or use a default
        api_key_id = os.environ.get('TEMP_KALSHI_API_KEY_ID', '')
        
        # Store both the API Key ID and Private Key
        success = credential_manager.store_kalshi_credentials(api_key_id, key_value)
        
        if success:
            print(f"Successfully stored Kalshi credentials")
            # Clean up the temporary environment variable
            if 'TEMP_KALSHI_API_KEY_ID' in os.environ:
                del os.environ['TEMP_KALSHI_API_KEY_ID']
        else:
            print(f"Failed to store Kalshi credentials")
            
    elif key_type == 'OPENAI_API_KEY':
        success = credential_manager.store_openai_api_key(key_value)
        if success:
            print(f"Successfully stored {key_type}")
        else:
            print(f"Failed to store {key_type}")
    
    else:
        print(f"Unknown key type: {key_type}")

if __name__ == "__main__":
    # Usage: python store_credentials.py KEY_TYPE KEY_VALUE
    if len(sys.argv) != 3:
        print("Usage: python store_credentials.py KEY_TYPE KEY_VALUE")
        sys.exit(1)
    
    store_credentials(sys.argv[1], sys.argv[2]) 