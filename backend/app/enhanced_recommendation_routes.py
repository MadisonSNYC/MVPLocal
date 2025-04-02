"""
Updated recommendation routes to use the enhanced AI recommendation system.

This module provides API routes for the enhanced AI recommendation system.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from app.kalshi_api_client import KalshiApiClient
from app.enhanced_ai_recommendations import EnhancedAIRecommendationSystem
from app.dependencies import get_kalshi_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced_recommendation_routes")

# Create router
router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

# Initialize recommendation system
recommendation_systems = {}

def get_recommendation_system(kalshi_client: KalshiApiClient = Depends(get_kalshi_client)) -> EnhancedAIRecommendationSystem:
    """
    Get or create an enhanced AI recommendation system.
    
    Args:
        kalshi_client: Kalshi API client instance
        
    Returns:
        Enhanced AI recommendation system instance
    """
    client_id = id(kalshi_client)
    
    if client_id not in recommendation_systems:
        recommendation_systems[client_id] = EnhancedAIRecommendationSystem(kalshi_client)
    
    return recommendation_systems[client_id]

@router.get("/strategies")
async def get_strategies() -> Dict[str, Any]:
    """
    Get available trading strategies.
    
    Returns:
        Dictionary with available strategies
    """
    strategies = [
        {
            "id": "momentum",
            "name": "Momentum",
            "description": "Identifies markets with strong trends and suggests continuing in that direction.",
            "risk_levels": ["low", "medium", "high"]
        },
        {
            "id": "mean-reversion",
            "name": "Mean Reversion",
            "description": "Identifies markets with extreme prices that might revert to their average.",
            "risk_levels": ["low", "medium", "high"]
        },
        {
            "id": "hybrid",
            "name": "Hybrid",
            "description": "Combines momentum and mean-reversion strategies for a balanced approach.",
            "risk_levels": ["low", "medium", "high"]
        }
    ]
    
    return {"strategies": strategies}

@router.get("")
async def get_recommendations(
    strategy: str = Query(..., description="Strategy to use"),
    max_recommendations: int = Query(5, description="Maximum number of recommendations to return"),
    risk_level: str = Query("medium", description="Risk level"),
    force_refresh: bool = Query(False, description="Whether to force a refresh of cached recommendations"),
    recommendation_system: EnhancedAIRecommendationSystem = Depends(get_recommendation_system)
) -> Dict[str, Any]:
    """
    Get trade recommendations based on the specified strategy.
    
    Args:
        strategy: Strategy to use ("momentum", "mean-reversion", or "hybrid")
        max_recommendations: Maximum number of recommendations to return
        risk_level: Risk level ("low", "medium", or "high")
        force_refresh: Whether to force a refresh of cached recommendations
        recommendation_system: Enhanced AI recommendation system instance
        
    Returns:
        Dictionary with recommendations and metadata
    """
    try:
        result = recommendation_system.get_recommendations(
            strategy=strategy,
            max_recommendations=max_recommendations,
            risk_level=risk_level,
            force_refresh=force_refresh
        )
        
        return result
    
    except ValueError as e:
        logger.error(f"Invalid request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to get recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")
