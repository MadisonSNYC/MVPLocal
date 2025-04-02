import React, { useState, useEffect } from 'react';
import { useOffline } from '../contexts/OfflineContext';

interface StrategyOption {
  id: string;
  name: string;
  description: string;
  risk_levels: string[];
}

interface StrategyRecommendation {
  market_id: string;
  market: string;
  action: string;
  contracts: number;
  probability: number;
  cost: number;
  confidence: string;
  rationale: string;
  strategy: string;
  target_exit: number;
  stop_loss: number;
}

const Strategies: React.FC = () => {
  const { isOffline } = useOffline();
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [strategies, setStrategies] = useState<StrategyOption[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<string>('hybrid');
  const [riskLevel, setRiskLevel] = useState<string>('medium');
  const [recommendations, setRecommendations] = useState<StrategyRecommendation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  // Fetch available strategies
  useEffect(() => {
    const fetchStrategies = async () => {
      if (isOffline) {
        setIsLoading(false);
        return;
      }
      
      try {
        setIsLoading(true);
        setError(null);
        
        const response = await window.api.fetch('/api/enhanced/recommendations/strategies');
        setStrategies(response.strategies || []);
      } catch (error) {
        console.error('Failed to fetch strategies:', error);
        setError('Failed to fetch available strategies. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStrategies();
  }, [isOffline]);

  // Fetch recommendations when strategy or risk level changes
  useEffect(() => {
    const fetchRecommendations = async () => {
      if (isOffline) {
        setIsLoading(false);
        return;
      }
      
      try {
        setIsLoading(true);
        setError(null);
        
        const response = await window.api.fetch(`/api/enhanced/recommendations?strategy=${selectedStrategy}&risk_level=${riskLevel}&max_recommendations=10`);
        setRecommendations(response.recommendations || []);
        setLastUpdated(new Date().toLocaleTimeString());
      } catch (error) {
        console.error('Failed to fetch recommendations:', error);
        setError('Failed to fetch recommendations. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    if (selectedStrategy && riskLevel) {
      fetchRecommendations();
    }
  }, [selectedStrategy, riskLevel, isOffline]);

  // Refresh recommendations
  const refreshRecommendations = async () => {
    if (isOffline) {
      setError('Cannot refresh recommendations in offline mode');
      return;
    }
    
    try {
      setIsRefreshing(true);
      setError(null);
      
      const response = await window.api.fetch(`/api/enhanced/recommendations?strategy=${selectedStrategy}&risk_level=${riskLevel}&max_recommendations=10&force_refresh=true`);
      setRecommendations(response.recommendations || []);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Failed to refresh recommendations:', error);
      setError('Failed to refresh recommendations. Please try again.');
    } finally {
      setIsRefreshing(false);
    }
  };

  // Get confidence badge color
  const getConfidenceBadgeColor = (confidence: string) => {
    switch (confidence.toLowerCase()) {
      case 'high':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-blue-100 text-blue-800';
      case 'low':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get strategy badge color
  const getStrategyBadgeColor = (strategy: string) => {
    switch (strategy.toLowerCase()) {
      case 'momentum':
        return 'bg-purple-100 text-purple-800';
      case 'mean-reversion':
        return 'bg-indigo-100 text-indigo-800';
      case 'hybrid':
        return 'bg-blue-100 text-blue-800';
      case 'arbitrage':
        return 'bg-green-100 text-green-800';
      case 'volatility':
        return 'bg-orange-100 text-orange-800';
      case 'sentiment':
        return 'bg-pink-100 text-pink-800';
      case 'combined':
        return 'bg-teal-100 text-teal-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Trading Strategies</h1>
        <div className="flex space-x-2">
          <button
            onClick={refreshRecommendations}
            disabled={isRefreshing || isOffline}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 disabled:opacity-50 flex items-center"
          >
            {isRefreshing ? (
              <>
                <span className="inline-block animate-spin rounded-full h-4 w-4 border-2 border-current border-r-transparent mr-2"></span>
                Refreshing...
              </>
            ) : (
              'Refresh Recommendations'
            )}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md mb-4">
          {error}
        </div>
      )}

      {/* Strategy Selection */}
      <div className="bg-card rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Strategy Settings</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium mb-2">Trading Strategy</label>
            <select
              value={selectedStrategy}
              onChange={(e) => setSelectedStrategy(e.target.value)}
              disabled={isLoading}
              className="w-full px-3 py-2 bg-background border border-input rounded-md"
            >
              {strategies.map((strategy) => (
                <option key={strategy.id} value={strategy.id}>
                  {strategy.name}
                </option>
              ))}
            </select>
            
            {strategies.find(s => s.id === selectedStrategy)?.description && (
              <p className="mt-2 text-sm text-muted-foreground">
                {strategies.find(s => s.id === selectedStrategy)?.description}
              </p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Risk Level</label>
            <select
              value={riskLevel}
              onChange={(e) => setRiskLevel(e.target.value)}
              disabled={isLoading}
              className="w-full px-3 py-2 bg-background border border-input rounded-md"
            >
              <option value="low">Low Risk</option>
              <option value="medium">Medium Risk</option>
              <option value="high">High Risk</option>
            </select>
            
            <p className="mt-2 text-sm text-muted-foreground">
              {riskLevel === 'low' && 'Conservative approach with only high-confidence recommendations.'}
              {riskLevel === 'medium' && 'Balanced approach with medium to high-confidence recommendations.'}
              {riskLevel === 'high' && 'Aggressive approach including all confidence levels.'}
            </p>
          </div>
        </div>
        
        {lastUpdated && (
          <p className="mt-4 text-sm text-muted-foreground">
            Last updated: {lastUpdated}
          </p>
        )}
      </div>

      {/* Recommendations */}
      <div className="bg-card rounded-lg shadow-md overflow-hidden">
        <div className="p-4 bg-muted/50 border-b border-border">
          <h2 className="text-lg font-medium">Trade Recommendations</h2>
        </div>
        
        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary border-r-transparent"></div>
            <p className="mt-2 text-muted-foreground">Loading recommendations...</p>
          </div>
        )}
        
        {/* Empty State */}
        {!isLoading && recommendations.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            No recommendations available for the selected strategy and risk level.
          </div>
        )}
        
        {/* Recommendations List */}
        {!isLoading && recommendations.length > 0 && (
          <div className="divide-y divide-border">
            {recommendations.map((recommendation, index) => (
              <div key={index} className="p-4 hover:bg-muted/30">
                <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium">{recommendation.market}</h3>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        recommendation.action === 'YES' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {recommendation.action}
                      </span>
                    </div>
                    
                    <p className="text-sm text-muted-foreground mb-2">
                      {recommendation.rationale}
                    </p>
                    
                    <div className="flex flex-wrap gap-2 mb-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceBadgeColor(recommendation.confidence)}`}>
                        {recommendation.confidence} Confidence
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStrategyBadgeColor(recommendation.strategy)}`}>
                        {recommendation.strategy.charAt(0).toUpperCase() + recommendation.strategy.slice(1)} Strategy
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex flex-col gap-1 min-w-[200px]">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Contracts:</span>
                      <span className="text-sm font-medium">{recommendation.contracts}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Probability:</span>
                      <span className="text-sm font-medium">{recommendation.probability}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Cost:</span>
                      <span className="text-sm font-medium">${recommendation.cost.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Target Exit:</span>
                      <span className="text-sm font-medium">{recommendation.target_exit}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Stop Loss:</span>
                      <span className="text-sm font-medium">{recommendation.stop_loss}%</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Strategies;
