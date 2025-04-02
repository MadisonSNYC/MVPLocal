"""
Hybrid recommendation model for Kalshi trade recommendations.

This module provides a hybrid approach that combines multiple recommendation models
and selects the best recommendations based on confidence and strategy.
"""

import logging
from typing import Dict, List, Any, Optional
import random

from app.ai_models.openai_model import OpenAIRecommendationModel
from app.ai_models.rule_based_model import RuleBasedRecommendationModel
from app.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("hybrid_model")

class HybridRecommendationModel:
    """
    Hybrid recommendation model for Kalshi trading.
    Combines OpenAI-powered and rule-based models for robust recommendations.
    """
    
    def __init__(self):
        """Initialize the hybrid recommendation model."""
        self.openai_model = OpenAIRecommendationModel()
        self.rule_based_model = RuleBasedRecommendationModel()
        self.openai_enabled = bool(config.get("ai", "api_key"))
        
        logger.info(f"Initialized hybrid recommendation model (OpenAI enabled: {self.openai_enabled})")
    
    def generate_recommendations(
        self, 
        markets_data: List[Dict[str, Any]], 
        strategy: str,
        max_recommendations: int = 5,
        risk_level: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Generate trade recommendations using a hybrid approach.
        
        Args:
            markets_data: List of market data dictionaries
            strategy: Strategy to use ("momentum", "mean-reversion", or "hybrid")
            max_recommendations: Maximum number of recommendations to return
            risk_level: Risk level ("low", "medium", or "high")
            
        Returns:
            List of recommendation dictionaries
        """
        # For hybrid strategy, combine recommendations from both momentum and mean-reversion
        if strategy == "hybrid":
            return self._generate_hybrid_strategy_recommendations(
                markets_data, 
                max_recommendations, 
                risk_level
            )
        
        # For standard strategies, try OpenAI first if enabled
        if self.openai_enabled:
            try:
                openai_recommendations = self.openai_model.generate_recommendations(
                    markets_data, 
                    strategy, 
                    max_recommendations, 
                    risk_level
                )
                
                # If we got valid recommendations from OpenAI, use them
                if openai_recommendations and len(openai_recommendations) > 0:
                    logger.info(f"Using {len(openai_recommendations)} OpenAI recommendations for {strategy} strategy")
                    return openai_recommendations
            except Exception as e:
                logger.error(f"OpenAI recommendation generation failed: {str(e)}")
        
        # Fallback to rule-based model
        logger.info(f"Using rule-based recommendations for {strategy} strategy")
        return self.rule_based_model.generate_recommendations(
            markets_data, 
            strategy, 
            max_recommendations, 
            risk_level
        )
    
    def _generate_hybrid_strategy_recommendations(
        self, 
        markets_data: List[Dict[str, Any]], 
        max_recommendations: int,
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations using a hybrid of momentum and mean-reversion strategies.
        
        Args:
            markets_data: List of market data dictionaries
            max_recommendations: Maximum number of recommendations to return
            risk_level: Risk level ("low", "medium", or "high")
            
        Returns:
            List of recommendation dictionaries
        """
        # Determine split between strategies based on risk level
        if risk_level == "low":
            # Low risk: more mean-reversion (tends to be more conservative)
            momentum_count = max(1, int(max_recommendations * 0.4))
            mean_reversion_count = max_recommendations - momentum_count
        elif risk_level == "high":
            # High risk: more momentum (tends to be more aggressive)
            momentum_count = max(1, int(max_recommendations * 0.7))
            mean_reversion_count = max_recommendations - momentum_count
        else:  # medium
            # Medium risk: balanced approach
            momentum_count = max(1, int(max_recommendations * 0.5))
            mean_reversion_count = max_recommendations - momentum_count
        
        # Get recommendations for each strategy
        momentum_recommendations = []
        mean_reversion_recommendations = []
        
        # Try OpenAI first if enabled
        if self.openai_enabled:
            try:
                momentum_recommendations = self.openai_model.generate_recommendations(
                    markets_data, 
                    "momentum", 
                    momentum_count, 
                    risk_level
                )
                
                mean_reversion_recommendations = self.openai_model.generate_recommendations(
                    markets_data, 
                    "mean-reversion", 
                    mean_reversion_count, 
                    risk_level
                )
            except Exception as e:
                logger.error(f"OpenAI recommendation generation failed for hybrid strategy: {str(e)}")
        
        # Fallback to rule-based model if needed
        if not momentum_recommendations or len(momentum_recommendations) < momentum_count:
            momentum_recommendations = self.rule_based_model.generate_recommendations(
                markets_data, 
                "momentum", 
                momentum_count, 
                risk_level
            )
        
        if not mean_reversion_recommendations or len(mean_reversion_recommendations) < mean_reversion_count:
            mean_reversion_recommendations = self.rule_based_model.generate_recommendations(
                markets_data, 
                "mean-reversion", 
                mean_reversion_count, 
                risk_level
            )
        
        # Add strategy tag to each recommendation
        for rec in momentum_recommendations:
            rec["strategy"] = "momentum"
        
        for rec in mean_reversion_recommendations:
            rec["strategy"] = "mean-reversion"
        
        # Combine recommendations
        combined_recommendations = momentum_recommendations + mean_reversion_recommendations
        
        # Ensure we don't have duplicate market IDs
        unique_recommendations = []
        seen_market_ids = set()
        
        for rec in combined_recommendations:
            if rec["market_id"] not in seen_market_ids:
                unique_recommendations.append(rec)
                seen_market_ids.add(rec["market_id"])
                
                # Break if we have enough recommendations
                if len(unique_recommendations) >= max_recommendations:
                    break
        
        # If we still need more recommendations, add more from either strategy
        if len(unique_recommendations) < max_recommendations:
            # Get all remaining recommendations
            remaining_recs = [
                rec for rec in combined_recommendations 
                if rec["market_id"] not in seen_market_ids
            ]
            
            # Sort by confidence (High > Medium > Low)
            confidence_order = {"High": 3, "Medium": 2, "Low": 1}
            remaining_recs.sort(key=lambda x: confidence_order.get(x["confidence"], 0), reverse=True)
            
            # Add remaining recommendations until we reach the limit
            for rec in remaining_recs:
                if len(unique_recommendations) >= max_recommendations:
                    break
                
                unique_recommendations.append(rec)
                seen_market_ids.add(rec["market_id"])
        
        logger.info(f"Generated {len(unique_recommendations)} hybrid strategy recommendations")
        return unique_recommendations
