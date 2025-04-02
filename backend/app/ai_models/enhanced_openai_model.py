"""
Enhanced OpenAI integration for Kalshi trade recommendations.

This module provides improved prompt engineering and context for OpenAI-powered
trade recommendations, incorporating more comprehensive market data.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime, timedelta

from app.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced_openai_model")

class EnhancedOpenAIRecommendationModel:
    """
    Enhanced OpenAI-powered recommendation model for Kalshi trading.
    Features improved prompt engineering and richer market context.
    """
    
    def __init__(self):
        """Initialize the enhanced OpenAI recommendation model."""
        self.api_key = config.get("ai", "api_key")
        self.model = config.get("ai", "model")
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. Model will not be able to generate recommendations.")
        
        logger.info(f"Initialized enhanced OpenAI recommendation model with model: {self.model}")
    
    def generate_recommendations(
        self, 
        markets_data: List[Dict[str, Any]], 
        strategy: str,
        max_recommendations: int = 5,
        risk_level: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Generate trade recommendations using enhanced OpenAI integration.
        
        Args:
            markets_data: List of market data dictionaries
            strategy: Strategy to use ("momentum", "mean-reversion", or "hybrid")
            max_recommendations: Maximum number of recommendations to return
            risk_level: Risk level ("low", "medium", or "high")
            
        Returns:
            List of recommendation dictionaries
        """
        if not self.api_key:
            logger.error("Cannot generate recommendations: OpenAI API key not found")
            return []
        
        try:
            # Enrich market data with additional context
            enriched_markets = self._enrich_market_data(markets_data)
            
            # Prepare market data for the prompt
            market_data_str = json.dumps(enriched_markets)
            
            # Create enhanced prompts for OpenAI
            system_prompt = self._create_enhanced_system_prompt(strategy, risk_level, max_recommendations)
            user_prompt = self._create_enhanced_user_prompt(market_data_str, strategy, risk_level, max_recommendations)
            
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
                "temperature": 0.2,  # Lower temperature for more consistent results
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
            
            logger.info(f"Generated {len(recommendations)} recommendations using enhanced OpenAI integration")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations with enhanced OpenAI: {str(e)}")
            return []
    
    def _enrich_market_data(self, markets_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich market data with additional context for better recommendations.
        
        Args:
            markets_data: List of market data dictionaries
            
        Returns:
            List of enriched market data dictionaries
        """
        enriched_markets = []
        
        for market in markets_data[:20]:  # Limit to 20 markets to keep prompt size reasonable
            # Calculate time to market close
            close_time = market.get("close_time", "")
            time_to_close = "Unknown"
            
            if close_time:
                try:
                    close_datetime = datetime.fromisoformat(close_time.replace("Z", "+00:00"))
                    now = datetime.now().astimezone()
                    time_diff = close_datetime - now
                    
                    if time_diff.total_seconds() > 0:
                        days = time_diff.days
                        hours = time_diff.seconds // 3600
                        minutes = (time_diff.seconds % 3600) // 60
                        
                        if days > 0:
                            time_to_close = f"{days} days, {hours} hours"
                        elif hours > 0:
                            time_to_close = f"{hours} hours, {minutes} minutes"
                        else:
                            time_to_close = f"{minutes} minutes"
                    else:
                        time_to_close = "Market closed"
                except Exception as e:
                    logger.warning(f"Failed to parse close time: {str(e)}")
            
            # Calculate price movement indicators
            yes_price = market.get("yes_ask", 0) / 100.0
            price_extremity = abs(yes_price - 0.5)  # How far from 50%
            
            # Create enriched market data
            enriched_market = {
                "id": market.get("id", ""),
                "title": market.get("title", ""),
                "subtitle": market.get("subtitle", ""),
                "yes_price": yes_price,
                "no_price": market.get("no_ask", 0) / 100.0,
                "volume_24h": market.get("volume_24h", 0) / 100.0,  # Convert to dollars
                "time_to_close": time_to_close,
                "price_extremity": price_extremity,
                "market_category": self._categorize_market(market.get("title", ""), market.get("subtitle", ""))
            }
            
            enriched_markets.append(enriched_market)
        
        return enriched_markets
    
    def _categorize_market(self, title: str, subtitle: str) -> str:
        """
        Categorize the market based on title and subtitle.
        
        Args:
            title: Market title
            subtitle: Market subtitle
            
        Returns:
            Market category
        """
        title_lower = title.lower()
        subtitle_lower = subtitle.lower()
        
        if any(word in title_lower or word in subtitle_lower for word in ["btc", "bitcoin", "eth", "ethereum", "crypto"]):
            return "Cryptocurrency"
        elif any(word in title_lower or word in subtitle_lower for word in ["s&p", "nasdaq", "dow", "index", "stock"]):
            return "Stock Market"
        elif any(word in title_lower or word in subtitle_lower for word in ["fed", "interest", "rate", "inflation"]):
            return "Economic"
        elif any(word in title_lower or word in subtitle_lower for word in ["election", "president", "congress", "senate"]):
            return "Political"
        elif any(word in title_lower or word in subtitle_lower for word in ["weather", "temperature", "rain", "snow"]):
            return "Weather"
        else:
            return "Other"
    
    def _create_enhanced_system_prompt(self, strategy: str, risk_level: str, max_recommendations: int) -> str:
        """
        Create an enhanced system prompt for OpenAI with improved instructions.
        
        Args:
            strategy: Strategy to use ("momentum", "mean-reversion", or "hybrid")
            risk_level: Risk level ("low", "medium", or "high")
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            Enhanced system prompt string
        """
        # Base prompt with improved instructions
        prompt = f"""
        You are an expert trading advisor specializing in Kalshi prediction markets. Your task is to analyze market data and provide 
        {max_recommendations} high-quality trade recommendations based on a {strategy} strategy with {risk_level} risk tolerance.
        
        Your recommendations must be data-driven, precise, and actionable. Each recommendation should include:
        
        1. The specific market to trade
        2. Whether to buy YES or NO contracts
        3. The number of contracts to purchase
        4. Target exit price and stop loss levels
        5. A clear, concise rationale explaining the recommendation
        
        Format your response as a valid JSON object with this structure:
        {{
            "recommendations": [
                {{
                    "market": "Market Title",
                    "market_id": "market-id",
                    "action": "YES" or "NO",
                    "probability": current probability as percentage (e.g., 65.0),
                    "contracts": number of contracts to trade (1-5),
                    "cost": total cost of the position in dollars,
                    "target_exit": target exit price as percentage,
                    "stop_loss": stop loss price as percentage,
                    "confidence": "Low", "Medium", or "High",
                    "rationale": detailed explanation of the recommendation
                }},
                ...
            ]
        }}
        """
        
        # Add detailed strategy-specific guidance
        if strategy == "momentum":
            prompt += """
            For momentum strategy recommendations:
            
            1. Identify markets with strong directional trends
               - Look for consistent price movement in one direction
               - Higher trading volume supports stronger momentum signals
               - Recent acceleration in price movement is particularly significant
            
            2. Evaluate trend strength and sustainability
               - Consider time remaining until market close
               - Markets with longer time horizons allow trends to develop further
               - Evaluate if current momentum is likely to continue based on market category
            
            3. Set appropriate position sizing
               - Scale position size based on trend strength and conviction
               - Consider market liquidity when determining position size
               - Adjust for risk level (higher risk = larger positions)
            
            4. Determine precise exit points
               - Set target exits based on realistic price projections
               - Place stop losses at technical support/resistance levels
               - Tighter stops for higher-risk strategies, wider for lower-risk
            """
        elif strategy == "mean-reversion":
            prompt += """
            For mean-reversion strategy recommendations:
            
            1. Identify markets with extreme price deviations
               - Look for prices significantly above or below historical averages
               - Higher price_extremity values indicate stronger reversion potential
               - Consider if the extreme price is justified by new information
            
            2. Evaluate reversion potential
               - Markets with shorter time horizons may have less time to revert
               - Consider if there are catalysts that could trigger reversion
               - Evaluate if the current price represents an overreaction
            
            3. Set appropriate position sizing
               - Scale position size based on reversion potential
               - More extreme prices may warrant larger positions (adjusted for risk)
               - Consider market liquidity when determining position size
            
            4. Determine precise exit points
               - Set target exits based on historical price levels or fair value estimates
               - Place stop losses to limit downside if price continues to move away
               - Consider time-based exits if reversion doesn't occur within expected timeframe
            """
        else:  # hybrid
            prompt += """
            For hybrid strategy recommendations:
            
            1. Apply both momentum and mean-reversion analysis
               - Identify markets that show strong signals for either strategy
               - Prioritize markets where both strategies align for highest conviction trades
               - Balance the portfolio between momentum and mean-reversion positions
            
            2. Evaluate market-specific factors
               - Different market categories may respond better to different strategies
               - Consider time horizons when selecting between momentum and reversion
               - Evaluate current market conditions and overall sentiment
            
            3. Set appropriate position sizing
               - Allocate larger positions to highest conviction signals
               - Diversify across both strategies to manage risk
               - Adjust position sizes based on risk level and strategy confidence
            
            4. Determine precise exit points
               - Set strategy-appropriate exit points for each position
               - Consider correlation between positions when setting overall risk limits
               - Implement time-based reviews to reassess positions regularly
            """
        
        # Add risk level-specific guidance
        if risk_level == "low":
            prompt += """
            For low risk tolerance recommendations:
            
            1. Position sizing
               - Recommend 1-2 contracts per position
               - Total exposure should be limited and diversified
               - Focus on higher probability trades (>70% confidence)
            
            2. Exit strategy
               - Set conservative target exits (10-15% price movement)
               - Use wider stop losses (15-20% price movement)
               - Prioritize capital preservation over maximum returns
            
            3. Market selection
               - Focus on more liquid markets with higher trading volume
               - Prefer markets with clearer signals and higher confidence
               - Avoid markets with extreme volatility or uncertainty
            """
        elif risk_level == "medium":
            prompt += """
            For medium risk tolerance recommendations:
            
            1. Position sizing
               - Recommend 2-3 contracts per position
               - Balance between capital preservation and growth
               - Consider both high and medium probability trades
            
            2. Exit strategy
               - Set moderate target exits (15-25% price movement)
               - Use balanced stop losses (10-15% price movement)
               - Aim for optimal risk-reward ratios around 2:1
            
            3. Market selection
               - Consider a wider range of markets with varying liquidity
               - Balance between high-confidence and higher-potential trades
               - Include some contrarian positions when signals are strong
            """
        else:  # high
            prompt += """
            For high risk tolerance recommendations:
            
            1. Position sizing
               - Recommend 3-5 contracts per position
               - Prioritize maximum returns over capital preservation
               - Consider both high-probability and speculative opportunities
            
            2. Exit strategy
               - Set aggressive target exits (25%+ price movement)
               - Use tighter stop losses (5-10% price movement)
               - Aim for higher risk-reward ratios of 3:1 or greater
            
            3. Market selection
               - Consider all markets with trading opportunities
               - Include some speculative positions with higher upside
               - Willing to take contrarian positions against current trends
            """
        
        return prompt
    
    def _create_enhanced_user_prompt(
        self, 
        market_data_str: str, 
        strategy: str, 
        risk_level: str, 
        max_recommendations: int
    ) -> str:
        """
        Create an enhanced user prompt for OpenAI with improved context.
        
        Args:
            market_data_str: JSON string of enriched market data
            strategy: Strategy to use ("momentum", "mean-reversion", or "hybrid")
            risk_level: Risk level ("low", "medium", or "high")
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            Enhanced user prompt string
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""
        Current date and time: {current_time}
        
        Here is detailed market data for Kalshi prediction markets:
        {market_data_str}
        
        Based on a {strategy} strategy with {risk_level} risk tolerance, provide exactly {max_recommendations} trade recommendations.
        
        For each recommendation:
        
        1. Analyze the market data thoroughly, considering price levels, volume, time to close, and market category
        2. Determine whether a YES or NO position aligns with the {strategy} strategy
        3. Calculate an appropriate position size based on the {risk_level} risk profile
        4. Set precise target exit and stop loss levels based on technical analysis
        5. Provide a detailed rationale explaining why this trade fits the strategy and risk profile
        
        Focus on the highest conviction trades that offer the best risk-adjusted returns.
        """
