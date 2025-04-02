"""
Test script for the AI recommendation system.

This script tests the functionality of the AI recommendation system
by generating recommendations using different strategies and risk levels.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import config
from app.kalshi_api_client import KalshiApiClient
from app.ai_recommendations import AIRecommendationSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_ai_recommendations")

def test_ai_recommendations():
    """Test the AI recommendation system."""
    logger.info("Testing AI recommendation system...")
    
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
        
        # Initialize AI recommendation system
        recommendation_system = AIRecommendationSystem(kalshi_client)
        
        # Test strategies and risk levels
        strategies = ["momentum", "mean-reversion", "hybrid"]
        risk_levels = ["low", "medium", "high"]
        
        results = {}
        
        for strategy in strategies:
            strategy_results = {}
            
            for risk_level in risk_levels:
                logger.info(f"Testing {strategy} strategy with {risk_level} risk level...")
                
                try:
                    # Generate recommendations
                    recommendations = recommendation_system.get_recommendations(
                        strategy=strategy,
                        max_recommendations=5,
                        risk_level=risk_level,
                        force_refresh=True
                    )
                    
                    # Check if recommendations were generated
                    if recommendations and len(recommendations) > 0:
                        logger.info(f"Successfully generated {len(recommendations)} recommendations")
                        strategy_results[risk_level] = {
                            "success": True,
                            "count": len(recommendations),
                            "sample": recommendations[0] if recommendations else None
                        }
                    else:
                        logger.warning(f"No recommendations generated for {strategy} strategy with {risk_level} risk level")
                        strategy_results[risk_level] = {
                            "success": False,
                            "error": "No recommendations generated"
                        }
                
                except Exception as e:
                    logger.error(f"Failed to generate recommendations: {str(e)}")
                    strategy_results[risk_level] = {
                        "success": False,
                        "error": str(e)
                    }
            
            results[strategy] = strategy_results
        
        # Save results to file
        output_dir = Path("test_results")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "ai_recommendations_test.json", "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Test results saved to {output_dir / 'ai_recommendations_test.json'}")
        
        # Check if all tests passed
        all_passed = all(
            result.get("success", False)
            for strategy_results in results.values()
            for result in strategy_results.values()
        )
        
        if all_passed:
            logger.info("All tests passed!")
        else:
            logger.warning("Some tests failed. Check the results file for details.")
        
        return all_passed
    
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    test_ai_recommendations()
