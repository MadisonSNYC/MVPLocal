"""
API routes for the performance tracking system.

This module provides API routes for accessing and managing performance tracking data.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from app.kalshi_api_client import KalshiApiClient
from app.performance_tracking import PerformanceTracker
from app.dependencies import get_kalshi_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("performance_routes")

# Create router
router = APIRouter(prefix="/api/performance", tags=["performance"])

# Initialize performance tracker
performance_tracker = PerformanceTracker()

@router.get("/summary")
async def get_performance_summary() -> Dict[str, Any]:
    """
    Get a summary of overall performance across all strategies.
    
    Returns:
        Dictionary with performance summary
    """
    try:
        return performance_tracker.get_performance_summary()
    except Exception as e:
        logger.error(f"Failed to get performance summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance summary: {str(e)}")

@router.get("/strategies")
async def get_all_strategy_performance() -> Dict[str, Any]:
    """
    Get performance metrics for all strategies.
    
    Returns:
        Dictionary with performance metrics for all strategies
    """
    try:
        return {
            "strategies": performance_tracker.get_all_strategy_performance()
        }
    except Exception as e:
        logger.error(f"Failed to get strategy performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get strategy performance: {str(e)}")

@router.get("/strategies/{strategy}")
async def get_strategy_performance(strategy: str) -> Dict[str, Any]:
    """
    Get performance metrics for a specific strategy.
    
    Args:
        strategy: Strategy to get performance for
        
    Returns:
        Dictionary with performance metrics
    """
    try:
        return performance_tracker.get_strategy_performance(strategy)
    except Exception as e:
        logger.error(f"Failed to get strategy performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get strategy performance: {str(e)}")

@router.get("/recommendations")
async def get_recommendations(
    strategy: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> Dict[str, Any]:
    """
    Get recommendations with optional filtering.
    
    Args:
        strategy: Optional strategy to filter by
        status: Optional status to filter by
        limit: Maximum number of recommendations to return
        offset: Offset for pagination
        
    Returns:
        Dictionary with recommendations
    """
    try:
        recommendations = performance_tracker.get_recommendations(
            strategy=strategy,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to get recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.get("/timeframe")
async def get_performance_by_timeframe(
    timeframe: str = Query("all", regex="^(day|week|month|all)$"),
    strategy: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get performance metrics filtered by timeframe.
    
    Args:
        timeframe: Timeframe to filter by ("day", "week", "month", "all")
        strategy: Optional strategy to filter by
        
    Returns:
        Dictionary with performance metrics
    """
    try:
        return performance_tracker.get_performance_by_timeframe(
            strategy=strategy,
            timeframe=timeframe
        )
    except Exception as e:
        logger.error(f"Failed to get performance by timeframe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance by timeframe: {str(e)}")

@router.post("/recommendations")
async def record_recommendation(recommendation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Record a new recommendation for performance tracking.
    
    Args:
        recommendation: Recommendation dictionary
        
    Returns:
        Success message
    """
    try:
        performance_tracker.record_recommendation(recommendation)
        return {"message": "Recommendation recorded successfully"}
    except Exception as e:
        logger.error(f"Failed to record recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to record recommendation: {str(e)}")

@router.put("/recommendations/{recommendation_id}")
async def update_recommendation_status(
    recommendation_id: str,
    status: str = Query(..., regex="^(open|closed|expired)$"),
    exit_price: Optional[float] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update the status of a recommendation.
    
    Args:
        recommendation_id: ID of the recommendation to update
        status: New status ("open", "closed", "expired")
        exit_price: Exit price (if status is "closed")
        notes: Optional notes about the update
        
    Returns:
        Success message
    """
    try:
        success = performance_tracker.update_recommendation_status(
            recommendation_id=recommendation_id,
            status=status,
            exit_price=exit_price,
            notes=notes
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Recommendation {recommendation_id} not found")
        
        return {"message": f"Recommendation {recommendation_id} updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update recommendation: {str(e)}")

@router.post("/simulate")
async def simulate_historical_data(
    num_recommendations: int = Query(50, ge=10, le=1000)
) -> Dict[str, Any]:
    """
    Simulate historical performance data for testing.
    
    Args:
        num_recommendations: Number of recommendations to simulate
        
    Returns:
        Success message
    """
    try:
        performance_tracker.simulate_historical_data(num_recommendations=num_recommendations)
        return {"message": f"Simulated {num_recommendations} historical recommendations successfully"}
    except Exception as e:
        logger.error(f"Failed to simulate historical data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate historical data: {str(e)}")
