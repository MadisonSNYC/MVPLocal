"""
Update to the AI models package to include the enhanced OpenAI model.

This module updates the AI models package to include the enhanced OpenAI model
with improved prompt engineering and richer market context.
"""

from app.ai_models.openai_model import OpenAIRecommendationModel
from app.ai_models.rule_based_model import RuleBasedRecommendationModel
from app.ai_models.hybrid_model import HybridRecommendationModel
from app.ai_models.enhanced_openai_model import EnhancedOpenAIRecommendationModel

__all__ = [
    'OpenAIRecommendationModel',
    'RuleBasedRecommendationModel',
    'HybridRecommendationModel',
    'EnhancedOpenAIRecommendationModel'
]
