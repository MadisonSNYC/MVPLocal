#!/usr/bin/env python3
"""
Script to retrieve and store credentials from the keychain as variables.
"""
from get_my_credentials import get_credentials

# Retrieve credentials and store them as variables
KALSHI_API_KEY_ID = get_credentials('KALSHI_API_KEY_ID')
KALSHI_PRIVATE_KEY = get_credentials('KALSHI_PRIVATE_KEY')
OPENAI_API_KEY = get_credentials('OPENAI_API_KEY')

# Print to confirm they were retrieved
print(f"Retrieved KALSHI_API_KEY_ID: {KALSHI_API_KEY_ID}")
print(f"Retrieved KALSHI_PRIVATE_KEY: {'*' * 10 if KALSHI_PRIVATE_KEY else 'Not found'}")
print(f"Retrieved OPENAI_API_KEY: {'*' * 10 if OPENAI_API_KEY else 'Not found'}")

# Now these variables can be used in your application
# Example usage:
print("\nExample of how these variables could be used in your application:")
print("import requests")
print("headers = {'Authorization': f'Bearer {OPENAI_API_KEY}'}")
print("response = requests.post('https://api.openai.com/v1/...')") 