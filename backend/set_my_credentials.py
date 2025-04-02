#!/usr/bin/env python3
"""
Script to set the user's credentials.
"""
from store_credentials import store_credentials

# Store Kalshi API Key ID
store_credentials('KALSHI_API_KEY_ID', 'YOUR_KALSHI_API_KEY_ID')

# Store Kalshi Private Key
store_credentials('KALSHI_PRIVATE_KEY', 'YOUR_KALSHI_PRIVATE_KEY')

# Store OpenAI API Key
store_credentials('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')

print("All credentials have been stored successfully.") 