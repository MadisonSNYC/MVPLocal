"""
Additional trading strategies for Kalshi markets.

This module implements additional trading strategies beyond the basic
Momentum and Mean-Reversion approaches, including:
1. Arbitrage Detection
2. Volatility-Based Trading
3. Sentiment-Driven Strategies
"""

import logging
import math
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from app.market_filter import HourlyMarketFilter
from app.social_feed import KalshiSocialFeed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("trading_strategies")

class ArbitrageStrategy:
    """
    Arbitrage detection strategy for Kalshi markets.
    
    This strategy identifies arbitrage opportunities between related markets,
    such as different strike prices for the same underlying asset.
    """
    
    def __init__(self, market_filter: HourlyMarketFilter):
        """
        Initialize the arbitrage strategy.
        
        Args:
            market_filter: Market filter instance
        """
        self.market_filter = market_filter
        logger.info("Initialized arbitrage strategy")
    
    def analyze(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze markets to identify arbitrage opportunities.
        
        Args:
            markets: List of market data dictionaries
            
        Returns:
            List of recommendation dictionaries
        """
        if not markets:
            return []
        
        recommendations = []
        
        # Group markets by series
        series_markets = {}
        for market in markets:
            market_id = market.get("id", "")
            
            # Extract market series
            for series in self.market_filter.TARGET_SERIES:
                if series in market_id:
                    if series not in series_markets:
                        series_markets[series] = []
                    
                    series_markets[series].append(market)
                    break
        
        # Analyze each series for arbitrage opportunities
        for series, markets_list in series_markets.items():
            # Skip series with fewer than 2 markets
            if len(markets_list) < 2:
                continue
            
            # For price range markets (KXETH, KXBTC)
            if series in ["KXETH", "KXBTC"]:
                arb_opportunities = self._analyze_price_range_arbitrage(markets_list)
                recommendations.extend(arb_opportunities)
            
            # For index markets (KXNASDAQ100U, KXINXU)
            elif series in ["KXNASDAQ100U", "KXINXU"]:
                arb_opportunities = self._analyze_index_arbitrage(markets_list)
                recommendations.extend(arb_opportunities)
        
        logger.info(f"Found {len(recommendations)} arbitrage opportunities")
        return recommendations
    
    def _analyze_price_range_arbitrage(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze price range markets for arbitrage opportunities.
        
        Args:
            markets: List of market data dictionaries for a single series
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Sort markets by strike price
        sorted_markets = sorted(markets, key=lambda m: self._extract_strike_price(m.get("id", "")))
        
        # Check for arbitrage opportunities between adjacent strike prices
        for i in range(len(sorted_markets) - 1):
            market1 = sorted_markets[i]
            market2 = sorted_markets[i + 1]
            
            # Get market prices
            market1_yes_price = market1.get("yes_ask", 0)
            market2_no_price = market2.get("no_ask", 0)
            
            # Check if there's an arbitrage opportunity
            # If YES price of lower strike + NO price of higher strike < 100, there's an opportunity
            if market1_yes_price > 0 and market2_no_price > 0 and market1_yes_price + market2_no_price < 95:
                arb_profit = 100 - (market1_yes_price + market2_no_price)
                
                # Create recommendations
                recommendations.append({
                    "market_id": market1.get("id", ""),
                    "market": market1.get("title", ""),
                    "action": "YES",
                    "contracts": 1,
                    "probability": market1_yes_price,
                    "cost": market1_yes_price / 100,
                    "confidence": "High" if arb_profit > 10 else "Medium",
                    "rationale": f"Arbitrage opportunity: Buy YES at {market1_yes_price}¢ and NO at {market2_no_price}¢ for a theoretical profit of {arb_profit:.1f}¢ per contract pair.",
                    "strategy": "arbitrage",
                    "target_exit": market1_yes_price + 5,
                    "stop_loss": market1_yes_price - 5
                })
                
                recommendations.append({
                    "market_id": market2.get("id", ""),
                    "market": market2.get("title", ""),
                    "action": "NO",
                    "contracts": 1,
                    "probability": 100 - market2_no_price,
                    "cost": market2_no_price / 100,
                    "confidence": "High" if arb_profit > 10 else "Medium",
                    "rationale": f"Arbitrage opportunity: Buy YES at {market1_yes_price}¢ and NO at {market2_no_price}¢ for a theoretical profit of {arb_profit:.1f}¢ per contract pair.",
                    "strategy": "arbitrage",
                    "target_exit": market2_no_price - 5,
                    "stop_loss": market2_no_price + 5
                })
        
        return recommendations
    
    def _analyze_index_arbitrage(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze index markets for arbitrage opportunities.
        
        Args:
            markets: List of market data dictionaries for a single series
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Sort markets by strike price
        sorted_markets = sorted(markets, key=lambda m: self._extract_strike_price(m.get("id", "")))
        
        # Check for mispricing between adjacent markets
        for i in range(len(sorted_markets) - 1):
            market1 = sorted_markets[i]
            market2 = sorted_markets[i + 1]
            
            # Get market prices
            market1_yes_price = market1.get("yes_ask", 0)
            market2_yes_price = market2.get("yes_ask", 0)
            
            # Check for significant price discrepancy
            if market1_yes_price > 0 and market2_yes_price > 0:
                # Lower strike should have higher YES price than higher strike
                if market1_yes_price < market2_yes_price - 5:
                    # Mispricing detected - buy lower strike YES, sell higher strike YES
                    recommendations.append({
                        "market_id": market1.get("id", ""),
                        "market": market1.get("title", ""),
                        "action": "YES",
                        "contracts": 1,
                        "probability": market1_yes_price,
                        "cost": market1_yes_price / 100,
                        "confidence": "Medium",
                        "rationale": f"Relative value opportunity: YES price of {market1_yes_price}¢ is significantly lower than the YES price of {market2_yes_price}¢ for a higher strike.",
                        "strategy": "arbitrage",
                        "target_exit": market1_yes_price + 10,
                        "stop_loss": market1_yes_price - 5
                    })
                    
                    recommendations.append({
                        "market_id": market2.get("id", ""),
                        "market": market2.get("title", ""),
                        "action": "NO",
                        "contracts": 1,
                        "probability": 100 - market2_yes_price,
                        "cost": (100 - market2_yes_price) / 100,
                        "confidence": "Medium",
                        "rationale": f"Relative value opportunity: YES price of {market2_yes_price}¢ is significantly higher than the YES price of {market1_yes_price}¢ for a lower strike.",
                        "strategy": "arbitrage",
                        "target_exit": market2_yes_price - 10,
                        "stop_loss": market2_yes_price + 5
                    })
        
        return recommendations
    
    def _extract_strike_price(self, market_id: str) -> float:
        """
        Extract the strike price from a market ID.
        
        Args:
            market_id: Market ID
            
        Returns:
            Strike price as a float
        """
        try:
            # Extract the part after the last hyphen
            parts = market_id.split("-")
            if len(parts) < 3:
                return 0.0
            
            strike_part = parts[-1]
            
            # Handle different formats
            if strike_part.startswith("T"):
                # Format: T19529.99
                return float(strike_part[1:])
            elif strike_part.startswith("B"):
                # Format: B1920
                return float(strike_part[1:])
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Failed to extract strike price from {market_id}: {str(e)}")
            return 0.0


class VolatilityStrategy:
    """
    Volatility-based trading strategy for Kalshi markets.
    
    This strategy identifies markets with unusual volatility and
    recommends trades based on expected mean reversion or trend continuation.
    """
    
    def __init__(self, market_filter: HourlyMarketFilter):
        """
        Initialize the volatility strategy.
        
        Args:
            market_filter: Market filter instance
        """
        self.market_filter = market_filter
        logger.info("Initialized volatility strategy")
    
    def analyze(self, markets: List[Dict[str, Any]], historical_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Analyze markets to identify volatility-based trading opportunities.
        
        Args:
            markets: List of market data dictionaries
            historical_data: Optional historical data for volatility calculation
            
        Returns:
            List of recommendation dictionaries
        """
        if not markets:
            return []
        
        recommendations = []
        
        # Use historical data if provided, otherwise use current market data
        if not historical_data:
            historical_data = self._generate_simulated_historical_data(markets)
        
        # Analyze each market for volatility
        for market in markets:
            market_id = market.get("id", "")
            
            # Skip markets without historical data
            if market_id not in historical_data:
                continue
            
            # Calculate volatility metrics
            volatility_data = self._calculate_volatility(market, historical_data[market_id])
            
            # Check for high volatility
            if volatility_data["is_high_volatility"]:
                # Determine if we expect mean reversion or trend continuation
                if volatility_data["expect_reversion"]:
                    # Mean reversion strategy
                    if volatility_data["current_price"] > volatility_data["mean_price"] + volatility_data["std_dev"]:
                        # Price is high, expect reversion down
                        recommendations.append({
                            "market_id": market_id,
                            "market": market.get("title", ""),
                            "action": "NO",
                            "contracts": 1,
                            "probability": 100 - market.get("yes_bid", 50),
                            "cost": market.get("no_ask", 50) / 100,
                            "confidence": "Medium",
                            "rationale": f"High volatility with price significantly above average ({volatility_data['current_price']}¢ vs {volatility_data['mean_price']:.1f}¢). Expecting mean reversion.",
                            "strategy": "volatility",
                            "target_exit": volatility_data["mean_price"],
                            "stop_loss": volatility_data["current_price"] + 10
                        })
                    elif volatility_data["current_price"] < volatility_data["mean_price"] - volatility_data["std_dev"]:
                        # Price is low, expect reversion up
                        recommendations.append({
                            "market_id": market_id,
                            "market": market.get("title", ""),
                            "action": "YES",
                            "contracts": 1,
                            "probability": market.get("yes_ask", 50),
                            "cost": market.get("yes_ask", 50) / 100,
                            "confidence": "Medium",
                            "rationale": f"High volatility with price significantly below average ({volatility_data['current_price']}¢ vs {volatility_data['mean_price']:.1f}¢). Expecting mean reversion.",
                            "strategy": "volatility",
                            "target_exit": volatility_data["mean_price"],
                            "stop_loss": volatility_data["current_price"] - 10
                        })
                else:
                    # Trend continuation strategy
                    if volatility_data["is_uptrend"]:
                        # Uptrend, expect continuation
                        recommendations.append({
                            "market_id": market_id,
                            "market": market.get("title", ""),
                            "action": "YES",
                            "contracts": 1,
                            "probability": market.get("yes_ask", 50),
                            "cost": market.get("yes_ask", 50) / 100,
                            "confidence": "Medium",
                            "rationale": f"High volatility with strong uptrend. Momentum suggests continued price increase.",
                            "strategy": "volatility",
                            "target_exit": volatility_data["current_price"] + 10,
                            "stop_loss": volatility_data["current_price"] - 5
                        })
                    else:
                        # Downtrend, expect continuation
                        recommendations.append({
                            "market_id": market_id,
                            "market": market.get("title", ""),
                            "action": "NO",
                            "contracts": 1,
                            "probability": 100 - market.get("yes_bid", 50),
                            "cost": market.get("no_ask", 50) / 100,
                            "confidence": "Medium",
                            "rationale": f"High volatility with strong downtrend. Momentum suggests continued price decrease.",
                            "strategy": "volatility",
                            "target_exit": volatility_data["current_price"] - 10,
                            "stop_loss": volatility_data["current_price"] + 5
                        })
        
        logger.info(f"Found {len(recommendations)} volatility-based opportunities")
        return recommendations
    
    def _calculate_volatility(self, market: Dict[str, Any], historical_prices: List[float]) -> Dict[str, Any]:
        """
        Calculate volatility metrics for a market.
        
        Args:
            market: Market data dictionary
            historical_prices: List of historical prices
            
        Returns:
            Dictionary with volatility metrics
        """
        current_price = market.get("yes_bid", 50)
        
        # Calculate basic statistics
        mean_price = statistics.mean(historical_prices)
        std_dev = statistics.stdev(historical_prices) if len(historical_prices) > 1 else 5.0
        
        # Calculate recent trend
        recent_prices = historical_prices[-5:] if len(historical_prices) >= 5 else historical_prices
        is_uptrend = all(recent_prices[i] <= recent_prices[i+1] for i in range(len(recent_prices)-1))
        is_downtrend = all(recent_prices[i] >= recent_prices[i+1] for i in range(len(recent_prices)-1))
        
        # Calculate volatility ratio (current std_dev vs historical)
        volatility_ratio = std_dev / 5.0  # Compare to baseline volatility of 5
        is_high_volatility = volatility_ratio > 1.5
        
        # Determine if we expect mean reversion or trend continuation
        # If price is far from mean, expect reversion
        # If price is in strong trend, expect continuation
        price_deviation = abs(current_price - mean_price) / std_dev
        expect_reversion = price_deviation > 1.5 and not (is_uptrend or is_downtrend)
        
        return {
            "current_price": current_price,
            "mean_price": mean_price,
            "std_dev": std_dev,
            "is_uptrend": is_uptrend,
            "is_downtrend": is_downtrend,
            "volatility_ratio": volatility_ratio,
            "is_high_volatility": is_high_volatility,
            "price_deviation": price_deviation,
            "expect_reversion": expect_reversion
        }
    
    def _generate_simulated_historical_data(self, markets: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """
        Generate simulated historical data for testing.
        
        Args:
            markets: List of market data dictionaries
            
        Returns:
            Dictionary mapping market IDs to lists of historical prices
        """
        historical_data = {}
        
        for market in markets:
            market_id = market.get("id", "")
            current_price = market.get("yes_bid", 50)
            
            # Generate 10 historical prices with some randomness
            historical_prices = []
            base_price = current_price
            
            for i in range(10):
                # Add some random variation
                random_factor = (i % 3 - 1) * 5  # -5, 0, or 5
                price = max(5, min(95, base_price + random_factor))
                historical_prices.append(price)
                
                # Adjust base price for next iteration
                base_price = price
            
            historical_data[market_id] = historical_prices
        
        return historical_data


class SentimentStrategy:
    """
    Sentiment-driven trading strategy for Kalshi markets.
    
    This strategy uses insights from the Kalshi social activity feed
    to identify markets with strong sentiment signals.
    """
    
    def __init__(self, market_filter: HourlyMarketFilter, social_feed: KalshiSocialFeed):
        """
        Initialize the sentiment strategy.
        
        Args:
            market_filter: Market filter instance
            social_feed: Social feed instance
        """
        self.market_filter = market_filter
        self.social_feed = social_feed
        logger.info("Initialized sentiment strategy")
    
    def analyze(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze markets to identify sentiment-driven trading opportunities.
        
        Args:
            markets: List of market data dictionaries
            
        Returns:
            List of recommendation dictionaries
        """
        if not markets:
            return []
        
        recommendations = []
        
        # Get social feed data
        feed_data = self.social_feed.get_social_feed()
        
        if feed_data.get("status") == "error" or not feed_data.get("insights"):
            logger.warning("Failed to get social feed data for sentiment analysis")
            return []
        
        # Get series sentiment data
        series_sentiment = feed_data.get("insights", {}).get("series_sentiment", {})
        
        # Analyze each market for sentiment signals
        for market in markets:
            market_id = market.get("id", "")
            
            # Extract market series
            market_series = None
            for series in self.market_filter.TARGET_SERIES:
                if series in market_id:
                    market_series = series
                    break
            
            if not market_series or market_series not in series_sentiment:
                continue
            
            # Get sentiment data for this series
            sentiment_data = series_sentiment[market_series]
            
            # Check for strong sentiment signals
            if sentiment_data["confidence"] != "low":
                if sentiment_data["sentiment"] in ["bullish", "slightly_bullish"] and sentiment_data["buy_percentage"] >= 60:
                    # Bullish sentiment
                    recommendations.append({
                        "market_id": market_id,
                        "market": market.get("title", ""),
                        "action": "YES",
                        "contracts": 1,
                        "probability": market.get("yes_ask", 50),
                        "cost": market.get("yes_ask", 50) / 100,
                        "confidence": "High" if sentiment_data["confidence"] == "high" else "Medium",
                        "rationale": f"Strong bullish sentiment ({sentiment_data['buy_percentage']:.1f}% buy) with {sentiment_data['activity_level']} activity level.",
                        "strategy": "sentiment",
                        "target_exit": market.get("yes_ask", 50) + 10,
                        "stop_loss": market.get("yes_ask", 50) - 5
                    })
                elif sentiment_data["sentiment"] in ["bearish", "slightly_bearish"] and sentiment_data["sell_percentage"] >= 60:
                    # Bearish sentiment
                    recommendations.append({
                        "market_id": market_id,
                        "market": market.get("title", ""),
                        "action": "NO",
                        "contracts": 1,
                        "probability": 100 - market.get("yes_bid", 50),
                        "cost": market.get("no_ask", 50) / 100,
                        "confidence": "High" if sentiment_data["confidence"] == "high" else "Medium",
                        "rationale": f"Strong bearish sentiment ({sentiment_data['sell_percentage']:.1f}% sell) with {sentiment_data['activity_level']} activity level.",
                        "strategy": "sentiment",
                        "target_exit": market.get("no_ask", 50) + 10,
                        "stop_loss": market.get("no_ask", 50) - 5
                    })
        
        logger.info(f"Found {len(recommendations)} sentiment-driven opportunities")
        return recommendations
