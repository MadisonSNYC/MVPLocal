import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';
import { useOffline } from '../contexts/OfflineContext';
import { useMarkets } from '../contexts/MarketsContext';

const Strategies = () => {
  const { apiRequest, isConnected } = useApi();
  const { isOffline, cachedData, cacheData } = useOffline();
  const { filteredMarkets } = useMarkets();
  
  const [strategies, setStrategies] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState('all');
  const [riskLevel, setRiskLevel] = useState('medium');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch strategies
  useEffect(() => {
    const fetchStrategies = async () => {
      if (isOffline) {
        if (cachedData.strategies) {
          setStrategies(cachedData.strategies);
        }
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const data = await apiRequest('get', '/api/strategies');
        setStrategies(data);
        cacheData('strategies', data);
      } catch (error) {
        setError('Failed to fetch strategies');
        if (cachedData.strategies) {
          setStrategies(cachedData.strategies);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchStrategies();
  }, [isConnected, isOffline]);

  // Fetch recommendations when strategy or risk level changes
  useEffect(() => {
    const fetchRecommendations = async () => {
      if (isOffline) {
        if (cachedData.recommendations) {
          // Filter cached recommendations based on selected strategy
          const filtered = selectedStrategy === 'all'
            ? cachedData.recommendations
            : cachedData.recommendations.filter(rec => rec.strategy === selectedStrategy);
          setRecommendations(filtered);
        }
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const endpoint = selectedStrategy === 'all'
          ? `/api/recommendations?risk=${riskLevel}`
          : `/api/recommendations?strategy=${selectedStrategy}&risk=${riskLevel}`;
        
        const data = await apiRequest('get', endpoint);
        setRecommendations(data);
        
        // Cache all recommendations
        if (selectedStrategy === 'all') {
          cacheData('recommendations', data);
        }
      } catch (error) {
        setError('Failed to fetch recommendations');
        if (cachedData.recommendations) {
          const filtered = selectedStrategy === 'all'
            ? cachedData.recommendations
            : cachedData.recommendations.filter(rec => rec.strategy === selectedStrategy);
          setRecommendations(filtered);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, [selectedStrategy, riskLevel, isConnected, isOffline]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Trading Strategies</h1>
      </div>

      {/* Strategy Selection */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Strategy Settings</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Strategy
            </label>
            <select
              value={selectedStrategy}
              onChange={(e) => setSelectedStrategy(e.target.value)}
              className="input-field w-full"
              disabled={isLoading}
            >
              <option value="all">All Strategies</option>
              {strategies.map((strategy) => (
                <option key={strategy.id} value={strategy.id}>
                  {strategy.name}
                </option>
              ))}
            </select>
            {selectedStrategy !== 'all' && strategies.length > 0 && (
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                {strategies.find(s => s.id === selectedStrategy)?.description || ''}
              </p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Risk Level
            </label>
            <div className="flex space-x-4">
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  className="form-radio"
                  name="riskLevel"
                  value="low"
                  checked={riskLevel === 'low'}
                  onChange={() => setRiskLevel('low')}
                  disabled={isLoading}
                />
                <span className="ml-2">Low</span>
              </label>
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  className="form-radio"
                  name="riskLevel"
                  value="medium"
                  checked={riskLevel === 'medium'}
                  onChange={() => setRiskLevel('medium')}
                  disabled={isLoading}
                />
                <span className="ml-2">Medium</span>
              </label>
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  className="form-radio"
                  name="riskLevel"
                  value="high"
                  checked={riskLevel === 'high'}
                  onChange={() => setRiskLevel('high')}
                  disabled={isLoading}
                />
                <span className="ml-2">High</span>
              </label>
            </div>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              {riskLevel === 'low' && 'Conservative approach with lower returns but higher probability of success.'}
              {riskLevel === 'medium' && 'Balanced approach with moderate returns and reasonable probability of success.'}
              {riskLevel === 'high' && 'Aggressive approach with higher potential returns but lower probability of success.'}
            </p>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">
          Recommendations
          {selectedStrategy !== 'all' && strategies.find(s => s.id === selectedStrategy) && (
            <span className="ml-2 text-base font-normal text-gray-500 dark:text-gray-400">
              ({strategies.find(s => s.id === selectedStrategy).name})
            </span>
          )}
        </h2>
        
        {isLoading ? (
          <p>Loading recommendations...</p>
        ) : error ? (
          <p className="text-red-500">{error}</p>
        ) : recommendations.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400">No recommendations available for the selected strategy and risk level.</p>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {recommendations.map((rec) => (
              <div key={rec.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex flex-col md:flex-row md:justify-between md:items-start">
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">{rec.market_title}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{rec.series}</p>
                  </div>
                  <div className="flex items-center mt-2 md:mt-0">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      rec.confidence > 0.7 ? 'bg-green-100 text-green-800' : 
                      rec.confidence > 0.4 ? 'bg-yellow-100 text-yellow-800' : 
                      'bg-red-100 text-red-800'
                    }`}>
                      {Math.round(rec.confidence * 100)}% Confidence
                    </span>
                    <span className="ml-2 px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                      {rec.strategy}
                    </span>
                  </div>
                </div>
                
                <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm">
                      <span className="font-medium">Recommendation:</span> {rec.position_type} {rec.outcome}
                    </p>
                    <p className="text-sm">
                      <span className="font-medium">Price:</span> ${rec.price.toFixed(2)}
                    </p>
                    <p className="text-sm">
                      <span className="font-medium">Quantity:</span> {rec.quantity || 'N/A'}
                    </p>
                  </div>
                  
                  <div>
                    <p className="text-sm">
                      <span className="font-medium">Target Exit:</span> ${rec.target_exit ? rec.target_exit.toFixed(2) : 'N/A'}
                    </p>
                    <p className="text-sm">
                      <span className="font-medium">Stop Loss:</span> ${rec.stop_loss ? rec.stop_loss.toFixed(2) : 'N/A'}
                    </p>
                    <p className="text-sm">
                      <span className="font-medium">Risk/Reward:</span> {rec.risk_reward || 'N/A'}
                    </p>
                  </div>
                  
                  <div>
                    <p className="text-sm">
                      <span className="font-medium">Rationale:</span> {rec.rationale || 'N/A'}
                    </p>
                  </div>
                </div>
                
                <div className="mt-4 flex space-x-2">
                  <button className="btn-primary">Place Order</button>
                  <button className="btn-secondary">Add to Watchlist</button>
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