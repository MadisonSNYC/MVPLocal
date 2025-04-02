"""
Market filter for specific hourly Kalshi markets.

This module implements filtering logic to focus on specific hourly markets
as requested by the user.
"""

import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("market_filter")

class HourlyMarketFilter:
    """
    Filter for specific hourly Kalshi markets.
    
    This class implements filtering logic to focus on specific hourly markets
    for the Nasdaq, S&P 500, Ethereum, and Bitcoin.
    """
    
    # Target market series
    TARGET_SERIES = [
        "KXNASDAQ100U",  # Nasdaq (Hourly)
        "KXINXU",        # S&P 500 (Hourly)
        "KXETHD",        # Ethereum Price (Hourly)
        "KXETH",         # Ethereum Price Range (Hourly)
        "KXBTCD",        # Bitcoin Price (Hourly)
        "KXBTC"          # Bitcoin Price Range (Hourly)
    ]
    
    def __init__(self):
        """Initialize the hourly market filter."""
        logger.info("Initialized hourly market filter for specific markets")
    
    def filter_markets(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter markets to include only the specified hourly markets.
        
        Args:
            markets: List of market data dictionaries
            
        Returns:
            Filtered list of market data dictionaries
        """
        if not markets:
            return []
        
        filtered_markets = []
        
        for market in markets:
            # Check if market belongs to one of the target series
            ticker = market.get("ticker", "")
            if not any(ticker.startswith(series) for series in self.TARGET_SERIES):
                continue
            
            # Check if it's an hourly market (contains H in the event ticker for index markets
            # or contains the hour number for crypto markets)
            event_ticker = market.get("event_ticker", "")
            
            # For Nasdaq and S&P 500 (contain H in event ticker)
            is_hourly_index = any(
                series in event_ticker and "H" in event_ticker 
                for series in ["KXNASDAQ100U", "KXINXU"]
            )
            
            # For crypto markets (contain hour number in event ticker)
            is_hourly_crypto = any(
                series in event_ticker and re.search(r"\d{2}$", event_ticker)
                for series in ["KXETHD", "KXETH", "KXBTCD", "KXBTC"]
            )
            
            if is_hourly_index or is_hourly_crypto:
                filtered_markets.append(market)
        
        logger.info(f"Filtered {len(filtered_markets)} hourly markets from {len(markets)} total markets")
        return filtered_markets
    
    def get_current_hourly_markets(self, all_markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get the current hour's markets for the specified series.
        
        Args:
            all_markets: List of all market data dictionaries
            
        Returns:
            List of current hourly market data dictionaries
        """
        # First filter to only include target series
        target_markets = self.filter_markets(all_markets)
        
        if not target_markets:
            return []
        
        # Get current date and hour
        now = datetime.now()
        current_date = now.strftime("%y%b%d").upper()  # Format: 25APR02
        current_hour = now.hour
        
        # For index markets, format is like KXNASDAQ100U-25APR02H1200
        # For crypto markets, format is like KXETHD-25APR0212
        
        current_markets = []
        
        for market in target_markets:
            event_ticker = market.get("event_ticker", "")
            
            # Check if the market is for the current date
            if current_date not in event_ticker:
                continue
            
            # For index markets, check if it's the current hour or next hour
            if "KXNASDAQ100U" in event_ticker or "KXINXU" in event_ticker:
                hour_match = re.search(r"H(\d{2})00", event_ticker)
                if hour_match:
                    market_hour = int(hour_match.group(1))
                    if market_hour == current_hour or market_hour == (current_hour + 1) % 24:
                        current_markets.append(market)
            
            # For crypto markets, check if it's the current hour or next hour
            elif "KXETHD" in event_ticker or "KXETH" in event_ticker or "KXBTCD" in event_ticker or "KXBTC" in event_ticker:
                hour_match = re.search(r"(\d{2})$", event_ticker)
                if hour_match:
                    market_hour = int(hour_match.group(1))
                    if market_hour == current_hour or market_hour == (current_hour + 1) % 24:
                        current_markets.append(market)
        
        logger.info(f"Found {len(current_markets)} current hourly markets for date {current_date}, hour {current_hour}")
        return current_markets
    
    def is_target_market(self, market_id: str) -> bool:
        """
        Check if a market ID belongs to one of the target hourly markets.
        
        Args:
            market_id: Market ID to check
            
        Returns:
            True if the market is a target hourly market, False otherwise
        """
        if not market_id:
            return False
        
        # Check if market belongs to one of the target series
        return any(series in market_id for series in self.TARGET_SERIES)
