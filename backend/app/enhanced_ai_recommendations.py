"""
Update to the enhanced AI recommendation system to incorporate additional trading strategies.

This module updates the enhanced AI recommendation system to use the new
trading strategies: Arbitrage, Volatility-Based, and Sentiment-Driven.
"""

import logging
import json
import os
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from app.config import config
from app.kalshi_api_client import KalshiApiClient
from app.ai_models.enhanced_openai_model import EnhancedOpenAIRecommendationModel
from app.ai_models.hybrid_model import HybridRecommendationModel
from app.ai_models.rule_based_model import RuleBasedRecommendationModel
from app.market_filter import HourlyMarketFilter
from app.social_feed import KalshiSocialFeed
from app.strategy_integration import StrategyManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced_ai_recommendations")

class EnhancedAIRecommendationSystem:
    """
    Enhanced AI-powered recommendation system for Kalshi trading.
    Uses improved OpenAI integration with better prompt engineering and richer market context.
    Now includes additional trading strategies and focuses only on specific hourly markets.
    """
    
    def __init__(self, kalshi_client: KalshiApiClient):
        """
        Initialize the enhanced AI recommendation system.
        
        Args:
            kalshi_client: Kalshi API client instance
        """
        self.kalshi_client = kalshi_client
        self.enhanced_openai_model = EnhancedOpenAIRecommendationModel()
        self.hybrid_model = HybridRecommendationModel()
        self.rule_based_model = RuleBasedRecommendationModel()
        self.market_filter = HourlyMarketFilter()
        
        # Initialize social feed and strategy manager
        self.social_feed = KalshiSocialFeed(kalshi_client)
        self.strategy_manager = StrategyManager(kalshi_client, self.social_feed)
        
        self.openai_enabled = bool(config.get("ai", "api_key"))
        self.use_enhanced_model = config.get("ai", "use_enhanced_model", True)
        
        self.cache_enabled = config.get("ai", "cache_recommendations")
        self.cache_ttl = config.get("ai", "cache_ttl_minutes") * 60  # Convert to seconds
        self.cache_dir = Path(config.get("app", "cache_dir"))
        
        # Create cache directory if it doesn't exist
        if self.cache_enabled and not (self.cache_dir / "recommendations").exists():
            (self.cache_dir / "recommendations").mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized enhanced AI recommendation system with additional trading strategies")
    
    def get_recommendations(
        self, 
        strategy: str, 
        max_recommendations: int = 5,
        risk_level: str = "medium",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get trade recommendations based on the specified strategy.
        
        Args:
            strategy: Strategy to use ("momentum", "mean-reversion", "hybrid", "arbitrage", "volatility", "sentiment", "combined")
            max_recommendations: Maximum number of recommendations to return
            risk_level: Risk level ("low", "medium", or "high")
            force_refresh: Whether to force a refresh of cached recommendations
            
        Returns:
            Dictionary with recommendations and metadata
        """
        # Validate strategy
        valid_strategies = ["momentum", "mean-reversion", "hybrid", "arbitrage", "volatility", "sentiment", "combined"]
        if strategy.lower() not in valid_strategies:
            logger.error(f"Invalid strategy: {strategy}")
            raise ValueError(f"Invalid strategy: {strategy}. Must be one of {valid_strategies}")
        
        # Validate risk level
        valid_risk_levels = ["low", "medium", "high"]
        if risk_level.lower() not in valid_risk_levels:
            logger.error(f"Invalid risk level: {risk_level}")
            raise ValueError(f"Invalid risk level: {risk_level}. Must be one of {valid_risk_levels}")
        
        # Check cache if enabled and not forcing refresh
        if self.cache_enabled and not force_refresh:
            cached_data = self._get_cached_recommendations(strategy, risk_level)
            if cached_data:
                logger.info(f"Using cached recommendations for {strategy} strategy")
                return {
                    "recommendations": cached_data["recommendations"][:max_recommendations],
                    "timestamp": cached_data["timestamp"],
                    "source": cached_data["source"],
                    "strategy": strategy,
                    "risk_level": risk_level,
                    "cached": True
                }
        
        try:
            # Get market data from Kalshi, filtered to only include target hourly markets
            markets_data = self._get_filtered_market_data()
            
            if not markets_data:
                logger.warning("No target hourly markets found")
                return {
                    "recommendations": [],
                    "timestamp": time.time(),
                    "source": "none",
                    "strategy": strategy,
                    "risk_level": risk_level,
                    "cached": False,
                    "message": "No target hourly markets found"
                }
            
            # Generate recommendations using the appropriate model or strategy
            recommendations = []
            source = "rule_based"
            
            # For new strategies, use the strategy manager
            if strategy.lower() in ["arbitrage", "volatility", "sentiment", "combined"]:
                try:
                    recommendations = self.strategy_manager.get_recommendations(
                        strategy.lower(),
                        markets_data,
                        max_recommendations,
                        risk_level.lower()
                    )
                    source = strategy.lower()
                except Exception as e:
                    logger.error(f"{strategy.capitalize()} strategy failed: {str(e)}")
                    recommendations = []
            else:
                # For traditional strategies, use the AI models
                if self.openai_enabled and self.use_enhanced_model:
                    try:
                        # Try enhanced OpenAI model first
                        recommendations = self.enhanced_openai_model.generate_recommendations(
                            markets_data,
                            strategy.lower(),
                            max_recommendations,
                            risk_level.lower()
                        )
                        source = "enhanced_openai"
                    except Exception as e:
                        logger.error(f"Enhanced OpenAI model failed: {str(e)}")
                        recommendations = []
                
                # If enhanced model failed or is disabled, try hybrid model
                if not recommendations:
                    try:
                        recommendations = self.hybrid_model.generate_recommendations(
                            markets_data,
                            strategy.lower(),
                            max_recommendations,
                            risk_level.lower()
                        )
                        source = "hybrid"
                    except Exception as e:
                        logger.error(f"Hybrid model failed: {str(e)}")
                        
                        # Fall back to rule-based model
                        recommendations = self.rule_based_model.generate_recommendations(
                            markets_data,
                            strategy.lower(),
                            max_recommendations,
                            risk_level.lower()
                        )
                        source = "rule_based"
            
            # Prepare result
            timestamp = time.time()
            result = {
                "recommendations": recommendations,
                "timestamp": timestamp,
                "source": source,
                "strategy": strategy,
                "risk_level": risk_level,
                "cached": False
            }
            
            # Cache recommendations if enabled
            if self.cache_enabled:
                self._cache_recommendations(strategy, risk_level, result)
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            raise
    
    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available trading strategies.
        
        Returns:
            List of strategy dictionaries
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
            },
            {
                "id": "arbitrage",
                "name": "Arbitrage",
                "description": "Identifies arbitrage opportunities between related markets.",
                "risk_levels": ["low", "medium", "high"]
            },
            {
                "id": "volatility",
                "name": "Volatility-Based",
                "description": "Identifies markets with unusual volatility and recommends trades based on expected price movement.",
                "risk_levels": ["low", "medium", "high"]
            },
            {
                "id": "sentiment",
                "name": "Sentiment-Driven",
                "description": "Uses social feed data to identify markets with strong sentiment signals.",
                "risk_levels": ["low", "medium", "high"]
            },
            {
                "id": "combined",
                "name": "Combined Strategies",
                "description": "Uses all available strategies to generate a diverse set of recommendations.",
                "risk_levels": ["low", "medium", "high"]
            }
        ]
        
        return strategies
    
    def _get_filtered_market_data(self) -> List[Dict[str, Any]]:
        """
        Get market data from Kalshi API, filtered to only include target hourly markets.
        
        Returns:
            List of filtered market data dictionaries
        """
        try:
            # Get active markets
            markets_response = self.kalshi_client.get_markets(status="active", limit=100)
            
            if "markets" not in markets_response:
                logger.error("Invalid response from Kalshi API")
                raise ValueError("Invalid response from Kalshi API")
            
            markets = markets_response["markets"]
            
            # Filter to only include target hourly markets
            filtered_markets = self.market_filter.get_current_hourly_markets(markets)
            
            if not filtered_markets:
                logger.warning("No target hourly markets found in active markets")
                return []
            
            # Enrich market data with additional information
            enriched_markets = []
            for market in filtered_markets:
                # Get market details
                market_details = self.kalshi_client.get_market(market["id"])
                
                # Add to enriched markets
                enriched_markets.append({
                    "id": market["id"],
                    "ticker": market.get("ticker", ""),
                    "title": market.get("title", ""),
                    "subtitle": market.get("subtitle", ""),
                    "yes_bid": market.get("yes_bid", 0),
                    "yes_ask": market.get("yes_ask", 0),
                    "no_bid": market.get("no_bid", 0),
                    "no_ask": market.get("no_ask", 0),
                    "last_price": market.get("last_price", 0),
                    "close_time": market.get("close_time", ""),
                    "volume_24h": market.get("volume_24h", 0),
                    "details": market_details
                })
            
            logger.info(f"Retrieved data for {len(enriched_markets)} filtered hourly markets")
            return enriched_markets
        
        except Exception as e:
            logger.error(f"Failed to get filtered market data: {str(e)}")
            raise
    
    def _get_cached_recommendations(
        self, 
        strategy: str, 
        risk_level: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached recommendations if available and not expired.
        
        Args:
            strategy: Strategy used for recommendations
            risk_level: Risk level used for recommendations
            
        Returns:
            Dictionary with recommendations and metadata or None if not available
        """
        cache_file = self.cache_dir / "recommendations" / f"{strategy}_{risk_level}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            if time.time() - cache_data.get("timestamp", 0) > self.cache_ttl:
                logger.info(f"Cache expired for {strategy} strategy")
                return None
            
            return cache_data
            
        except Exception as e:
            logger.warning(f"Failed to read cache: {str(e)}")
            return None
    
    def _cache_recommendations(
        self, 
        strategy: str, 
        risk_level: str, 
        data: Dict[str, Any]
    ) -> None:
        """
        Cache recommendations for future use.
        
        Args:
            strategy: Strategy used for recommendations
            risk_level: Risk level used for recommendations
            data: Dictionary with recommendations and metadata
        """
        cache_file = self.cache_dir / "recommendations" / f"{strategy}_{risk_level}.json"
        
        try:
            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Cached recommendations for {strategy} strategy")
            
        except Exception as e:
            logger.warning(f"Failed to cache recommendations: {str(e)}")
