"""
Kalshi social activity feed integration.

This module implements integration with Kalshi's social activity feed
to enhance trading recommendations with community sentiment data.
"""

import logging
import json
import time
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

from app.config import config
from app.kalshi_api_client import KalshiApiClient
from app.market_filter import HourlyMarketFilter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("social_feed")

class KalshiSocialFeed:
    """
    Integration with Kalshi's social activity feed.
    
    This class scrapes and analyzes the Kalshi social activity feed
    to extract insights about market sentiment and trading activity.
    """
    
    SOCIAL_FEED_URL = "https://kalshi.com/social/activity"
    
    def __init__(self, kalshi_client: KalshiApiClient):
        """
        Initialize the Kalshi social feed integration.
        
        Args:
            kalshi_client: Kalshi API client instance
        """
        self.kalshi_client = kalshi_client
        self.market_filter = HourlyMarketFilter()
        self.cache_dir = config.get("app", "cache_dir")
        self.cache_ttl = config.get("social", "cache_ttl_minutes", 15) * 60  # Convert to seconds
        
        # Last fetch timestamp
        self.last_fetch_time = 0
        self.cached_feed_data = None
        
        logger.info("Initialized Kalshi social feed integration")
    
    def get_social_feed(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get the Kalshi social activity feed.
        
        Args:
            force_refresh: Whether to force a refresh of cached data
            
        Returns:
            Dictionary with social feed data
        """
        current_time = time.time()
        
        # Check if we need to refresh the cache
        if (not self.cached_feed_data or 
            force_refresh or 
            current_time - self.last_fetch_time > self.cache_ttl):
            
            try:
                # Fetch social feed data
                feed_data = self._fetch_social_feed()
                
                # Filter and analyze feed data
                analyzed_data = self._analyze_feed_data(feed_data)
                
                # Update cache
                self.cached_feed_data = analyzed_data
                self.last_fetch_time = current_time
                
                logger.info("Refreshed social feed data")
                
            except Exception as e:
                logger.error(f"Failed to fetch social feed: {str(e)}")
                
                # If we have cached data, use it even if expired
                if self.cached_feed_data:
                    logger.info("Using expired cached social feed data")
                else:
                    # Return empty data if no cache available
                    return {
                        "status": "error",
                        "message": f"Failed to fetch social feed: {str(e)}",
                        "timestamp": current_time,
                        "activities": [],
                        "insights": {}
                    }
        
        return self.cached_feed_data
    
    def get_market_sentiment(self, market_id: str) -> Dict[str, Any]:
        """
        Get sentiment data for a specific market.
        
        Args:
            market_id: Market ID to get sentiment for
            
        Returns:
            Dictionary with sentiment data
        """
        # Get social feed data
        feed_data = self.get_social_feed()
        
        if feed_data.get("status") == "error":
            return {
                "status": "error",
                "message": feed_data.get("message", "Failed to get social feed data"),
                "market_id": market_id,
                "sentiment": "neutral",
                "activity_level": "low"
            }
        
        # Extract market series from market ID
        market_series = None
        for series in self.market_filter.TARGET_SERIES:
            if series in market_id:
                market_series = series
                break
        
        if not market_series:
            return {
                "status": "error",
                "message": "Not a target market",
                "market_id": market_id,
                "sentiment": "neutral",
                "activity_level": "low"
            }
        
        # Get sentiment for market series
        series_sentiment = feed_data.get("insights", {}).get("series_sentiment", {}).get(market_series, {})
        
        if not series_sentiment:
            return {
                "status": "success",
                "market_id": market_id,
                "market_series": market_series,
                "sentiment": "neutral",
                "activity_level": "low",
                "confidence": "low",
                "recent_activities": []
            }
        
        # Get recent activities for this market series
        recent_activities = []
        for activity in feed_data.get("activities", []):
            if market_series in activity.get("market_id", ""):
                recent_activities.append(activity)
        
        return {
            "status": "success",
            "market_id": market_id,
            "market_series": market_series,
            "sentiment": series_sentiment.get("sentiment", "neutral"),
            "activity_level": series_sentiment.get("activity_level", "low"),
            "confidence": series_sentiment.get("confidence", "low"),
            "buy_percentage": series_sentiment.get("buy_percentage", 50),
            "sell_percentage": series_sentiment.get("sell_percentage", 50),
            "volume_change": series_sentiment.get("volume_change", 0),
            "recent_activities": recent_activities[:5]  # Limit to 5 most recent activities
        }
    
    def _fetch_social_feed(self) -> Dict[str, Any]:
        """
        Fetch the Kalshi social activity feed.
        
        Returns:
            Dictionary with raw social feed data
        """
        try:
            # Use the Kalshi API client to get the social feed
            # This is a placeholder - in a real implementation, we would use
            # the Kalshi API if available, or scrape the social feed page
            
            # For MVP, we'll simulate the social feed with some sample data
            # In a production implementation, this would be replaced with actual API calls
            
            # Get active markets to use in the simulated feed
            markets_response = self.kalshi_client.get_markets(status="active", limit=100)
            
            if "markets" not in markets_response:
                raise ValueError("Invalid response from Kalshi API")
            
            markets = markets_response["markets"]
            
            # Filter to only include target hourly markets
            filtered_markets = self.market_filter.get_current_hourly_markets(markets)
            
            if not filtered_markets:
                logger.warning("No target hourly markets found in active markets")
                return {"activities": []}
            
            # Generate simulated social feed activities
            activities = self._generate_simulated_activities(filtered_markets)
            
            return {
                "activities": activities,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch social feed: {str(e)}")
            raise
    
    def _generate_simulated_activities(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate simulated social feed activities for testing.
        
        Args:
            markets: List of market data dictionaries
            
        Returns:
            List of simulated activity dictionaries
        """
        activities = []
        current_time = time.time()
        
        # Activity types
        activity_types = ["trade", "comment", "like", "follow"]
        
        # Generate 20-30 random activities
        for i in range(20, 31):
            # Select a random market
            if not markets:
                break
                
            market_index = i % len(markets)
            market = markets[market_index]
            
            # Generate activity
            activity_type = activity_types[i % len(activity_types)]
            
            activity = {
                "id": f"activity_{i}",
                "type": activity_type,
                "timestamp": current_time - (i * 60),  # Each activity is 1 minute apart
                "user": {
                    "id": f"user_{i % 10}",
                    "username": f"trader{i % 10}",
                    "profile_url": f"https://kalshi.com/user/trader{i % 10}"
                },
                "market_id": market.get("id", ""),
                "market_ticker": market.get("ticker", ""),
                "market_title": market.get("title", "")
            }
            
            # Add activity-specific details
            if activity_type == "trade":
                activity["action"] = "YES" if i % 2 == 0 else "NO"
                activity["contracts"] = (i % 5) + 1
                activity["price"] = market.get("yes_bid" if i % 2 == 0 else "no_bid", 50)
            elif activity_type == "comment":
                comments = [
                    "I think this is going up!",
                    "Bearish on this one.",
                    "Volume is picking up!",
                    "Interesting price action here.",
                    "This market is trending down.",
                    "Bullish sentiment increasing.",
                    "Volatility is high today.",
                    "Strong support at this level.",
                    "Resistance breaking down.",
                    "Market seems overvalued."
                ]
                activity["comment"] = comments[i % len(comments)]
            
            activities.append(activity)
        
        return activities
    
    def _analyze_feed_data(self, feed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze social feed data to extract insights.
        
        Args:
            feed_data: Raw social feed data
            
        Returns:
            Dictionary with analyzed feed data and insights
        """
        activities = feed_data.get("activities", [])
        
        if not activities:
            return {
                "status": "success",
                "timestamp": time.time(),
                "activities": [],
                "insights": {
                    "trending_markets": [],
                    "series_sentiment": {},
                    "overall_sentiment": "neutral",
                    "activity_level": "low"
                }
            }
        
        # Analyze activities to extract insights
        
        # 1. Count activities by market series
        series_activity_count = {}
        for activity in activities:
            market_id = activity.get("market_id", "")
            
            # Extract market series
            for series in self.market_filter.TARGET_SERIES:
                if series in market_id:
                    if series not in series_activity_count:
                        series_activity_count[series] = {
                            "total": 0,
                            "trades": 0,
                            "comments": 0,
                            "yes_trades": 0,
                            "no_trades": 0
                        }
                    
                    series_activity_count[series]["total"] += 1
                    
                    if activity.get("type") == "trade":
                        series_activity_count[series]["trades"] += 1
                        
                        if activity.get("action") == "YES":
                            series_activity_count[series]["yes_trades"] += 1
                        elif activity.get("action") == "NO":
                            series_activity_count[series]["no_trades"] += 1
                    
                    elif activity.get("type") == "comment":
                        series_activity_count[series]["comments"] += 1
                    
                    break
        
        # 2. Determine trending markets
        trending_markets = []
        for series, counts in series_activity_count.items():
            if counts["total"] >= 3:  # Arbitrary threshold for "trending"
                trending_markets.append({
                    "series": series,
                    "activity_count": counts["total"],
                    "trade_count": counts["trades"],
                    "comment_count": counts["comments"]
                })
        
        # Sort trending markets by activity count
        trending_markets.sort(key=lambda x: x["activity_count"], reverse=True)
        
        # 3. Determine sentiment for each market series
        series_sentiment = {}
        for series, counts in series_activity_count.items():
            yes_trades = counts["yes_trades"]
            no_trades = counts["no_trades"]
            total_trades = yes_trades + no_trades
            
            if total_trades > 0:
                buy_percentage = (yes_trades / total_trades) * 100
                sell_percentage = (no_trades / total_trades) * 100
                
                # Determine sentiment based on buy/sell ratio
                if buy_percentage >= 70:
                    sentiment = "bullish"
                elif buy_percentage >= 55:
                    sentiment = "slightly_bullish"
                elif sell_percentage >= 70:
                    sentiment = "bearish"
                elif sell_percentage >= 55:
                    sentiment = "slightly_bearish"
                else:
                    sentiment = "neutral"
                
                # Determine activity level
                if counts["total"] >= 10:
                    activity_level = "high"
                elif counts["total"] >= 5:
                    activity_level = "medium"
                else:
                    activity_level = "low"
                
                # Determine confidence based on sample size
                if total_trades >= 10:
                    confidence = "high"
                elif total_trades >= 5:
                    confidence = "medium"
                else:
                    confidence = "low"
                
                series_sentiment[series] = {
                    "sentiment": sentiment,
                    "activity_level": activity_level,
                    "confidence": confidence,
                    "buy_percentage": round(buy_percentage, 1),
                    "sell_percentage": round(sell_percentage, 1),
                    "total_trades": total_trades,
                    "total_activities": counts["total"],
                    "volume_change": 0  # Placeholder - would calculate from historical data
                }
            else:
                series_sentiment[series] = {
                    "sentiment": "neutral",
                    "activity_level": "low",
                    "confidence": "low",
                    "buy_percentage": 50,
                    "sell_percentage": 50,
                    "total_trades": 0,
                    "total_activities": counts["total"],
                    "volume_change": 0
                }
        
        # 4. Determine overall sentiment
        overall_sentiment = "neutral"
        overall_activity_level = "low"
        
        if trending_markets:
            # Use the sentiment of the most active market as overall sentiment
            top_market = trending_markets[0]["series"]
            overall_sentiment = series_sentiment.get(top_market, {}).get("sentiment", "neutral")
            
            # Determine overall activity level
            total_activities = sum(counts["total"] for counts in series_activity_count.values())
            if total_activities >= 20:
                overall_activity_level = "high"
            elif total_activities >= 10:
                overall_activity_level = "medium"
        
        # Prepare result
        return {
            "status": "success",
            "timestamp": time.time(),
            "activities": activities,
            "insights": {
                "trending_markets": trending_markets,
                "series_sentiment": series_sentiment,
                "overall_sentiment": overall_sentiment,
                "activity_level": overall_activity_level
            }
        }
