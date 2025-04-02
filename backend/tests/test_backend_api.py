"""
Test script for the FastAPI backend application.

This script tests the functionality of the FastAPI backend application
by making requests to various endpoints.
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
import subprocess
import time
import signal

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_backend_api")

def start_server():
    """Start the FastAPI server for testing."""
    logger.info("Starting FastAPI server...")
    
    # Start the server as a subprocess
    server_process = subprocess.Popen(
        ["python", "../server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid  # Use process group for easier termination
    )
    
    # Wait for the server to start
    logger.info("Waiting for server to start...")
    time.sleep(5)
    
    return server_process

def stop_server(server_process):
    """Stop the FastAPI server."""
    logger.info("Stopping FastAPI server...")
    
    # Kill the process group
    os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
    
    # Wait for the process to terminate
    server_process.wait()
    
    logger.info("Server stopped")

def test_backend_api():
    """Test the FastAPI backend application."""
    logger.info("Testing FastAPI backend application...")
    
    server_process = None
    
    try:
        # Start the server
        server_process = start_server()
        
        # Base URL for the API
        base_url = "http://localhost:5000"
        
        # Test endpoints
        endpoints = [
            {"name": "health_check", "url": f"{base_url}/api/health", "method": "GET"},
            {"name": "get_strategies", "url": f"{base_url}/api/recommendations/strategies", "method": "GET"},
            {"name": "get_exchange_status", "url": f"{base_url}/api/exchange/status", "method": "GET"}
        ]
        
        results = {}
        
        for endpoint in endpoints:
            logger.info(f"Testing {endpoint['name']}...")
            
            try:
                # Make the request
                if endpoint["method"] == "GET":
                    response = requests.get(endpoint["url"], timeout=10)
                else:
                    # Add other methods as needed
                    logger.warning(f"Unsupported method: {endpoint['method']}")
                    continue
                
                # Check if response is valid
                if response.status_code == 200:
                    logger.info(f"Successfully called {endpoint['name']}")
                    results[endpoint['name']] = {
                        "success": True,
                        "status_code": response.status_code,
                        "response": response.json()
                    }
                else:
                    logger.warning(f"Invalid response from {endpoint['name']}: {response.status_code}")
                    results[endpoint['name']] = {
                        "success": False,
                        "status_code": response.status_code,
                        "error": response.text
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
        
        with open(output_dir / "backend_api_test.json", "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Test results saved to {output_dir / 'backend_api_test.json'}")
        
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
    
    finally:
        # Stop the server if it was started
        if server_process:
            stop_server(server_process)

if __name__ == "__main__":
    test_backend_api()
