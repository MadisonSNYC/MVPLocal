"""
Integration of additional trading strategies with the AI recommendation system.

This module updates the AI recommendation system to incorporate the new
trading strategies: Arbitrage, Volatility-Based, and Sentiment-Driven.
"""

import logging
from typing import Dict, List, Any, Optional

from app.kalshi_api_client import KalshiApiClient
from app.market_filter import HourlyMarketFilter
from app.social_feed import KalshiSocialFeed
from app.trading_strategies import ArbitrageStrategy, VolatilityStrategy, SentimentStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("strategy_integration")

class StrategyManager:
    """
    Manager for all trading strategies.
    
    This class integrates all available trading strategies and provides
    a unified interface for generating recommendations.
    """
    
    def __init__(self, kalshi_client: KalshiApiClient, social_feed: KalshiSocialFeed):
        """
        Initialize the strategy manager.
        
        Args:
            kalshi_client: Kalshi API client instance
            social_feed: Social feed instance
        """
        self.kalshi_client = kalshi_client
        self.social_feed = social_feed
        self.market_filter = HourlyMarketFilter()
        
        # Initialize strategies
        self.arbitrage_strategy = ArbitrageStrategy(self.market_filter)
        self.volatility_strategy = VolatilityStrategy(self.market_filter)
        self.sentiment_strategy = SentimentStrategy(self.market_filter, self.social_feed)
        
        logger.info("Initialized strategy manager with all trading strategies")
    
    def get_recommendations(
        self, 
        strategy: str, 
        markets: List[Dict[str, Any]], 
        max_recommendations: int = 5,
        risk_level: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations based on the specified strategy.
        
        Args:
            strategy: Strategy to use
            markets: List of market data dictionaries
            max_recommendations: Maximum number of recommendations to return
            risk_level: Risk level ("low", "medium", or "high")
            
        Returns:
            List of recommendation dictionaries
        """
        if not markets:
            return []
        
        recommendations = []
        
        # Apply the requested strategy
        if strategy == "arbitrage":
            recommendations = self.arbitrage_strategy.analyze(markets)
        elif strategy == "volatility":
            recommendations = self.volatility_strategy.analyze(markets)
        elif strategy == "sentiment":
            recommendations = self.sentiment_strategy.analyze(markets)
        elif strategy == "combined":
            # Combined strategy uses all available strategies
            arb_recs = self.arbitrage_strategy.analyze(markets)
            vol_recs = self.volatility_strategy.analyze(markets)
            sent_recs = self.sentiment_strategy.analyze(markets)
            
            recommendations = arb_recs + vol_recs + sent_recs
        else:
            logger.warning(f"Unknown strategy: {strategy}")
            return []
        
        # Filter by risk level
        filtered_recommendations = self._filter_by_risk_level(recommendations, risk_level)
        
        # Sort by confidence and limit to max recommendations
        sorted_recommendations = self._sort_by_confidence(filtered_recommendations)
        limited_recommendations = sorted_recommendations[:max_recommendations]
        
        logger.info(f"Generated {len(limited_recommendations)} recommendations using {strategy} strategy")
        return limited_recommendations
    
    def _filter_by_risk_level(
        self, 
        recommendations: List[Dict[str, Any]], 
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """
        Filter recommendations by risk level.
        
        Args:
            recommendations: List of recommendation dictionaries
            risk_level: Risk level ("low", "medium", or "high")
            
        Returns:
            Filtered list of recommendation dictionaries
        """
        if risk_level == "high":
            # High risk level includes all recommendations
            return recommendations
        elif risk_level == "medium":
            # Medium risk level excludes low confidence recommendations
            return [rec for rec in recommendations if rec.get("confidence", "") != "Low"]
        elif risk_level == "low":
            # Low risk level only includes high confidence recommendations
            return [rec for rec in recommendations if rec.get("confidence", "") == "High"]
        else:
            # Default to medium risk level
            return [rec for rec in recommendations if rec.get("confidence", "") != "Low"]
    
    def _sort_by_confidence(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort recommendations by confidence level.
        
        Args:
            recommendations: List of recommendation dictionaries
            
        Returns:
            Sorted list of recommendation dictionaries
        """
        confidence_order = {"High": 3, "Medium": 2, "Low": 1}
        
        return sorted(
            recommendations,
            key=lambda x: (
                confidence_order.get(x.get("confidence", ""), 0),
                x.get("cost", 0) * -1  # Secondary sort by cost (descending)
            ),
            reverse=True
        )
