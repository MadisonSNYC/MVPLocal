"""
Update to the YOLO trading mode to incorporate market filtering.

This module updates the YOLO automated trading mode to focus only on
the specific hourly markets requested by the user.
"""

import logging
import json
import time
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from app.config import config
from app.kalshi_api_client import KalshiApiClient
from app.enhanced_ai_recommendations import EnhancedAIRecommendationSystem
from app.market_filter import HourlyMarketFilter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("yolo_trading")

class YOLOTradingMode:
    """
    YOLO Automated Trading Mode for Kalshi markets.
    
    This class implements automated trading based on AI recommendations
    with configurable risk parameters and trading caps.
    Now focuses only on specific hourly markets as requested by the user.
    """
    
    def __init__(self, kalshi_client: KalshiApiClient):
        """
        Initialize the YOLO trading mode.
        
        Args:
            kalshi_client: Kalshi API client instance
        """
        self.kalshi_client = kalshi_client
        self.recommendation_system = EnhancedAIRecommendationSystem(kalshi_client)
        self.market_filter = HourlyMarketFilter()
        
        # Trading parameters
        self.is_active = False
        self.trading_thread = None
        self.stop_event = threading.Event()
        
        # Default parameters (can be overridden)
        self.strategy = "hybrid"
        self.risk_level = "medium"
        self.max_spend_per_trade = 10.0  # Default $10 cap per trade
        self.max_trades_per_hour = 3
        self.max_total_spend = 50.0  # Default $50 total cap
        
        # Trading history
        self.trade_history = []
        self.total_spent = 0.0
        self.trades_this_hour = 0
        self.last_hour_reset = time.time()
        
        # Storage for trade history
        self.history_dir = Path(config.get("app", "data_dir")) / "yolo_history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Initialized YOLO Trading Mode with market filtering for specific hourly markets")
    
    def start(
        self,
        strategy: str = "hybrid",
        risk_level: str = "medium",
        max_spend_per_trade: float = 10.0,
        max_trades_per_hour: int = 3,
        max_total_spend: float = 50.0,
        market_conditions: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Start the YOLO trading mode.
        
        Args:
            strategy: Trading strategy to use
            risk_level: Risk level for trades
            max_spend_per_trade: Maximum amount to spend per trade in dollars
            max_trades_per_hour: Maximum number of trades per hour
            max_total_spend: Maximum total amount to spend in dollars
            market_conditions: Optional conditions that must be met for trading
            
        Returns:
            Dictionary with status information
        """
        if self.is_active:
            return {
                "status": "error",
                "message": "YOLO trading mode is already active"
            }
        
        # Validate parameters
        if max_spend_per_trade <= 0:
            return {
                "status": "error",
                "message": "Maximum spend per trade must be greater than zero"
            }
        
        if max_trades_per_hour <= 0:
            return {
                "status": "error",
                "message": "Maximum trades per hour must be greater than zero"
            }
        
        if max_total_spend <= 0:
            return {
                "status": "error",
                "message": "Maximum total spend must be greater than zero"
            }
        
        # Set parameters
        self.strategy = strategy
        self.risk_level = risk_level
        self.max_spend_per_trade = max_spend_per_trade
        self.max_trades_per_hour = max_trades_per_hour
        self.max_total_spend = max_total_spend
        self.market_conditions = market_conditions or {}
        
        # Reset trading state
        self.stop_event.clear()
        self.total_spent = 0.0
        self.trades_this_hour = 0
        self.last_hour_reset = time.time()
        
        # Start trading thread
        self.is_active = True
        self.trading_thread = threading.Thread(target=self._trading_loop)
        self.trading_thread.daemon = True
        self.trading_thread.start()
        
        logger.info(f"Started YOLO trading mode with strategy={strategy}, risk_level={risk_level}, max_spend_per_trade=${max_spend_per_trade}")
        
        return {
            "status": "success",
            "message": "YOLO trading mode started",
            "parameters": {
                "strategy": strategy,
                "risk_level": risk_level,
                "max_spend_per_trade": max_spend_per_trade,
                "max_trades_per_hour": max_trades_per_hour,
                "max_total_spend": max_total_spend,
                "market_conditions": market_conditions
            }
        }
    
    def stop(self) -> Dict[str, Any]:
        """
        Stop the YOLO trading mode.
        
        Returns:
            Dictionary with status information
        """
        if not self.is_active:
            return {
                "status": "error",
                "message": "YOLO trading mode is not active"
            }
        
        # Stop trading thread
        self.stop_event.set()
        if self.trading_thread:
            self.trading_thread.join(timeout=5.0)
        
        self.is_active = False
        
        # Save trading history
        self._save_trade_history()
        
        logger.info("Stopped YOLO trading mode")
        
        return {
            "status": "success",
            "message": "YOLO trading mode stopped",
            "summary": {
                "total_trades": len(self.trade_history),
                "total_spent": self.total_spent
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the YOLO trading mode.
        
        Returns:
            Dictionary with status information
        """
        return {
            "is_active": self.is_active,
            "strategy": self.strategy,
            "risk_level": self.risk_level,
            "max_spend_per_trade": self.max_spend_per_trade,
            "max_trades_per_hour": self.max_trades_per_hour,
            "max_total_spend": self.max_total_spend,
            "total_spent": self.total_spent,
            "trades_this_hour": self.trades_this_hour,
            "total_trades": len(self.trade_history),
            "recent_trades": self.trade_history[-5:] if self.trade_history else [],
            "target_markets": self.market_filter.TARGET_SERIES
        }
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """
        Get the complete trade history.
        
        Returns:
            List of trade dictionaries
        """
        return self.trade_history
    
    def _trading_loop(self) -> None:
        """
        Main trading loop that runs in a separate thread.
        """
        logger.info("Trading loop started")
        
        while not self.stop_event.is_set():
            try:
                # Check if we've reached the spending cap
                if self.total_spent >= self.max_total_spend:
                    logger.info(f"Reached maximum total spend (${self.total_spent}/${self.max_total_spend})")
                    self.stop_event.set()
                    break
                
                # Check if we need to reset the hourly trade counter
                current_time = time.time()
                if current_time - self.last_hour_reset >= 3600:
                    self.trades_this_hour = 0
                    self.last_hour_reset = current_time
                
                # Check if we've reached the hourly trade limit
                if self.trades_this_hour >= self.max_trades_per_hour:
                    logger.info(f"Reached maximum trades per hour ({self.trades_this_hour}/{self.max_trades_per_hour})")
                    # Sleep until the next hour
                    sleep_time = 3600 - (current_time - self.last_hour_reset)
                    logger.info(f"Sleeping for {sleep_time:.1f} seconds until next hour")
                    self.stop_event.wait(sleep_time)
                    continue
                
                # Check market conditions if specified
                if self.market_conditions and not self._check_market_conditions():
                    logger.info("Market conditions not met, waiting...")
                    self.stop_event.wait(300)  # Wait 5 minutes before checking again
                    continue
                
                # Get recommendations
                recommendations = self._get_recommendations()
                
                if not recommendations:
                    logger.info("No suitable recommendations found, waiting...")
                    self.stop_event.wait(300)  # Wait 5 minutes before trying again
                    continue
                
                # Execute trades based on recommendations
                for recommendation in recommendations:
                    if self.stop_event.is_set():
                        break
                    
                    # Verify this is a target market
                    market_id = recommendation.get("market_id", "")
                    if not self.market_filter.is_target_market(market_id):
                        logger.info(f"Skipping non-target market: {market_id}")
                        continue
                    
                    # Execute trade
                    trade_result = self._execute_trade(recommendation)
                    
                    if trade_result["status"] == "success":
                        # Update trading state
                        self.trade_history.append(trade_result)
                        self.total_spent += trade_result["cost"]
                        self.trades_this_hour += 1
                        
                        # Save trade history
                        self._save_trade_history()
                        
                        # Check if we've reached any limits
                        if self.total_spent >= self.max_total_spend:
                            logger.info(f"Reached maximum total spend (${self.total_spent}/${self.max_total_spend})")
                            break
                        
                        if self.trades_this_hour >= self.max_trades_per_hour:
                            logger.info(f"Reached maximum trades per hour ({self.trades_this_hour}/{self.max_trades_per_hour})")
                            break
                    
                    # Wait between trades
                    self.stop_event.wait(10)
                
                # Wait before getting new recommendations
                self.stop_event.wait(600)  # Wait 10 minutes between recommendation cycles
                
            except Exception as e:
                logger.error(f"Error in trading loop: {str(e)}")
                self.stop_event.wait(60)  # Wait 1 minute before retrying
        
        logger.info("Trading loop stopped")
    
    def _get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get and filter trade recommendations.
        
        Returns:
            List of filtered recommendation dictionaries
        """
        try:
            # Get recommendations from the AI system
            result = self.recommendation_system.get_recommendations(
                strategy=self.strategy,
                max_recommendations=10,  # Get more recommendations to filter
                risk_level=self.risk_level,
                force_refresh=True
            )
            
            recommendations = result.get("recommendations", [])
            
            if not recommendations:
                logger.warning("No recommendations received from AI system")
                return []
            
            # Filter recommendations based on confidence and other criteria
            filtered_recommendations = []
            
            for rec in recommendations:
                # Skip recommendations with low confidence
                if rec.get("confidence", "").lower() == "low" and self.risk_level != "high":
                    continue
                
                # Skip recommendations that would exceed the max spend per trade
                cost = rec.get("cost", 0)
                if cost > self.max_spend_per_trade:
                    continue
                
                # Skip recommendations for markets we've already traded
                market_id = rec.get("market_id", "")
                if any(trade["market_id"] == market_id for trade in self.trade_history):
                    continue
                
                # Verify this is a target market
                if not self.market_filter.is_target_market(market_id):
                    logger.info(f"Skipping non-target market: {market_id}")
                    continue
                
                # Add to filtered recommendations
                filtered_recommendations.append(rec)
            
            # Sort by confidence (High > Medium > Low)
            confidence_order = {"High": 3, "Medium": 2, "Low": 1}
            filtered_recommendations.sort(
                key=lambda x: confidence_order.get(x.get("confidence", ""), 0),
                reverse=True
            )
            
            # Limit to max trades per hour
            remaining_trades = self.max_trades_per_hour - self.trades_this_hour
            filtered_recommendations = filtered_recommendations[:remaining_trades]
            
            logger.info(f"Filtered {len(filtered_recommendations)} recommendations for trading")
            return filtered_recommendations
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {str(e)}")
            return []
    
    def _execute_trade(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trade based on a recommendation.
        
        Args:
            recommendation: Recommendation dictionary
            
        Returns:
            Dictionary with trade result
        """
        market_id = recommendation.get("market_id", "")
        action = recommendation.get("action", "")
        contracts = recommendation.get("contracts", 0)
        cost = recommendation.get("cost", 0)
        
        if not market_id or not action or contracts <= 0:
            return {
                "status": "error",
                "message": "Invalid recommendation",
                "recommendation": recommendation
            }
        
        # Verify this is a target market
        if not self.market_filter.is_target_market(market_id):
            return {
                "status": "error",
                "message": "Not a target hourly market",
                "recommendation": recommendation
            }
        
        try:
            logger.info(f"Executing trade: {action} {contracts} contracts in market {market_id}")
            
            # Prepare order parameters
            order_params = {
                "market_id": market_id,
                "side": action.lower(),
                "type": "limit",
                "count": contracts,
                "yes_price" if action.lower() == "yes" else "no_price": int(recommendation.get("probability", 50)),
                "client_order_id": f"yolo_{int(time.time())}"
            }
            
            # Execute order
            order_result = self.kalshi_client.create_order(**order_params)
            
            if "order" not in order_result:
                return {
                    "status": "error",
                    "message": "Failed to create order",
                    "recommendation": recommendation,
                    "order_result": order_result
                }
            
            # Create trade record
            trade = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "market_id": market_id,
                "market_title": recommendation.get("market", ""),
                "action": action,
                "contracts": contracts,
                "cost": cost,
                "probability": recommendation.get("probability", 0),
                "target_exit": recommendation.get("target_exit", 0),
                "stop_loss": recommendation.get("stop_loss", 0),
                "confidence": recommendation.get("confidence", ""),
                "rationale": recommendation.get("rationale", ""),
                "order_id": order_result["order"].get("order_id", ""),
                "strategy": self.strategy,
                "risk_level": self.risk_level
            }
            
            logger.info(f"Trade executed successfully: {action} {contracts} contracts in market {market_id}")
            return trade
            
        except Exception as e:
            logger.error(f"Failed to execute trade: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to execute trade: {str(e)}",
                "recommendation": recommendation
            }
    
    def _check_market_conditions(self) -> bool:
        """
        Check if market conditions meet the specified criteria.
        
        Returns:
            True if conditions are met, False otherwise
        """
        if not self.market_conditions:
            return True
        
        try:
            # Get exchange status
            exchange_status = self.kalshi_client.get_exchange_status()
            
            # Check if exchange is open
            if self.market_conditions.get("exchange_open", False):
                if exchange_status.get("exchange_status", "") != "open":
                    logger.info("Exchange is not open")
                    return False
            
            # Add more condition checks as needed
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check market conditions: {str(e)}")
            return False
    
    def _save_trade_history(self) -> None:
        """
        Save the trade history to a file.
        """
        if not self.trade_history:
            return
        
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"yolo_trades_{timestamp}.json"
            filepath = self.history_dir / filename
            
            # Save to file
            with open(filepath, "w") as f:
                json.dump({
                    "trades": self.trade_history,
                    "parameters": {
                        "strategy": self.strategy,
                        "risk_level": self.risk_level,
                        "max_spend_per_trade": self.max_spend_per_trade,
                        "max_trades_per_hour": self.max_trades_per_hour,
                        "max_total_spend": self.max_total_spend,
                        "target_markets": self.market_filter.TARGET_SERIES
                    },
                    "summary": {
                        "total_trades": len(self.trade_history),
                        "total_spent": self.total_spent
                    }
                }, f, indent=2)
            
            logger.info(f"Saved trade history to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save trade history: {str(e)}")
