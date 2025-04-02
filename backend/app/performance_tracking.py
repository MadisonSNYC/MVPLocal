"""
Historical performance tracking for trading strategies.

This module implements a system to track and analyze the historical performance
of trading strategies, including win/loss ratios, profitability, and accuracy.
"""

import logging
import json
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from app.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("performance_tracking")

class PerformanceTracker:
    """
    Performance tracking system for trading strategies.
    
    This class tracks and analyzes the historical performance of trading strategies,
    including win/loss ratios, profitability, and accuracy.
    """
    
    def __init__(self):
        """
        Initialize the performance tracker.
        """
        self.data_dir = Path(config.get("app", "data_dir"))
        self.performance_dir = self.data_dir / "performance"
        
        # Create performance directory if it doesn't exist
        if not self.performance_dir.exists():
            self.performance_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize performance data
        self.performance_data = self._load_performance_data()
        
        logger.info("Initialized performance tracker")
    
    def record_recommendation(self, recommendation: Dict[str, Any]) -> None:
        """
        Record a new recommendation for performance tracking.
        
        Args:
            recommendation: Recommendation dictionary
        """
        if not recommendation:
            return
        
        # Extract recommendation details
        recommendation_id = recommendation.get("id", f"rec_{int(time.time())}_{hash(str(recommendation))}")
        market_id = recommendation.get("market_id", "")
        strategy = recommendation.get("strategy", "unknown")
        action = recommendation.get("action", "")
        entry_price = recommendation.get("probability", 0)
        target_exit = recommendation.get("target_exit", 0)
        stop_loss = recommendation.get("stop_loss", 0)
        confidence = recommendation.get("confidence", "Medium")
        timestamp = int(time.time())
        
        # Create recommendation record
        record = {
            "id": recommendation_id,
            "market_id": market_id,
            "strategy": strategy,
            "action": action,
            "entry_price": entry_price,
            "target_exit": target_exit,
            "stop_loss": stop_loss,
            "confidence": confidence,
            "timestamp": timestamp,
            "status": "open",
            "exit_price": None,
            "exit_timestamp": None,
            "result": None,
            "profit_loss": None,
            "notes": ""
        }
        
        # Add to performance data
        if strategy not in self.performance_data["recommendations"]:
            self.performance_data["recommendations"][strategy] = []
        
        self.performance_data["recommendations"][strategy].append(record)
        
        # Save performance data
        self._save_performance_data()
        
        logger.info(f"Recorded new recommendation: {recommendation_id} for strategy: {strategy}")
    
    def update_recommendation_status(
        self, 
        recommendation_id: str, 
        status: str, 
        exit_price: Optional[float] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update the status of a recommendation.
        
        Args:
            recommendation_id: ID of the recommendation to update
            status: New status ("open", "closed", "expired")
            exit_price: Exit price (if status is "closed")
            notes: Optional notes about the update
            
        Returns:
            True if the update was successful, False otherwise
        """
        # Find the recommendation
        for strategy, recommendations in self.performance_data["recommendations"].items():
            for i, rec in enumerate(recommendations):
                if rec["id"] == recommendation_id:
                    # Update status
                    self.performance_data["recommendations"][strategy][i]["status"] = status
                    
                    # Update exit details if provided
                    if exit_price is not None:
                        self.performance_data["recommendations"][strategy][i]["exit_price"] = exit_price
                        self.performance_data["recommendations"][strategy][i]["exit_timestamp"] = int(time.time())
                        
                        # Calculate result and profit/loss
                        entry_price = rec["entry_price"]
                        action = rec["action"]
                        
                        if action == "YES":
                            result = "win" if exit_price > entry_price else "loss"
                            profit_loss = exit_price - entry_price
                        else:  # action == "NO"
                            result = "win" if exit_price < entry_price else "loss"
                            profit_loss = entry_price - exit_price
                        
                        self.performance_data["recommendations"][strategy][i]["result"] = result
                        self.performance_data["recommendations"][strategy][i]["profit_loss"] = profit_loss
                    
                    # Update notes if provided
                    if notes:
                        self.performance_data["recommendations"][strategy][i]["notes"] = notes
                    
                    # Save performance data
                    self._save_performance_data()
                    
                    # Update strategy performance metrics
                    self._update_strategy_performance(strategy)
                    
                    logger.info(f"Updated recommendation {recommendation_id} status to {status}")
                    return True
        
        logger.warning(f"Recommendation {recommendation_id} not found")
        return False
    
    def get_strategy_performance(self, strategy: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific strategy.
        
        Args:
            strategy: Strategy to get performance for
            
        Returns:
            Dictionary with performance metrics
        """
        if strategy not in self.performance_data["performance"]:
            return {
                "strategy": strategy,
                "win_count": 0,
                "loss_count": 0,
                "open_count": 0,
                "win_rate": 0,
                "avg_profit": 0,
                "avg_loss": 0,
                "total_profit_loss": 0,
                "accuracy": 0,
                "last_updated": int(time.time())
            }
        
        return self.performance_data["performance"][strategy]
    
    def get_all_strategy_performance(self) -> List[Dict[str, Any]]:
        """
        Get performance metrics for all strategies.
        
        Returns:
            List of dictionaries with performance metrics
        """
        return list(self.performance_data["performance"].values())
    
    def get_recommendations(
        self, 
        strategy: Optional[str] = None, 
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations with optional filtering.
        
        Args:
            strategy: Optional strategy to filter by
            status: Optional status to filter by
            limit: Maximum number of recommendations to return
            offset: Offset for pagination
            
        Returns:
            List of recommendation dictionaries
        """
        all_recommendations = []
        
        # Collect recommendations from all strategies or the specified one
        if strategy:
            if strategy in self.performance_data["recommendations"]:
                all_recommendations.extend(self.performance_data["recommendations"][strategy])
        else:
            for strategy_recs in self.performance_data["recommendations"].values():
                all_recommendations.extend(strategy_recs)
        
        # Filter by status if specified
        if status:
            all_recommendations = [rec for rec in all_recommendations if rec["status"] == status]
        
        # Sort by timestamp (newest first)
        all_recommendations.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination
        paginated_recommendations = all_recommendations[offset:offset + limit]
        
        return paginated_recommendations
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a summary of overall performance across all strategies.
        
        Returns:
            Dictionary with performance summary
        """
        total_recommendations = 0
        total_wins = 0
        total_losses = 0
        total_open = 0
        total_profit_loss = 0
        
        for strategy, metrics in self.performance_data["performance"].items():
            total_wins += metrics["win_count"]
            total_losses += metrics["loss_count"]
            total_open += metrics["open_count"]
            total_profit_loss += metrics["total_profit_loss"]
        
        total_recommendations = total_wins + total_losses + total_open
        win_rate = (total_wins / (total_wins + total_losses)) * 100 if (total_wins + total_losses) > 0 else 0
        
        return {
            "total_recommendations": total_recommendations,
            "total_wins": total_wins,
            "total_losses": total_losses,
            "total_open": total_open,
            "win_rate": win_rate,
            "total_profit_loss": total_profit_loss,
            "last_updated": int(time.time())
        }
    
    def get_performance_by_timeframe(
        self, 
        strategy: Optional[str] = None,
        timeframe: str = "all"
    ) -> Dict[str, Any]:
        """
        Get performance metrics filtered by timeframe.
        
        Args:
            strategy: Optional strategy to filter by
            timeframe: Timeframe to filter by ("day", "week", "month", "all")
            
        Returns:
            Dictionary with performance metrics
        """
        # Determine cutoff timestamp based on timeframe
        now = datetime.now()
        cutoff_timestamp = None
        
        if timeframe == "day":
            cutoff_timestamp = int((now - timedelta(days=1)).timestamp())
        elif timeframe == "week":
            cutoff_timestamp = int((now - timedelta(weeks=1)).timestamp())
        elif timeframe == "month":
            cutoff_timestamp = int((now - timedelta(days=30)).timestamp())
        
        # Get recommendations within the timeframe
        recommendations = self.get_recommendations(strategy=strategy)
        
        if cutoff_timestamp:
            recommendations = [rec for rec in recommendations if rec["timestamp"] >= cutoff_timestamp]
        
        # Calculate performance metrics
        win_count = sum(1 for rec in recommendations if rec["result"] == "win")
        loss_count = sum(1 for rec in recommendations if rec["result"] == "loss")
        open_count = sum(1 for rec in recommendations if rec["status"] == "open")
        
        win_rate = (win_count / (win_count + loss_count)) * 100 if (win_count + loss_count) > 0 else 0
        
        profits = [rec["profit_loss"] for rec in recommendations if rec["result"] == "win" and rec["profit_loss"] is not None]
        losses = [rec["profit_loss"] for rec in recommendations if rec["result"] == "loss" and rec["profit_loss"] is not None]
        
        avg_profit = sum(profits) / len(profits) if profits else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        total_profit_loss = sum(profits) + sum(losses)
        
        return {
            "timeframe": timeframe,
            "strategy": strategy if strategy else "all",
            "win_count": win_count,
            "loss_count": loss_count,
            "open_count": open_count,
            "win_rate": win_rate,
            "avg_profit": avg_profit,
            "avg_loss": avg_loss,
            "total_profit_loss": total_profit_loss,
            "recommendation_count": len(recommendations),
            "last_updated": int(time.time())
        }
    
    def _update_strategy_performance(self, strategy: str) -> None:
        """
        Update performance metrics for a strategy.
        
        Args:
            strategy: Strategy to update metrics for
        """
        if strategy not in self.performance_data["recommendations"]:
            return
        
        recommendations = self.performance_data["recommendations"][strategy]
        
        # Count wins, losses, and open recommendations
        win_count = sum(1 for rec in recommendations if rec["result"] == "win")
        loss_count = sum(1 for rec in recommendations if rec["result"] == "loss")
        open_count = sum(1 for rec in recommendations if rec["status"] == "open")
        
        # Calculate win rate
        win_rate = (win_count / (win_count + loss_count)) * 100 if (win_count + loss_count) > 0 else 0
        
        # Calculate average profit and loss
        profits = [rec["profit_loss"] for rec in recommendations if rec["result"] == "win" and rec["profit_loss"] is not None]
        losses = [rec["profit_loss"] for rec in recommendations if rec["result"] == "loss" and rec["profit_loss"] is not None]
        
        avg_profit = sum(profits) / len(profits) if profits else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        total_profit_loss = sum(profits) + sum(losses)
        
        # Calculate accuracy (percentage of recommendations that reached target before stop loss)
        closed_recs = [rec for rec in recommendations if rec["status"] == "closed"]
        accuracy = (win_count / len(closed_recs)) * 100 if closed_recs else 0
        
        # Update performance metrics
        self.performance_data["performance"][strategy] = {
            "strategy": strategy,
            "win_count": win_count,
            "loss_count": loss_count,
            "open_count": open_count,
            "win_rate": win_rate,
            "avg_profit": avg_profit,
            "avg_loss": avg_loss,
            "total_profit_loss": total_profit_loss,
            "accuracy": accuracy,
            "last_updated": int(time.time())
        }
        
        # Save performance data
        self._save_performance_data()
        
        logger.info(f"Updated performance metrics for strategy: {strategy}")
    
    def _load_performance_data(self) -> Dict[str, Any]:
        """
        Load performance data from disk.
        
        Returns:
            Dictionary with performance data
        """
        performance_file = self.performance_dir / "performance_data.json"
        
        if not performance_file.exists():
            # Initialize empty performance data
            return {
                "recommendations": {},
                "performance": {}
            }
        
        try:
            with open(performance_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load performance data: {str(e)}")
            return {
                "recommendations": {},
                "performance": {}
            }
    
    def _save_performance_data(self) -> None:
        """
        Save performance data to disk.
        """
        performance_file = self.performance_dir / "performance_data.json"
        
        try:
            with open(performance_file, "w") as f:
                json.dump(self.performance_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save performance data: {str(e)}")
    
    def simulate_historical_data(self, num_recommendations: int = 50) -> None:
        """
        Simulate historical performance data for testing.
        
        Args:
            num_recommendations: Number of recommendations to simulate
        """
        import random
        
        strategies = ["momentum", "mean-reversion", "hybrid", "arbitrage", "volatility", "sentiment", "combined"]
        actions = ["YES", "NO"]
        confidences = ["High", "Medium", "Low"]
        statuses = ["open", "closed"]
        results = ["win", "loss"]
        
        # Clear existing data
        self.performance_data = {
            "recommendations": {},
            "performance": {}
        }
        
        # Initialize recommendation lists for each strategy
        for strategy in strategies:
            self.performance_data["recommendations"][strategy] = []
        
        # Generate random recommendations
        for i in range(num_recommendations):
            strategy = random.choice(strategies)
            action = random.choice(actions)
            confidence = random.choice(confidences)
            status = random.choice(statuses)
            
            # Generate random prices
            entry_price = random.randint(10, 90)
            target_exit = entry_price + random.randint(5, 15) if action == "YES" else entry_price - random.randint(5, 15)
            stop_loss = entry_price - random.randint(5, 10) if action == "YES" else entry_price + random.randint(5, 10)
            
            # Create recommendation record
            record = {
                "id": f"sim_rec_{i}",
                "market_id": f"market_{random.randint(1, 10)}",
                "strategy": strategy,
                "action": action,
                "entry_price": entry_price,
                "target_exit": target_exit,
                "stop_loss": stop_loss,
                "confidence": confidence,
                "timestamp": int(time.time()) - random.randint(0, 30 * 24 * 60 * 60),  # Random time in the last 30 days
                "status": status,
                "exit_price": None,
                "exit_timestamp": None,
                "result": None,
                "profit_loss": None,
                "notes": ""
            }
            
            # Add exit details for closed recommendations
            if status == "closed":
                result = random.choice(results)
                
                if result == "win":
                    exit_price = target_exit
                else:
                    exit_price = stop_loss
                
                record["exit_price"] = exit_price
                record["exit_timestamp"] = record["timestamp"] + random.randint(1, 24 * 60 * 60)  # 1 to 24 hours later
                record["result"] = result
                
                # Calculate profit/loss
                if action == "YES":
                    profit_loss = exit_price - entry_price
                else:  # action == "NO"
                    profit_loss = entry_price - exit_price
                
                record["profit_loss"] = profit_loss
            
            # Add to performance data
            self.performance_data["recommendations"][strategy].append(record)
        
        # Update performance metrics for each strategy
        for strategy in strategies:
            self._update_strategy_performance(strategy)
        
        # Save performance data
        self._save_performance_data()
        
        logger.info(f"Simulated {num_recommendations} historical recommendations")
