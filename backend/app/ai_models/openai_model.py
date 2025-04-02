"""
OpenAI integration for Kalshi trade recommendations.

This module provides functions to generate trade recommendations using OpenAI's GPT models.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional
import requests

from app.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("openai_model")

class OpenAIRecommendationModel:
    """
    OpenAI-powered recommendation model for Kalshi trading.
    """
    
    def __init__(self):
        """Initialize the OpenAI recommendation model."""
        self.api_key = config.get("ai", "api_key")
        self.model = config.get("ai", "model")
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. Model will not be able to generate recommendations.")
        
        logger.info(f"Initialized OpenAI recommendation model with model: {self.model}")
    
    def generate_recommendations(
        self, 
        markets_data: List[Dict[str, Any]], 
        strategy: str,
        max_recommendations: int = 5,
        risk_level: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Generate trade recommendations using OpenAI.
        
        Args:
            markets_data: List of market data dictionaries
            strategy: Strategy to use ("momentum" or "mean-reversion")
            max_recommendations: Maximum number of recommendations to return
            risk_level: Risk level ("low", "medium", or "high")
            
        Returns:
            List of recommendation dictionaries
        """
        if not self.api_key:
            logger.error("Cannot generate recommendations: OpenAI API key not found")
            return []
        
        try:
            # Prepare market data for the prompt
            market_data_str = json.dumps([{
                "id": m["id"],
                "title": m.get("title", ""),
                "subtitle": m.get("subtitle", ""),
                "yes_price": m.get("yes_ask", 0) / 100.0,
                "no_price": m.get("no_ask", 0) / 100.0,
                "volume_24h": m.get("volume_24h", 0),
                "close_time": m.get("close_time", "")
            } for m in markets_data[:20]])  # Limit to 20 markets to keep prompt size reasonable
            
            # Create prompt for OpenAI
            system_prompt = self._create_system_prompt(strategy, risk_level, max_recommendations)
            user_prompt = self._create_user_prompt(market_data_str, strategy, risk_level, max_recommendations)
            
            # Call OpenAI API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            # Extract and parse recommendations
            content = response_data["choices"][0]["message"]["content"]
            recommendations = json.loads(content).get("recommendations", [])
            
            logger.info(f"Generated {len(recommendations)} recommendations using OpenAI")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations with OpenAI: {str(e)}")
            return []
    
    def _create_system_prompt(self, strategy: str, risk_level: str, max_recommendations: int) -> str:
        """
        Create the system prompt for OpenAI.
        
        Args:
            strategy: Strategy to use ("momentum" or "mean-reversion")
            risk_level: Risk level ("low", "medium", or "high")
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            System prompt string
        """
        # Base prompt
        prompt = f"""
        You are a trading assistant for Kalshi prediction markets. Your task is to analyze market data and provide 
        trade recommendations based on a {strategy} strategy with {risk_level} risk tolerance.
        
        Provide exactly {max_recommendations} recommendations in JSON format with these fields:
        - market: The market title
        - market_id: The market ID
        - action: "YES" or "NO" (which contract to buy)
        - probability: Current probability (price as percentage)
        - contracts: Number of contracts to trade (1-5, higher for higher risk)
        - cost: Total cost of the position
        - target_exit: Target exit price as percentage
        - stop_loss: Stop loss price as percentage
        - confidence: "Low", "Medium", or "High"
        - rationale: Brief explanation of the recommendation
        
        Your response should be valid JSON that can be parsed directly, with a structure like:
        {{
            "recommendations": [
                {{
                    "market": "Market Title",
                    "market_id": "market-id",
                    "action": "YES",
                    "probability": 65.0,
                    "contracts": 3,
                    "cost": 1.95,
                    "target_exit": 75.0,
                    "stop_loss": 55.0,
                    "confidence": "Medium",
                    "rationale": "Explanation of why this trade is recommended"
                }},
                ...
            ]
        }}
        """
        
        # Add strategy-specific guidance
        if strategy == "momentum":
            prompt += """
            For a momentum strategy:
            - Look for markets with strong trends and suggest continuing in that direction
            - Identify markets where prices have been consistently moving in one direction
            - Consider volume as an indicator of trend strength
            - For YES positions, look for markets with prices above 60% that are still rising
            - For NO positions, look for markets with prices below 40% that are still falling
            - Higher risk tolerance should mean larger position sizes and wider stop losses
            """
        else:  # mean-reversion
            prompt += """
            For a mean-reversion strategy:
            - Look for markets with extreme prices that might revert to their average
            - Identify markets where prices have moved too far in one direction too quickly
            - For YES positions, look for markets with unusually low prices (below 20%)
            - For NO positions, look for markets with unusually high prices (above 80%)
            - Consider historical price ranges when setting targets and stop losses
            - Higher risk tolerance should mean larger position sizes and tighter stop losses
            """
        
        # Add risk level guidance
        if risk_level == "low":
            prompt += """
            For low risk tolerance:
            - Recommend 1-2 contracts per position
            - Set conservative target exits (10-15% price movement)
            - Set wider stop losses (15-20% price movement)
            - Focus on higher confidence trades
            - Prioritize capital preservation over maximum returns
            """
        elif risk_level == "medium":
            prompt += """
            For medium risk tolerance:
            - Recommend 2-3 contracts per position
            - Set moderate target exits (15-25% price movement)
            - Set moderate stop losses (10-15% price movement)
            - Balance between capital preservation and returns
            """
        else:  # high
            prompt += """
            For high risk tolerance:
            - Recommend 3-5 contracts per position
            - Set aggressive target exits (25%+ price movement)
            - Set tighter stop losses (5-10% price movement)
            - Prioritize maximum returns over capital preservation
            - Consider trades with lower confidence but higher potential returns
            """
        
        return prompt
    
    def _create_user_prompt(
        self, 
        market_data_str: str, 
        strategy: str, 
        risk_level: str, 
        max_recommendations: int
    ) -> str:
        """
        Create the user prompt for OpenAI.
        
        Args:
            market_data_str: JSON string of market data
            strategy: Strategy to use ("momentum" or "mean-reversion")
            risk_level: Risk level ("low", "medium", or "high")
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            User prompt string
        """
        return f"""
        Here is current market data for Kalshi markets:
        {market_data_str}
        
        Based on a {strategy} strategy with {risk_level} risk tolerance, provide {max_recommendations} trade recommendations.
        
        Make sure each recommendation includes a clear rationale explaining why the trade fits the {strategy} strategy
        and how it aligns with a {risk_level} risk profile.
        
        For each recommendation, calculate the appropriate number of contracts, target exit price, and stop loss price
        based on the risk level.
        """
