"""
Demo mode configuration for the Kalshi Trading Dashboard.

This module provides functionality for running the application in demo mode
with sample data and configurations.
"""

import logging
import json
import os
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("demo_mode")

class DemoModeManager:
    """
    Manager for demo mode functionality.
    
    This class provides sample data and configurations for running the
    application in demo mode without requiring real API credentials.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the demo mode manager.
        
        Args:
            data_dir: Directory to store demo data
        """
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "demo_data")
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Initialize demo data
        self._initialize_demo_data()
        
        logger.info("Initialized demo mode manager")
    
    def is_demo_mode_enabled(self) -> bool:
        """
        Check if demo mode is enabled.
        
        Returns:
            True if demo mode is enabled, False otherwise
        """
        # Check if demo mode flag file exists
        flag_file = os.path.join(self.data_dir, "demo_mode_enabled")
        return os.path.exists(flag_file)
    
    def enable_demo_mode(self) -> bool:
        """
        Enable demo mode.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create demo mode flag file
            flag_file = os.path.join(self.data_dir, "demo_mode_enabled")
            with open(flag_file, "w") as f:
                f.write("Demo mode enabled")
            
            logger.info("Demo mode enabled")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling demo mode: {str(e)}")
            return False
    
    def disable_demo_mode(self) -> bool:
        """
        Disable demo mode.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove demo mode flag file
            flag_file = os.path.join(self.data_dir, "demo_mode_enabled")
            if os.path.exists(flag_file):
                os.remove(flag_file)
            
            logger.info("Demo mode disabled")
            return True
            
        except Exception as e:
            logger.error(f"Error disabling demo mode: {str(e)}")
            return False
    
    def get_demo_markets(self) -> List[Dict[str, Any]]:
        """
        Get sample market data for demo mode.
        
        Returns:
            List of market dictionaries
        """
        markets_file = os.path.join(self.data_dir, "markets.json")
        
        try:
            with open(markets_file, "r") as f:
                markets = json.load(f)
            
            # Update timestamps and prices to be current
            self._update_market_data(markets)
            
            return markets
            
        except Exception as e:
            logger.error(f"Error loading demo markets: {str(e)}")
            return []
    
    def get_demo_portfolio(self) -> Dict[str, Any]:
        """
        Get sample portfolio data for demo mode.
        
        Returns:
            Portfolio dictionary
        """
        portfolio_file = os.path.join(self.data_dir, "portfolio.json")
        
        try:
            with open(portfolio_file, "r") as f:
                portfolio = json.load(f)
            
            # Update timestamps to be current
            self._update_portfolio_data(portfolio)
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error loading demo portfolio: {str(e)}")
            return {
                "balance": 1000.00,
                "positions": []
            }
    
    def get_demo_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get sample recommendations for demo mode.
        
        Returns:
            List of recommendation dictionaries
        """
        recommendations_file = os.path.join(self.data_dir, "recommendations.json")
        
        try:
            with open(recommendations_file, "r") as f:
                recommendations = json.load(f)
            
            # Update timestamps to be current
            self._update_recommendation_data(recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error loading demo recommendations: {str(e)}")
            return []
    
    def get_demo_social_feed(self) -> List[Dict[str, Any]]:
        """
        Get sample social feed data for demo mode.
        
        Returns:
            List of social feed item dictionaries
        """
        social_feed_file = os.path.join(self.data_dir, "social_feed.json")
        
        try:
            with open(social_feed_file, "r") as f:
                social_feed = json.load(f)
            
            # Update timestamps to be current
            self._update_social_feed_data(social_feed)
            
            return social_feed
            
        except Exception as e:
            logger.error(f"Error loading demo social feed: {str(e)}")
            return []
    
    def get_demo_performance_data(self) -> Dict[str, Any]:
        """
        Get sample performance data for demo mode.
        
        Returns:
            Performance data dictionary
        """
        performance_file = os.path.join(self.data_dir, "performance_data.json")
        
        try:
            with open(performance_file, "r") as f:
                performance_data = json.load(f)
            
            # Update timestamps to be current
            self._update_performance_data(performance_data)
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error loading demo performance data: {str(e)}")
            return {
                "recommendations": {},
                "performance": {}
            }
    
    def get_demo_config(self) -> Dict[str, Any]:
        """
        Get sample configuration for demo mode.
        
        Returns:
            Configuration dictionary
        """
        config_file = os.path.join(self.data_dir, "config.json")
        
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            
            return config
            
        except Exception as e:
            logger.error(f"Error loading demo config: {str(e)}")
            return {
                "yolo_mode": {
                    "enabled": False,
                    "max_spend_per_trade": 50.00,
                    "risk_tolerance": "medium",
                    "strategy": "hybrid"
                },
                "default_strategy": "hybrid",
                "default_risk_level": "medium",
                "refresh_interval": 60
            }
    
    def execute_demo_trade(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a simulated trade in demo mode.
        
        Args:
            order: Order dictionary
            
        Returns:
            Order result dictionary
        """
        # Generate a random order ID
        order_id = f"demo_order_{random.randint(10000, 99999)}"
        
        # 80% chance of success
        success = random.random() < 0.8
        
        if success:
            return {
                "order_id": order_id,
                "status": "filled",
                "filled_quantity": order.get("quantity", 1),
                "filled_price": order.get("price", 50),
                "timestamp": int(datetime.now().timestamp())
            }
        else:
            return {
                "order_id": order_id,
                "status": "rejected",
                "reason": "Insufficient funds or market closed",
                "timestamp": int(datetime.now().timestamp())
            }
    
    def _initialize_demo_data(self) -> None:
        """
        Initialize demo data files if they don't exist.
        """
        # Create markets data
        markets_file = os.path.join(self.data_dir, "markets.json")
        if not os.path.exists(markets_file):
            self._create_sample_markets(markets_file)
        
        # Create portfolio data
        portfolio_file = os.path.join(self.data_dir, "portfolio.json")
        if not os.path.exists(portfolio_file):
            self._create_sample_portfolio(portfolio_file)
        
        # Create recommendations data
        recommendations_file = os.path.join(self.data_dir, "recommendations.json")
        if not os.path.exists(recommendations_file):
            self._create_sample_recommendations(recommendations_file)
        
        # Create social feed data
        social_feed_file = os.path.join(self.data_dir, "social_feed.json")
        if not os.path.exists(social_feed_file):
            self._create_sample_social_feed(social_feed_file)
        
        # Create performance data
        performance_file = os.path.join(self.data_dir, "performance_data.json")
        if not os.path.exists(performance_file):
            self._create_sample_performance_data(performance_file)
        
        # Create config data
        config_file = os.path.join(self.data_dir, "config.json")
        if not os.path.exists(config_file):
            self._create_sample_config(config_file)
    
    def _create_sample_markets(self, file_path: str) -> None:
        """
        Create sample market data.
        
        Args:
            file_path: Path to save the data
        """
        # Create sample data for the six target hourly markets
        markets = [
            # Nasdaq (Hourly)
            {
                "id": "KXNASDAQ100U-25APR02H1200-T19529.99",
                "event_id": "KXNASDAQ100U-25APR02H1200",
                "series_id": "KXNASDAQ100U",
                "title": "Nasdaq 100 above 19,529.99 at 12:00 PM ET?",
                "subtitle": "Will the Nasdaq 100 index be above 19,529.99 at 12:00 PM ET?",
                "yes_price": 65,
                "no_price": 35,
                "last_price": 65,
                "volume": 12500,
                "open_interest": 8750,
                "close_time": int((datetime.now() + timedelta(hours=1)).timestamp()),
                "last_update_time": int(datetime.now().timestamp()),
                "status": "open"
            },
            # S&P 500 (Hourly)
            {
                "id": "KXINXU-25APR02H1200-T5654.9999",
                "event_id": "KXINXU-25APR02H1200",
                "series_id": "KXINXU",
                "title": "S&P 500 above 5,654.99 at 12:00 PM ET?",
                "subtitle": "Will the S&P 500 index be above 5,654.99 at 12:00 PM ET?",
                "yes_price": 72,
                "no_price": 28,
                "last_price": 72,
                "volume": 18750,
                "open_interest": 12500,
                "close_time": int((datetime.now() + timedelta(hours=1)).timestamp()),
                "last_update_time": int(datetime.now().timestamp()),
                "status": "open"
            },
            # Ethereum Price (Hourly)
            {
                "id": "KXETHD-25APR0212-T1909.99",
                "event_id": "KXETHD-25APR0212",
                "series_id": "KXETHD",
                "title": "Ethereum above $1,909.99 at 12:00 PM ET?",
                "subtitle": "Will Ethereum be trading above $1,909.99 at 12:00 PM ET?",
                "yes_price": 48,
                "no_price": 52,
                "last_price": 48,
                "volume": 9500,
                "open_interest": 6250,
                "close_time": int((datetime.now() + timedelta(hours=1)).timestamp()),
                "last_update_time": int(datetime.now().timestamp()),
                "status": "open"
            },
            # Ethereum Price Range (Hourly)
            {
                "id": "KXETH-25APR0212-B1920",
                "event_id": "KXETH-25APR0212",
                "series_id": "KXETH",
                "title": "Ethereum between $1,900 and $1,920 at 12:00 PM ET?",
                "subtitle": "Will Ethereum be trading between $1,900 and $1,920 at 12:00 PM ET?",
                "yes_price": 32,
                "no_price": 68,
                "last_price": 32,
                "volume": 7500,
                "open_interest": 5000,
                "close_time": int((datetime.now() + timedelta(hours=1)).timestamp()),
                "last_update_time": int(datetime.now().timestamp()),
                "status": "open"
            },
            # Bitcoin Price (Hourly)
            {
                "id": "KXBTCD-25APR0212-T87249.99",
                "event_id": "KXBTCD-25APR0212",
                "series_id": "KXBTCD",
                "title": "Bitcoin above $87,249.99 at 12:00 PM ET?",
                "subtitle": "Will Bitcoin be trading above $87,249.99 at 12:00 PM ET?",
                "yes_price": 58,
                "no_price": 42,
                "last_price": 58,
                "volume": 15000,
                "open_interest": 10000,
                "close_time": int((datetime.now() + timedelta(hours=1)).timestamp()),
                "last_update_time": int(datetime.now().timestamp()),
                "status": "open"
            },
            # Bitcoin Price Range (Hourly)
            {
                "id": "KXBTC-25APR0212-B87375",
                "event_id": "KXBTC-25APR0212",
                "series_id": "KXBTC",
                "title": "Bitcoin between $87,250 and $87,375 at 12:00 PM ET?",
                "subtitle": "Will Bitcoin be trading between $87,250 and $87,375 at 12:00 PM ET?",
                "yes_price": 25,
                "no_price": 75,
                "last_price": 25,
                "volume": 8750,
                "open_interest": 6250,
                "close_time": int((datetime.now() + timedelta(hours=1)).timestamp()),
                "last_update_time": int(datetime.now().timestamp()),
                "status": "open"
            }
        ]
        
        # Save to file
        with open(file_path, "w") as f:
            json.dump(markets, f, indent=2)
        
        logger.info(f"Created sample markets data at {file_path}")
    
    def _create_sample_portfolio(self, file_path: str) -> None:
        """
        Create sample portfolio data.
        
        Args:
            file_path: Path to save the data
        """
        portfolio = {
            "balance": 1000.00,
            "positions": [
                {
                    "market_id": "KXNASDAQ100U-25APR02H1200-T19529.99",
                    "event_id": "KXNASDAQ100U-25APR02H1200",
                    "series_id": "KXNASDAQ100U",
                    "title": "Nasdaq 100 above 19,529.99 at 12:00 PM ET?",
                    "position": "YES",
                    "quantity": 10,
                    "average_price": 62,
                    "current_price": 65,
                    "profit_loss": 30.00,
                    "timestamp": int((datetime.now() - timedelta(minutes=30)).timestamp())
                },
                {
                    "market_id": "KXBTCD-25APR0212-T87249.99",
                    "event_id": "KXBTCD-25APR0212",
                    "series_id": "KXBTCD",
                    "title": "Bitcoin above $87,249.99 at 12:00 PM ET?",
                    "position": "NO",
                    "quantity": 15,
                    "average_price": 45,
                    "current_price": 42,
                    "profit_loss": 45.00,
                    "timestamp": int((datetime.now() - timedelta(minutes=45)).timestamp())
                }
            ],
            "history": [
                {
                    "market_id": "KXINXU-25APR01H1200-T5650.9999",
                    "event_id": "KXINXU-25APR01H1200",
                    "series_id": "KXINXU",
                    "title": "S&P 500 above 5,650.99 at 12:00 PM ET?",
                    "position": "YES",
                    "quantity": 20,
                    "average_price": 68,
                    "exit_price": 100,
                    "profit_loss": 640.00,
                    "timestamp": int((datetime.now() - timedelta(days=1)).timestamp()),
                    "status": "settled",
                    "result": "win"
                },
                {
                    "market_id": "KXETHD-25APR0112-T1905.99",
                    "event_id": "KXETHD-25APR0112",
                    "series_id": "KXETHD",
                    "title": "Ethereum above $1,905.99 at 12:00 PM ET?",
                    "position": "NO",
                    "quantity": 25,
                    "average_price": 55,
                    "exit_price": 0,
                    "profit_loss": 1375.00,
                    "timestamp": int((datetime.now() - timedelta(days=1)).timestamp()),
                    "status": "settled",
                    "result": "win"
                }
            ]
        }
        
        # Save to file
        with open(file_path, "w") as f:
            json.dump(portfolio, f, indent=2)
        
        logger.info(f"Created sample portfolio data at {file_path}")
    
    def _create_sample_recommendations(self, file_path: str) -> None:
        """
        Create sample recommendation data.
        
        Args:
            file_path: Path to save the data
        """
        recommendations = [
            {
                "id": "rec_momentum_1",
                "market_id": "KXNASDAQ100U-25APR02H1200-T19529.99",
                "event_id": "KXNASDAQ100U-25APR02H1200",
                "series_id": "KXNASDAQ100U",
                "title": "Nasdaq 100 above 19,529.99 at 12:00 PM ET?",
                "strategy": "momentum",
                "action": "YES",
                "confidence": "High",
                "rationale": "Strong upward momentum in the Nasdaq 100 over the past hour with increasing volume. Technical indicators suggest continued upward movement.",
                "entry_price": 65,
                "target_exit": 80,
                "stop_loss": 55,
                "timestamp": int((datetime.now() - timedelta(minutes=15)).timestamp())
            },
            {
                "id": "rec_mean_reversion_1",
                "market_id": "KXINXU-25APR02H1200-T5654.9999",
                "event_id": "KXINXU-25APR02H1200",
                "series_id": "KXINXU",
                "title": "S&P 500 above 5,654.99 at 12:00 PM ET?",
                "strategy": "mean-reversion",
                "action": "NO",
                "confidence": "Medium",
                "rationale": "S&P 500 has moved significantly above its hourly moving average and appears overbought. Expecting reversion to the mean before the event close.",
                "entry_price": 28,
                "target_exit": 15,
                "stop_loss": 35,
                "timestamp": int((datetime.now() - timedelta(minutes=20)).timestamp())
            },
            {
                "id": "rec_arbitrage_1",
                "market_id": "KXETH-25APR0212-B1920",
                "event_id": "KXETH-25APR0212",
                "series_id": "KXETH",
                "title": "Ethereum between $1,900 and $1,920 at 12:00 PM ET?",
                "strategy": "arbitrage",
                "action": "YES",
                "confidence": "High",
                "rationale": "Detected price inconsistency between this market and related Ethereum price markets. The combined probability of other outcomes is less than 100%, creating an arbitrage opportunity.",
                "entry_price": 32,
                "target_exit": 45,
                "stop_loss": 25,
                "timestamp": int((datetime.now() - timedelta(minutes=25)).timestamp())
            },
            {
                "id": "rec_volatility_1",
                "market_id": "KXBTCD-25APR0212-T87249.99",
                "event_id": "KXBTCD-25APR0212",
                "series_id": "KXBTCD",
                "title": "Bitcoin above $87,249.99 at 12:00 PM ET?",
                "strategy": "volatility",
                "action": "YES",
                "confidence": "Medium",
                "rationale": "Bitcoin is experiencing increased volatility with a positive bias. Recent price action shows strong buying pressure after a period of consolidation.",
                "entry_price": 58,
                "target_exit": 75,
                "stop_loss": 45,
                "timestamp": int((datetime.now() - timedelta(minutes=30)).timestamp())
            },
            {
                "id": "rec_sentiment_1",
                "market_id": "KXBTC-25APR0212-B87375",
                "event_id": "KXBTC-25APR0212",
                "series_id": "KXBTC",
                "title": "Bitcoin between $87,250 and $87,375 at 12:00 PM ET?",
                "strategy": "sentiment",
                "action": "NO",
                "confidence": "Medium",
                "rationale": "Social sentiment analysis indicates strong bullish bias for Bitcoin, suggesting price is likely to move above the upper range bound before the event close.",
                "entry_price": 75,
                "target_exit": 85,
                "stop_loss": 65,
                "timestamp": int((datetime.now() - timedelta(minutes=35)).timestamp())
            },
            {
                "id": "rec_hybrid_1",
                "market_id": "KXETHD-25APR0212-T1909.99",
                "event_id": "KXETHD-25APR0212",
                "series_id": "KXETHD",
                "title": "Ethereum above $1,909.99 at 12:00 PM ET?",
                "strategy": "hybrid",
                "action": "NO",
                "confidence": "High",
                "rationale": "Combined analysis of momentum, sentiment, and volatility indicators suggests Ethereum is likely to experience a short-term pullback. Technical indicators show overbought conditions.",
                "entry_price": 52,
                "target_exit": 65,
                "stop_loss": 45,
                "timestamp": int((datetime.now() - timedelta(minutes=40)).timestamp())
            }
        ]
        
        # Save to file
        with open(file_path, "w") as f:
            json.dump(recommendations, f, indent=2)
        
        logger.info(f"Created sample recommendations data at {file_path}")
    
    def _create_sample_social_feed(self, file_path: str) -> None:
        """
        Create sample social feed data.
        
        Args:
            file_path: Path to save the data
        """
        social_feed = [
            {
                "id": "social_1",
                "user_id": "user_12345",
                "username": "crypto_trader",
                "activity_type": "trade",
                "market_id": "KXBTCD-25APR0212-T87249.99",
                "event_id": "KXBTCD-25APR0212",
                "series_id": "KXBTCD",
                "title": "Bitcoin above $87,249.99 at 12:00 PM ET?",
                "position": "YES",
                "quantity": 25,
                "price": 58,
                "timestamp": int((datetime.now() - timedelta(minutes=5)).timestamp()),
                "comment": "Bitcoin looking strong today! Expecting new highs."
            },
            {
                "id": "social_2",
                "user_id": "user_67890",
                "username": "index_investor",
                "activity_type": "trade",
                "market_id": "KXINXU-25APR02H1200-T5654.9999",
                "event_id": "KXINXU-25APR02H1200",
                "series_id": "KXINXU",
                "title": "S&P 500 above 5,654.99 at 12:00 PM ET?",
                "position": "NO",
                "quantity": 15,
                "price": 28,
                "timestamp": int((datetime.now() - timedelta(minutes=10)).timestamp()),
                "comment": "S&P looking overbought on the hourly chart. Taking a contrarian position."
            },
            {
                "id": "social_3",
                "user_id": "user_24680",
                "username": "eth_whale",
                "activity_type": "comment",
                "market_id": "KXETHD-25APR0212-T1909.99",
                "event_id": "KXETHD-25APR0212",
                "series_id": "KXETHD",
                "title": "Ethereum above $1,909.99 at 12:00 PM ET?",
                "timestamp": int((datetime.now() - timedelta(minutes=15)).timestamp()),
                "comment": "Ethereum has strong resistance at $1,910. Don't think it will break through before noon."
            },
            {
                "id": "social_4",
                "user_id": "user_13579",
                "username": "tech_analyst",
                "activity_type": "trade",
                "market_id": "KXNASDAQ100U-25APR02H1200-T19529.99",
                "event_id": "KXNASDAQ100U-25APR02H1200",
                "series_id": "KXNASDAQ100U",
                "title": "Nasdaq 100 above 19,529.99 at 12:00 PM ET?",
                "position": "YES",
                "quantity": 30,
                "price": 65,
                "timestamp": int((datetime.now() - timedelta(minutes=20)).timestamp()),
                "comment": "Tech stocks rallying this morning. Nasdaq looking very bullish!"
            },
            {
                "id": "social_5",
                "user_id": "user_97531",
                "username": "crypto_skeptic",
                "activity_type": "comment",
                "market_id": "KXBTC-25APR0212-B87375",
                "event_id": "KXBTC-25APR0212",
                "series_id": "KXBTC",
                "title": "Bitcoin between $87,250 and $87,375 at 12:00 PM ET?",
                "timestamp": int((datetime.now() - timedelta(minutes=25)).timestamp()),
                "comment": "Bitcoin volatility increasing. Doubt it will stay in this narrow range until noon."
            }
        ]
        
        # Save to file
        with open(file_path, "w") as f:
            json.dump(social_feed, f, indent=2)
        
        logger.info(f"Created sample social feed data at {file_path}")
    
    def _create_sample_performance_data(self, file_path: str) -> None:
        """
        Create sample performance data.
        
        Args:
            file_path: Path to save the data
        """
        # Create sample recommendations for each strategy
        strategies = ["momentum", "mean-reversion", "arbitrage", "volatility", "sentiment", "hybrid"]
        recommendations = {}
        
        for strategy in strategies:
            recommendations[strategy] = []
            
            # Add some closed recommendations (mix of wins and losses)
            for i in range(10):
                is_win = i % 3 != 0  # 2/3 win rate
                
                rec = {
                    "id": f"{strategy}_rec_{i}",
                    "market_id": f"market_{i}",
                    "strategy": strategy,
                    "action": "YES" if i % 2 == 0 else "NO",
                    "entry_price": 50 + (i * 2),
                    "target_exit": 65 + (i * 2) if i % 2 == 0 else 35 + (i * 2),
                    "stop_loss": 40 + (i * 2) if i % 2 == 0 else 60 + (i * 2),
                    "confidence": "High" if i % 3 == 0 else ("Medium" if i % 3 == 1 else "Low"),
                    "timestamp": int((datetime.now() - timedelta(days=1, hours=i)).timestamp()),
                    "status": "closed",
                    "exit_price": (65 + (i * 2)) if is_win and i % 2 == 0 else 
                                 (35 + (i * 2)) if is_win and i % 2 != 0 else
                                 (40 + (i * 2)) if not is_win and i % 2 == 0 else
                                 (60 + (i * 2)),
                    "exit_timestamp": int((datetime.now() - timedelta(hours=i)).timestamp()),
                    "result": "win" if is_win else "loss",
                    "profit_loss": 15 if is_win and i % 2 == 0 else
                                  15 if is_win and i % 2 != 0 else
                                  -10 if not is_win and i % 2 == 0 else
                                  -10,
                    "notes": ""
                }
                
                recommendations[strategy].append(rec)
            
            # Add some open recommendations
            for i in range(3):
                rec = {
                    "id": f"{strategy}_open_rec_{i}",
                    "market_id": f"open_market_{i}",
                    "strategy": strategy,
                    "action": "YES" if i % 2 == 0 else "NO",
                    "entry_price": 50 + (i * 5),
                    "target_exit": 65 + (i * 5) if i % 2 == 0 else 35 + (i * 5),
                    "stop_loss": 40 + (i * 5) if i % 2 == 0 else 60 + (i * 5),
                    "confidence": "High" if i % 3 == 0 else ("Medium" if i % 3 == 1 else "Low"),
                    "timestamp": int((datetime.now() - timedelta(hours=i)).timestamp()),
                    "status": "open",
                    "exit_price": None,
                    "exit_timestamp": None,
                    "result": None,
                    "profit_loss": None,
                    "notes": ""
                }
                
                recommendations[strategy].append(rec)
        
        # Calculate performance metrics for each strategy
        performance = {}
        
        for strategy in strategies:
            recs = recommendations[strategy]
            
            win_count = sum(1 for rec in recs if rec["result"] == "win")
            loss_count = sum(1 for rec in recs if rec["result"] == "loss")
            open_count = sum(1 for rec in recs if rec["status"] == "open")
            
            win_rate = (win_count / (win_count + loss_count)) * 100 if (win_count + loss_count) > 0 else 0
            
            profits = [rec["profit_loss"] for rec in recs if rec["result"] == "win" and rec["profit_loss"] is not None]
            losses = [rec["profit_loss"] for rec in recs if rec["result"] == "loss" and rec["profit_loss"] is not None]
            
            avg_profit = sum(profits) / len(profits) if profits else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
            total_profit_loss = sum(profits) + sum(losses)
            
            closed_recs = [rec for rec in recs if rec["status"] == "closed"]
            accuracy = (win_count / len(closed_recs)) * 100 if closed_recs else 0
            
            performance[strategy] = {
                "strategy": strategy,
                "win_count": win_count,
                "loss_count": loss_count,
                "open_count": open_count,
                "win_rate": win_rate,
                "avg_profit": avg_profit,
                "avg_loss": avg_loss,
                "total_profit_loss": total_profit_loss,
                "accuracy": accuracy,
                "last_updated": int(datetime.now().timestamp())
            }
        
        # Create performance data object
        performance_data = {
            "recommendations": recommendations,
            "performance": performance
        }
        
        # Save to file
        with open(file_path, "w") as f:
            json.dump(performance_data, f, indent=2)
        
        logger.info(f"Created sample performance data at {file_path}")
    
    def _create_sample_config(self, file_path: str) -> None:
        """
        Create sample configuration data.
        
        Args:
            file_path: Path to save the data
        """
        config = {
            "yolo_mode": {
                "enabled": False,
                "max_spend_per_trade": 50.00,
                "risk_tolerance": "medium",
                "strategy": "hybrid"
            },
            "default_strategy": "hybrid",
            "default_risk_level": "medium",
            "refresh_interval": 60,
            "target_markets": [
                "KXNASDAQ100U",  # Nasdaq (Hourly)
                "KXINXU",        # S&P 500 (Hourly)
                "KXETHD",        # Ethereum Price (Hourly)
                "KXETH",         # Ethereum Price Range (Hourly)
                "KXBTCD",        # Bitcoin Price (Hourly)
                "KXBTC"          # Bitcoin Price Range (Hourly)
            ]
        }
        
        # Save to file
        with open(file_path, "w") as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Created sample config data at {file_path}")
    
    def _update_market_data(self, markets: List[Dict[str, Any]]) -> None:
        """
        Update market data timestamps and prices to be current.
        
        Args:
            markets: List of market dictionaries to update
        """
        now = datetime.now()
        
        for market in markets:
            # Update timestamps
            market["close_time"] = int((now + timedelta(hours=1)).timestamp())
            market["last_update_time"] = int(now.timestamp())
            
            # Slightly adjust prices (random walk)
            for price_key in ["yes_price", "no_price", "last_price"]:
                if price_key in market:
                    change = random.randint(-3, 3)
                    market[price_key] = max(1, min(99, market[price_key] + change))
            
            # Ensure yes_price + no_price = 100
            if "yes_price" in market and "no_price" in market:
                market["no_price"] = 100 - market["yes_price"]
    
    def _update_portfolio_data(self, portfolio: Dict[str, Any]) -> None:
        """
        Update portfolio data timestamps to be current.
        
        Args:
            portfolio: Portfolio dictionary to update
        """
        now = datetime.now()
        
        # Update position timestamps
        for position in portfolio.get("positions", []):
            position["timestamp"] = int((now - timedelta(minutes=random.randint(10, 60))).timestamp())
        
        # Update history timestamps
        for history_item in portfolio.get("history", []):
            history_item["timestamp"] = int((now - timedelta(days=random.randint(1, 7))).timestamp())
    
    def _update_recommendation_data(self, recommendations: List[Dict[str, Any]]) -> None:
        """
        Update recommendation data timestamps to be current.
        
        Args:
            recommendations: List of recommendation dictionaries to update
        """
        now = datetime.now()
        
        for rec in recommendations:
            rec["timestamp"] = int((now - timedelta(minutes=random.randint(5, 60))).timestamp())
    
    def _update_social_feed_data(self, social_feed: List[Dict[str, Any]]) -> None:
        """
        Update social feed data timestamps to be current.
        
        Args:
            social_feed: List of social feed item dictionaries to update
        """
        now = datetime.now()
        
        for item in social_feed:
            item["timestamp"] = int((now - timedelta(minutes=random.randint(5, 30))).timestamp())
    
    def _update_performance_data(self, performance_data: Dict[str, Any]) -> None:
        """
        Update performance data timestamps to be current.
        
        Args:
            performance_data: Performance data dictionary to update
        """
        now = datetime.now()
        
        # Update recommendation timestamps
        for strategy, recs in performance_data.get("recommendations", {}).items():
            for rec in recs:
                if rec["status"] == "open":
                    rec["timestamp"] = int((now - timedelta(hours=random.randint(1, 12))).timestamp())
                else:
                    rec["timestamp"] = int((now - timedelta(days=random.randint(1, 7))).timestamp())
                    rec["exit_timestamp"] = int((now - timedelta(hours=random.randint(1, 12))).timestamp())
        
        # Update performance timestamps
        for strategy, perf in performance_data.get("performance", {}).items():
            perf["last_updated"] = int(now.timestamp())
