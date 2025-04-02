"""
Test script for the Kalshi API client.

This script tests the functionality of the Kalshi API client
by making requests to various endpoints.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.kalshi_api_client import KalshiApiClient
from app.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_kalshi_api_client")

def test_kalshi_api_client():
    """Test the Kalshi API client."""
    logger.info("Testing Kalshi API client...")
    
    # Check if API credentials are available
    api_key_id = os.getenv("KALSHI_API_KEY_ID")
    private_key_path = os.getenv("KALSHI_PRIVATE_KEY_PATH")
    
    if not api_key_id or not private_key_path:
        logger.error("Missing Kalshi API credentials. Set KALSHI_API_KEY_ID and KALSHI_PRIVATE_KEY_PATH environment variables.")
        return False
    
    try:
        # Initialize Kalshi API client
        kalshi_client = KalshiApiClient(
            api_key_id=api_key_id,
            private_key_path=private_key_path,
            base_url=config.get("api", "base_url"),
            demo_mode=config.get("api", "demo_mode"),
            max_retries=config.get("api", "max_retries"),
            retry_delay=config.get("api", "retry_delay")
        )
        
        # Test endpoints
        endpoints = [
            {"name": "get_exchange_status", "method": kalshi_client.get_exchange_status, "args": {}},
            {"name": "get_markets", "method": kalshi_client.get_markets, "args": {"status": "active", "limit": 10}},
            {"name": "get_balance", "method": kalshi_client.get_balance, "args": {}},
            {"name": "get_positions", "method": kalshi_client.get_positions, "args": {}}
        ]
        
        results = {}
        
        for endpoint in endpoints:
            logger.info(f"Testing {endpoint['name']}...")
            
            try:
                # Call the endpoint
                response = endpoint["method"](**endpoint["args"])
                
                # Check if response is valid
                if response and isinstance(response, dict):
                    logger.info(f"Successfully called {endpoint['name']}")
                    results[endpoint['name']] = {
                        "success": True,
                        "sample": response if endpoint['name'] == "get_exchange_status" else "Response too large to include"
                    }
                else:
                    logger.warning(f"Invalid response from {endpoint['name']}")
                    results[endpoint['name']] = {
                        "success": False,
                        "error": "Invalid response"
                    }
            
            except Exception as e:
                logger.error(f"Failed to call {endpoint['name']}: {str(e)}")
                results[endpoint['name']] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Save results to file
        output_dir = Path("test_results")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "kalshi_api_client_test.json", "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Test results saved to {output_dir / 'kalshi_api_client_test.json'}")
        
        # Check if all tests passed
        all_passed = all(result.get("success", False) for result in results.values())
        
        if all_passed:
            logger.info("All tests passed!")
        else:
            logger.warning("Some tests failed. Check the results file for details.")
        
        return all_passed
    
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    test_kalshi_api_client()
