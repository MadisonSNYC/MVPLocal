"""
Update to the AI recommendation system to include the new hybrid model.

This module updates the AI recommendation system to use the new hybrid model
and provides additional strategies.
"""

import logging
import json
import os
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from app.config import config
from app.kalshi_api_client import KalshiApiClient
from app.ai_models.hybrid_model import HybridRecommendationModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai_recommendations")

class AIRecommendationSystem:
    """
    AI-powered recommendation system for Kalshi trading.
    Provides trade recommendations based on different strategies.
    """
    
    def __init__(self, kalshi_client: KalshiApiClient):
        """
        Initialize the AI recommendation system.
        
        Args:
            kalshi_client: Kalshi API client instance
        """
        self.kalshi_client = kalshi_client
        self.recommendation_model = HybridRecommendationModel()
        self.cache_enabled = config.get("ai", "cache_recommendations")
        self.cache_ttl = config.get("ai", "cache_ttl_minutes") * 60  # Convert to seconds
        self.cache_dir = Path(config.get("app", "cache_dir"))
        
        # Create cache directory if it doesn't exist
        if self.cache_enabled and not (self.cache_dir / "recommendations").exists():
            (self.cache_dir / "recommendations").mkdir(parents=True, exist_ok=True)
        
        logger.info("Initialized AI recommendation system with hybrid model")
    
    def get_recommendations(
        self, 
        strategy: str, 
        max_recommendations: int = 5,
        risk_level: str = "medium",
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get trade recommendations based on the specified strategy.
        
        Args:
            strategy: Strategy to use ("momentum", "mean-reversion", or "hybrid")
            max_recommendations: Maximum number of recommendations to return
            risk_level: Risk level ("low", "medium", or "high")
            force_refresh: Whether to force a refresh of cached recommendations
            
        Returns:
            List of recommendation dictionaries
        """
        # Validate strategy
        valid_strategies = ["momentum", "mean-reversion", "hybrid"]
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
            cached_recommendations = self._get_cached_recommendations(strategy, risk_level)
            if cached_recommendations:
                logger.info(f"Using cached recommendations for {strategy} strategy")
                return cached_recommendations[:max_recommendations]
        
        try:
            # Get market data from Kalshi
            markets_data = self._get_market_data()
            
            # Generate recommendations using the hybrid model
            recommendations = self.recommendation_model.generate_recommendations(
                markets_data,
                strategy.lower(),
                max_recommendations,
                risk_level.lower()
            )
            
            # Cache recommendations if enabled
            if self.cache_enabled:
                self._cache_recommendations(strategy, risk_level, recommendations)
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            raise
    
    def _get_market_data(self) -> List[Dict[str, Any]]:
        """
        Get market data from Kalshi API.
        
        Returns:
            List of market data dictionaries
        """
        try:
            # Get active markets
            markets_response = self.kalshi_client.get_markets(status="active", limit=100)
            
            if "markets" not in markets_response:
                logger.error("Invalid response from Kalshi API")
                raise ValueError("Invalid response from Kalshi API")
            
            markets = markets_response["markets"]
            
            # Enrich market data with additional information
            enriched_markets = []
            for market in markets:
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
            
            logger.info(f"Retrieved data for {len(enriched_markets)} markets")
            return enriched_markets
        
        except Exception as e:
            logger.error(f"Failed to get market data: {str(e)}")
            raise
    
    def _get_cached_recommendations(
        self, 
        strategy: str, 
        risk_level: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached recommendations if available and not expired.
        
        Args:
            strategy: Strategy used for recommendations
            risk_level: Risk level used for recommendations
            
        Returns:
            List of recommendation dictionaries or None if not available
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
            
            return cache_data.get("recommendations", [])
            
        except Exception as e:
            logger.warning(f"Failed to read cache: {str(e)}")
            return None
    
    def _cache_recommendations(
        self, 
        strategy: str, 
        risk_level: str, 
        recommendations: List[Dict[str, Any]]
    ) -> None:
        """
        Cache recommendations for future use.
        
        Args:
            strategy: Strategy used for recommendations
            risk_level: Risk level used for recommendations
            recommendations: List of recommendation dictionaries
        """
        cache_file = self.cache_dir / "recommendations" / f"{strategy}_{risk_level}.json"
        
        try:
            cache_data = {
                "timestamp": time.time(),
                "strategy": strategy,
                "risk_level": risk_level,
                "recommendations": recommendations
            }
            
            with open(cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Cached recommendations for {strategy} strategy")
            
        except Exception as e:
            logger.warning(f"Failed to cache recommendations: {str(e)}")
