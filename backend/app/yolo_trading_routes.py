"""
API routes for the YOLO automated trading mode.

This module provides API routes for controlling the YOLO automated trading mode.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Body

from app.kalshi_api_client import KalshiApiClient
from app.yolo_trading import YOLOTradingMode
from app.dependencies import get_kalshi_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("yolo_trading_routes")

# Create router
router = APIRouter(prefix="/api/yolo", tags=["yolo"])

# Initialize YOLO trading instances
yolo_instances = {}

def get_yolo_trading(kalshi_client: KalshiApiClient = Depends(get_kalshi_client)) -> YOLOTradingMode:
    """
    Get or create a YOLO trading instance.
    
    Args:
        kalshi_client: Kalshi API client instance
        
    Returns:
        YOLO trading instance
    """
    client_id = id(kalshi_client)
    
    if client_id not in yolo_instances:
        yolo_instances[client_id] = YOLOTradingMode(kalshi_client)
    
    return yolo_instances[client_id]

@router.post("/start")
async def start_yolo_trading(
    strategy: str = Query("hybrid", description="Trading strategy to use"),
    risk_level: str = Query("medium", description="Risk level for trades"),
    max_spend_per_trade: float = Query(10.0, description="Maximum amount to spend per trade in dollars"),
    max_trades_per_hour: int = Query(3, description="Maximum number of trades per hour"),
    max_total_spend: float = Query(50.0, description="Maximum total amount to spend in dollars"),
    market_conditions: Dict[str, Any] = Body({}, description="Optional conditions that must be met for trading"),
    yolo_trading: YOLOTradingMode = Depends(get_yolo_trading)
) -> Dict[str, Any]:
    """
    Start the YOLO automated trading mode.
    
    Args:
        strategy: Trading strategy to use
        risk_level: Risk level for trades
        max_spend_per_trade: Maximum amount to spend per trade in dollars
        max_trades_per_hour: Maximum number of trades per hour
        max_total_spend: Maximum total amount to spend in dollars
        market_conditions: Optional conditions that must be met for trading
        yolo_trading: YOLO trading instance
        
    Returns:
        Dictionary with status information
    """
    try:
        result = yolo_trading.start(
            strategy=strategy,
            risk_level=risk_level,
            max_spend_per_trade=max_spend_per_trade,
            max_trades_per_hour=max_trades_per_hour,
            max_total_spend=max_total_spend,
            market_conditions=market_conditions
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to start YOLO trading: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start YOLO trading: {str(e)}")

@router.post("/stop")
async def stop_yolo_trading(
    yolo_trading: YOLOTradingMode = Depends(get_yolo_trading)
) -> Dict[str, Any]:
    """
    Stop the YOLO automated trading mode.
    
    Args:
        yolo_trading: YOLO trading instance
        
    Returns:
        Dictionary with status information
    """
    try:
        result = yolo_trading.stop()
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to stop YOLO trading: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop YOLO trading: {str(e)}")

@router.get("/status")
async def get_yolo_status(
    yolo_trading: YOLOTradingMode = Depends(get_yolo_trading)
) -> Dict[str, Any]:
    """
    Get the current status of the YOLO automated trading mode.
    
    Args:
        yolo_trading: YOLO trading instance
        
    Returns:
        Dictionary with status information
    """
    try:
        return yolo_trading.get_status()
    
    except Exception as e:
        logger.error(f"Failed to get YOLO status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get YOLO status: {str(e)}")

@router.get("/history")
async def get_yolo_history(
    yolo_trading: YOLOTradingMode = Depends(get_yolo_trading)
) -> Dict[str, Any]:
    """
    Get the complete trade history of the YOLO automated trading mode.
    
    Args:
        yolo_trading: YOLO trading instance
        
    Returns:
        Dictionary with trade history
    """
    try:
        trade_history = yolo_trading.get_trade_history()
        
        return {
            "trades": trade_history,
            "total_trades": len(trade_history)
        }
    
    except Exception as e:
        logger.error(f"Failed to get YOLO history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get YOLO history: {str(e)}")
