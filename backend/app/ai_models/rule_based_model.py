"""
Rule-based model for Kalshi trade recommendations.

This module provides functions to generate trade recommendations using rule-based strategies.
"""

import logging
from typing import Dict, List, Any, Optional
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("rule_based_model")

class RuleBasedRecommendationModel:
    """
    Rule-based recommendation model for Kalshi trading.
    Implements momentum and mean-reversion strategies without requiring external API calls.
    """
    
    def __init__(self):
        """Initialize the rule-based recommendation model."""
        logger.info("Initialized rule-based recommendation model")
    
    def generate_recommendations(
        self, 
        markets_data: List[Dict[str, Any]], 
        strategy: str,
        max_recommendations: int = 5,
        risk_level: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Generate trade recommendations using rule-based strategies.
        
        Args:
            markets_data: List of market data dictionaries
            strategy: Strategy to use ("momentum" or "mean-reversion")
            max_recommendations: Maximum number of recommendations to return
            risk_level: Risk level ("low", "medium", or "high")
            
        Returns:
            List of recommendation dictionaries
        """
        if strategy == "momentum":
            return self._generate_momentum_recommendations(markets_data, max_recommendations, risk_level)
        elif strategy == "mean-reversion":
            return self._generate_mean_reversion_recommendations(markets_data, max_recommendations, risk_level)
        else:
            logger.error(f"Unknown strategy: {strategy}")
            return []
    
    def _generate_momentum_recommendations(
        self, 
        markets: List[Dict[str, Any]], 
        max_recommendations: int,
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on momentum strategy.
        
        Args:
            markets: List of market data dictionaries
            max_recommendations: Maximum number of recommendations to return
            risk_level: Risk level ("low", "medium", or "high")
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Sort markets by volume (high volume indicates momentum)
        sorted_markets = sorted(markets, key=lambda x: x.get("volume_24h", 0), reverse=True)
        
        for market in sorted_markets[:max_recommendations * 2]:  # Get more than needed to filter
            yes_price = market.get("yes_ask", 0) / 100.0  # Convert to decimal
            
            # For momentum strategy, we look for markets with strong trends
            # If yes_price > 0.65, it suggests market believes "yes" outcome is likely
            if yes_price > 0.65:
                action = "YES"
                probability = yes_price * 100
                confidence = "High" if yes_price > 0.8 else "Medium"
            # If yes_price < 0.35, it suggests market believes "no" outcome is likely
            elif yes_price < 0.35:
                action = "NO"
                probability = (1 - yes_price) * 100
                confidence = "High" if yes_price < 0.2 else "Medium"
            else:
                # Skip markets without clear momentum
                continue
            
            # Adjust position size based on risk level
            if risk_level == "low":
                contracts = 1
            elif risk_level == "medium":
                contracts = 3
            else:  # high
                contracts = 5
            
            # Calculate cost
            if action == "YES":
                cost = contracts * yes_price
                target_exit = min(yes_price + 0.15, 0.99)
                stop_loss = max(yes_price - 0.10, 0.01)
            else:  # NO
                cost = contracts * (1 - yes_price)
                target_exit = max(yes_price - 0.15, 0.01)
                stop_loss = min(yes_price + 0.10, 0.99)
            
            # Format target and stop loss as percentages
            target_exit = target_exit * 100
            stop_loss = stop_loss * 100
            
            recommendations.append({
                "market": market.get("title", ""),
                "market_id": market.get("id", ""),
                "action": action,
                "probability": round(probability, 1),
                "contracts": contracts,
                "cost": round(cost, 2),
                "target_exit": round(target_exit, 1),
                "stop_loss": round(stop_loss, 1),
                "confidence": confidence,
                "rationale": self._generate_momentum_rationale(market, action, confidence)
            })
            
            # Break if we have enough recommendations
            if len(recommendations) >= max_recommendations:
                break
        
        return recommendations
    
    def _generate_mean_reversion_recommendations(
        self, 
        markets: List[Dict[str, Any]], 
        max_recommendations: int,
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on mean-reversion strategy.
        
        Args:
            markets: List of market data dictionaries
            max_recommendations: Maximum number of recommendations to return
            risk_level: Risk level ("low", "medium", or "high")
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Sort markets by extreme prices (very high or very low yes_price)
        sorted_markets = sorted(
            markets, 
            key=lambda x: abs(x.get("yes_ask", 50) - 50),  # Distance from 50%
            reverse=True
        )
        
        for market in sorted_markets[:max_recommendations * 2]:  # Get more than needed to filter
            yes_price = market.get("yes_ask", 0) / 100.0  # Convert to decimal
            
            # For mean-reversion, we look for markets with extreme prices that might revert
            # If yes_price is very high, we expect it to come down (buy NO)
            if yes_price > 0.8:
                action = "NO"
                probability = (1 - yes_price) * 100
                confidence = "Medium" if yes_price > 0.9 else "Low"
            # If yes_price is very low, we expect it to go up (buy YES)
            elif yes_price < 0.2:
                action = "YES"
                probability = yes_price * 100
                confidence = "Medium" if yes_price < 0.1 else "Low"
            else:
                # Skip markets without extreme prices
                continue
            
            # Adjust position size based on risk level
            if risk_level == "low":
                contracts = 1
            elif risk_level == "medium":
                contracts = 2
            else:  # high
                contracts = 4
            
            # Calculate cost
            if action == "YES":
                cost = contracts * yes_price
                target_exit = min(yes_price + 0.20, 0.99)
                stop_loss = max(yes_price - 0.05, 0.01)
            else:  # NO
                cost = contracts * (1 - yes_price)
                target_exit = max(yes_price - 0.20, 0.01)
                stop_loss = min(yes_price + 0.05, 0.99)
            
            # Format target and stop loss as percentages
            target_exit = target_exit * 100
            stop_loss = stop_loss * 100
            
            recommendations.append({
                "market": market.get("title", ""),
                "market_id": market.get("id", ""),
                "action": action,
                "probability": round(probability, 1),
                "contracts": contracts,
                "cost": round(cost, 2),
                "target_exit": round(target_exit, 1),
                "stop_loss": round(stop_loss, 1),
                "confidence": confidence,
                "rationale": self._generate_mean_reversion_rationale(market, action, confidence)
            })
            
            # Break if we have enough recommendations
            if len(recommendations) >= max_recommendations:
                break
        
        return recommendations
    
    def _generate_momentum_rationale(
        self, 
        market: Dict[str, Any], 
        action: str, 
        confidence: str
    ) -> str:
        """
        Generate a rationale for a momentum strategy recommendation.
        
        Args:
            market: Market data dictionary
            action: Recommended action ("YES" or "NO")
            confidence: Confidence level ("Low", "Medium", or "High")
            
        Returns:
            Rationale string
        """
        market_title = market.get("title", "this market")
        volume = market.get("volume_24h", 0) / 100.0
        
        # Momentum phrases
        momentum_phrases = [
            f"Strong momentum detected for {action} position in {market_title}.",
            f"Market sentiment is clearly favoring {action} outcome in {market_title}.",
            f"Trend analysis indicates continued movement toward {action} in {market_title}.",
            f"Price action shows significant momentum for {action} in {market_title}."
        ]
        
        # Volume phrases
        volume_phrases = [
            f"Trading volume of ${volume:.2f} supports this directional move.",
            f"High trading activity (${volume:.2f}) confirms market conviction.",
            f"Volume analysis shows strong participation at ${volume:.2f}, validating the trend.",
            f"Market liquidity of ${volume:.2f} provides confidence in this direction."
        ]
        
        # Confidence phrases
        confidence_phrases = {
            "High": [
                "Technical indicators strongly support this position.",
                "Multiple signals align to suggest high probability of success.",
                "Price pattern shows exceptional clarity for this trade.",
                "Historical analysis indicates high likelihood of continued momentum."
            ],
            "Medium": [
                "Technical indicators moderately support this position.",
                "Several signals suggest favorable odds for this trade.",
                "Price pattern shows reasonable clarity for this direction.",
                "Historical analysis indicates moderate likelihood of continued momentum."
            ],
            "Low": [
                "Some technical indicators support this position, but with caveats.",
                "A few signals suggest potential for this trade, though uncertainty remains.",
                "Price pattern shows some evidence for this direction, but clarity is limited.",
                "Historical analysis indicates possible continued momentum, though risks exist."
            ]
        }
        
        # Combine phrases
        rationale = (
            f"{random.choice(momentum_phrases)} "
            f"{random.choice(volume_phrases)} "
            f"{random.choice(confidence_phrases[confidence])}"
        )
        
        return rationale
    
    def _generate_mean_reversion_rationale(
        self, 
        market: Dict[str, Any], 
        action: str, 
        confidence: str
    ) -> str:
        """
        Generate a rationale for a mean-reversion strategy recommendation.
        
        Args:
            market: Market data dictionary
            action: Recommended action ("YES" or "NO")
            confidence: Confidence level ("Low", "Medium", or "High")
            
        Returns:
            Rationale string
        """
        market_title = market.get("title", "this market")
        yes_price = market.get("yes_ask", 50) / 100.0
        
        # Mean-reversion phrases
        reversion_phrases = [
            f"Mean-reversion opportunity detected for {action} position in {market_title}.",
            f"Current price appears extreme and likely to revert in {market_title}.",
            f"Statistical analysis suggests price correction toward {action} in {market_title}.",
            f"Overextended price levels indicate potential reversal in {market_title}."
        ]
        
        # Price extreme phrases
        if action == "YES":
            # Current price is low, expecting rise
            price_phrases = [
                f"Current YES price of {yes_price:.2f} appears undervalued based on historical patterns.",
                f"YES price at {yes_price:.2f} shows significant deviation below historical average.",
                f"Market appears to have overreacted to the downside at {yes_price:.2f}.",
                f"Price of {yes_price:.2f} represents an unusually pessimistic outlook that may correct."
            ]
        else:  # NO
            # Current price is high, expecting fall
            price_phrases = [
                f"Current YES price of {yes_price:.2f} appears overvalued based on historical patterns.",
                f"YES price at {yes_price:.2f} shows significant deviation above historical average.",
                f"Market appears to have overreacted to the upside at {yes_price:.2f}.",
                f"Price of {yes_price:.2f} represents an unusually optimistic outlook that may correct."
            ]
        
        # Confidence phrases
        confidence_phrases = {
            "High": [
                "Statistical indicators strongly support reversion to the mean.",
                "Historical analysis shows high probability of price correction from these levels.",
                "Multiple technical signals indicate imminent reversion.",
                "Price extremes of this magnitude have consistently reverted in similar markets."
            ],
            "Medium": [
                "Statistical indicators moderately support reversion to the mean.",
                "Historical analysis suggests reasonable probability of price correction.",
                "Several technical signals point to potential reversion.",
                "Price extremes similar to this have often reverted in comparable markets."
            ],
            "Low": [
                "Some statistical indicators suggest possible reversion to the mean.",
                "Historical analysis shows mixed results for price correction from these levels.",
                "A few technical signals hint at potential reversion, though uncertainty remains.",
                "Price extremes like this have occasionally reverted in similar markets, but not consistently."
            ]
        }
        
        # Combine phrases
        rationale = (
            f"{random.choice(reversion_phrases)} "
            f"{random.choice(price_phrases)} "
            f"{random.choice(confidence_phrases[confidence])}"
        )
        
        return rationale
