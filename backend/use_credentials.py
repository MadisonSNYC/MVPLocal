#!/usr/bin/env python3
"""
Script that uses the exact format requested by the user for retrieving credentials.
"""
from get_my_credentials import get_credentials

# This is the exact format requested by the user
KALSHI_API_KEY_ID = get_credentials('KALSHI_API_KEY_ID')
KALSHI_PRIVATE_KEY = get_credentials('KALSHI_PRIVATE_KEY')
OPENAI_API_KEY = get_credentials('OPENAI_API_KEY')

# Print to confirm they were retrieved
print(f"KALSHI_API_KEY_ID = '{KALSHI_API_KEY_ID}'")
print(f"KALSHI_PRIVATE_KEY = '...[private key hidden]'")
print(f"OPENAI_API_KEY = '{OPENAI_API_KEY[:10]}...[rest of key hidden]'") 