"""
FastAPI routes for AI recommendations.

This module adds routes to the FastAPI application for AI-powered trade recommendations.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional, Any, Union

from app.kalshi_api_client import KalshiApiClient
from app.ai_recommendations import AIRecommendationSystem
from app.dependencies import get_kalshi_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api_recommendations")

# Create router
router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

# Dependency to get the AI recommendation system
def get_recommendation_system(
    kalshi_client: KalshiApiClient = Depends(get_kalshi_client)
) -> AIRecommendationSystem:
    """
    Get an instance of the AI recommendation system.
    
    Args:
        kalshi_client: Kalshi API client instance
        
    Returns:
        AIRecommendationSystem instance
    """
    try:
        return AIRecommendationSystem(kalshi_client)
    except Exception as e:
        logger.error(f"Failed to initialize AI recommendation system: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to initialize AI recommendation system: {str(e)}"
        )

@router.get("/")
async def get_recommendations(
    strategy: str = Query(..., description="Strategy to use (momentum or mean-reversion)"),
    max_recommendations: int = Query(5, ge=1, le=10, description="Maximum number of recommendations to return"),
    risk_level: str = Query("medium", description="Risk level (low, medium, or high)"),
    force_refresh: bool = Query(False, description="Whether to force a refresh of cached recommendations"),
    recommendation_system: AIRecommendationSystem = Depends(get_recommendation_system)
):
    """
    Get trade recommendations based on the specified strategy.
    
    Args:
        strategy: Strategy to use ("momentum" or "mean-reversion")
        max_recommendations: Maximum number of recommendations to return
        risk_level: Risk level ("low", "medium", or "high")
        force_refresh: Whether to force a refresh of cached recommendations
        recommendation_system: AI recommendation system instance
        
    Returns:
        List of recommendation dictionaries
    """
    try:
        # Validate strategy
        if strategy.lower() not in ["momentum", "mean-reversion"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid strategy: {strategy}. Must be 'momentum' or 'mean-reversion'"
            )
        
        # Validate risk level
        if risk_level.lower() not in ["low", "medium", "high"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid risk level: {risk_level}. Must be 'low', 'medium', or 'high'"
            )
        
        # Get recommendations
        recommendations = recommendation_system.get_recommendations(
            strategy=strategy.lower(),
            max_recommendations=max_recommendations,
            risk_level=risk_level.lower(),
            force_refresh=force_refresh
        )
        
        return {
            "strategy": strategy.lower(),
            "risk_level": risk_level.lower(),
            "recommendations": recommendations
        }
    
    except ValueError as e:
        logger.error(f"Invalid request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to get recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.get("/strategies")
async def get_available_strategies():
    """
    Get available recommendation strategies.
    
    Returns:
        List of available strategies with descriptions
    """
    return {
        "strategies": [
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
            }
        ]
    }
