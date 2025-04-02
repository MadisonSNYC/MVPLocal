"""
API routes for the Kalshi social feed integration.

This module provides API routes for accessing the Kalshi social feed data
and market sentiment insights.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from app.kalshi_api_client import KalshiApiClient
from app.social_feed import KalshiSocialFeed
from app.dependencies import get_kalshi_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("social_feed_routes")

# Create router
router = APIRouter(prefix="/api/social", tags=["social"])

# Initialize social feed instances
social_feed_instances = {}

def get_social_feed(kalshi_client: KalshiApiClient = Depends(get_kalshi_client)) -> KalshiSocialFeed:
    """
    Get or create a Kalshi social feed instance.
    
    Args:
        kalshi_client: Kalshi API client instance
        
    Returns:
        Kalshi social feed instance
    """
    client_id = id(kalshi_client)
    
    if client_id not in social_feed_instances:
        social_feed_instances[client_id] = KalshiSocialFeed(kalshi_client)
    
    return social_feed_instances[client_id]

@router.get("/feed")
async def get_social_feed_data(
    force_refresh: bool = Query(False, description="Whether to force a refresh of cached data"),
    social_feed: KalshiSocialFeed = Depends(get_social_feed)
) -> Dict[str, Any]:
    """
    Get the Kalshi social activity feed.
    
    Args:
        force_refresh: Whether to force a refresh of cached data
        social_feed: Kalshi social feed instance
        
    Returns:
        Dictionary with social feed data
    """
    try:
        result = social_feed.get_social_feed(force_refresh=force_refresh)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "Failed to get social feed data"))
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to get social feed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get social feed: {str(e)}")

@router.get("/sentiment/{market_id}")
async def get_market_sentiment(
    market_id: str,
    social_feed: KalshiSocialFeed = Depends(get_social_feed)
) -> Dict[str, Any]:
    """
    Get sentiment data for a specific market.
    
    Args:
        market_id: Market ID to get sentiment for
        social_feed: Kalshi social feed instance
        
    Returns:
        Dictionary with sentiment data
    """
    try:
        result = social_feed.get_market_sentiment(market_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to get market sentiment"))
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to get market sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get market sentiment: {str(e)}")

@router.get("/trending")
async def get_trending_markets(
    social_feed: KalshiSocialFeed = Depends(get_social_feed)
) -> Dict[str, Any]:
    """
    Get trending markets from the social feed.
    
    Args:
        social_feed: Kalshi social feed instance
        
    Returns:
        Dictionary with trending markets data
    """
    try:
        feed_data = social_feed.get_social_feed()
        
        if feed_data.get("status") == "error":
            raise HTTPException(status_code=500, detail=feed_data.get("message", "Failed to get social feed data"))
        
        trending_markets = feed_data.get("insights", {}).get("trending_markets", [])
        
        return {
            "trending_markets": trending_markets,
            "timestamp": feed_data.get("timestamp")
        }
    
    except Exception as e:
        logger.error(f"Failed to get trending markets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get trending markets: {str(e)}")
