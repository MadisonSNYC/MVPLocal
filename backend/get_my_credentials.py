#!/usr/bin/env python3
"""
Script to retrieve stored credentials from the keychain.
"""
from app.keychain_manager import CredentialManager

def get_credentials(key_type):
    """
    Retrieve credentials from the secure keychain.
    
    Args:
        key_type: The type of key to retrieve (KALSHI_API_KEY_ID, KALSHI_PRIVATE_KEY, or OPENAI_API_KEY)
        
    Returns:
        The credential value, or None if not found
    """
    credential_manager = CredentialManager()
    
    if key_type == 'KALSHI_API_KEY_ID':
        # For Kalshi, we need to get both credentials and return just the ID
        api_key_id, _ = credential_manager.get_kalshi_credentials()
        return api_key_id
        
    elif key_type == 'KALSHI_PRIVATE_KEY':
        # For Kalshi, we need to get both credentials and return just the private key
        _, private_key = credential_manager.get_kalshi_credentials()
        return private_key
            
    elif key_type == 'OPENAI_API_KEY':
        return credential_manager.get_openai_api_key()
    
    else:
        print(f"Unknown key type: {key_type}")
        return None

# Get all the credentials
kalshi_key = get_credentials('KALSHI_API_KEY_ID')
private_key = get_credentials('KALSHI_PRIVATE_KEY')
openai_key = get_credentials('OPENAI_API_KEY')

# Print the results
print("Kalshi API Key ID:", kalshi_key)
print("Kalshi Private Key (first 50 chars):", private_key[:50] if private_key else None)
print("OpenAI API Key:", openai_key) 