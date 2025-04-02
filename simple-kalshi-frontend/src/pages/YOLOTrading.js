import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';
import { useOffline } from '../contexts/OfflineContext';
import { useMarkets } from '../contexts/MarketsContext';
import { usePortfolio } from '../contexts/PortfolioContext';

const YOLOTrading = () => {
  const { apiRequest, isConnected } = useApi();
  const { isOffline } = useOffline();
  const { portfolio } = usePortfolio();
  
  const [isEnabled, setIsEnabled] = useState(false);
  const [config, setConfig] = useState({
    maxSpendPerTrade: 10,
    riskLevel: 'medium',
    strategies: [],
    marketSeries: []
  });
  const [availableStrategies, setAvailableStrategies] = useState([]);
  const [yoloStatus, setYoloStatus] = useState({
    isRunning: false,
    lastRun: null,
    tradesExecuted: 0,
    activeOrders: 0
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { targetSeries } = useMarkets();

  // Fetch available strategies
  useEffect(() => {
    const fetchStrategies = async () => {
      if (isOffline) return;

      setIsLoading(true);
      setError(null);

      try {
        const data = await apiRequest('get', '/api/strategies');
        setAvailableStrategies(data);
        
        // Initialize selected strategies if empty
        if (config.strategies.length === 0 && data.length > 0) {
          setConfig(prev => ({
            ...prev,
            strategies: [data[0].id]
          }));
        }
      } catch (error) {
        setError('Failed to fetch strategies');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStrategies();
  }, [isConnected]);

  // Fetch YOLO status
  useEffect(() => {
    const fetchYoloStatus = async () => {
      if (isOffline) return;

      setIsLoading(true);
      
      try {
        const data = await apiRequest('get', '/api/yolo/status');
        setYoloStatus(data);
        setIsEnabled(data.isRunning);
        
        // Update config from server if available
        const configData = await apiRequest('get', '/api/yolo/config');
        setConfig(configData);
      } catch (error) {
        console.error('Failed to fetch YOLO status:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchYoloStatus();
    
    // Poll for status updates every 30 seconds if enabled
    let interval;
    if (isEnabled && !isOffline) {
      interval = setInterval(fetchYoloStatus, 30000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isEnabled, isConnected, isOffline]);

  // Handle strategy selection
  const handleStrategyChange = (strategyId) => {
    setConfig(prev => {
      const strategies = prev.strategies.includes(strategyId)
        ? prev.strategies.filter(id => id !== strategyId)
        : [...prev.strategies, strategyId];
      
      return {
        ...prev,
        strategies
      };
    });
  };

  // Handle market series selection
  const handleSeriesChange = (series) => {
    setConfig(prev => {
      const marketSeries = prev.marketSeries.includes(series)
        ? prev.marketSeries.filter(s => s !== series)
        : [...prev.marketSeries, series];
      
      return {
        ...prev,
        marketSeries
      };
    });
  };

  // Save YOLO configuration
  const saveConfig = async () => {
    if (isOffline) {
      setError('Cannot save configuration while offline');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      await apiRequest('post', '/api/yolo/config', config);
      alert('Configuration saved successfully');
    } catch (error) {
      setError('Failed to save configuration');
    } finally {
      setIsLoading(false);
    }
  };

  // Toggle YOLO mode
  const toggleYoloMode = async () => {
    if (isOffline) {
      setError('Cannot toggle YOLO mode while offline');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      const newStatus = !isEnabled;
      await apiRequest('post', `/api/yolo/${newStatus ? 'start' : 'stop'}`);
      setIsEnabled(newStatus);
      
      // Refresh status
      const data = await apiRequest('get', '/api/yolo/status');
      setYoloStatus(data);
    } catch (error) {
      setError(`Failed to ${isEnabled ? 'stop' : 'start'} YOLO mode`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">YOLO Automated Trading</h1>
        <div className="flex items-center">
          <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
            yoloStatus.isRunning ? 'bg-green-500' : 'bg-red-500'
          }`}></span>
          <span className="text-sm text-gray-600 dark:text-gray-300 mr-4">
            {yoloStatus.isRunning ? 'Running' : 'Stopped'}
          </span>
          <button
            onClick={toggleYoloMode}
            disabled={isOffline || isLoading}
            className={`px-4 py-2 rounded-md font-medium ${
              isEnabled
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-green-600 hover:bg-green-700 text-white'
            } disabled:opacity-50`}
          >
            {isEnabled ? 'Stop YOLO Mode' : 'Start YOLO Mode'}
          </button>
        </div>
      </div>

      {/* Warning Banner */}
      <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium">
              Warning: YOLO mode will automatically execute trades based on your configuration.
              Use at your own risk and set appropriate limits.
            </p>
          </div>
        </div>
      </div>

      {/* YOLO Status */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg">
            <p className="text-sm text-gray-500 dark:text-gray-400">Available Balance</p>
            <p className="text-2xl font-bold">${portfolio.balance.toFixed(2)}</p>
          </div>
          <div className="bg-green-50 dark:bg-green-900 p-4 rounded-lg">
            <p className="text-sm text-gray-500 dark:text-gray-400">Trades Executed</p>
            <p className="text-2xl font-bold">{yoloStatus.tradesExecuted}</p>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900 p-4 rounded-lg">
            <p className="text-sm text-gray-500 dark:text-gray-400">Active Orders</p>
            <p className="text-2xl font-bold">{yoloStatus.activeOrders}</p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <p className="text-sm text-gray-500 dark:text-gray-400">Last Run</p>
            <p className="text-xl font-bold">
              {yoloStatus.lastRun ? new Date(yoloStatus.lastRun).toLocaleString() : 'Never'}
            </p>
          </div>
        </div>
      </div>

      {/* YOLO Configuration */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Configuration</h2>
        
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4">
            <p>{error}</p>
          </div>
        )}
        
        <div className="space-y-6">
          {/* Trading Limits */}
          <div>
            <h3 className="text-lg font-medium mb-2">Trading Limits</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Maximum Spend Per Trade ($)
                </label>
                <input
                  type="number"
                  min="1"
                  max="1000"
                  value={config.maxSpendPerTrade}
                  onChange={(e) => setConfig({ ...config, maxSpendPerTrade: parseInt(e.target.value) })}
                  className="input-field w-full"
                  disabled={isEnabled || isOffline}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Risk Level
                </label>
                <div className="flex space-x-4">
                  <label className="inline-flex items-center">
                    <input
                      type="radio"
                      className="form-radio"
                      name="riskLevel"
                      value="low"
                      checked={config.riskLevel === 'low'}
                      onChange={() => setConfig({ ...config, riskLevel: 'low' })}
                      disabled={isEnabled || isOffline}
                    />
                    <span className="ml-2">Low</span>
                  </label>
                  <label className="inline-flex items-center">
                    <input
                      type="radio"
                      className="form-radio"
                      name="riskLevel"
                      value="medium"
                      checked={config.riskLevel === 'medium'}
                      onChange={() => setConfig({ ...config, riskLevel: 'medium' })}
                      disabled={isEnabled || isOffline}
                    />
                    <span className="ml-2">Medium</span>
                  </label>
                  <label className="inline-flex items-center">
                    <input
                      type="radio"
                      className="form-radio"
                      name="riskLevel"
                      value="high"
                      checked={config.riskLevel === 'high'}
                      onChange={() => setConfig({ ...config, riskLevel: 'high' })}
                      disabled={isEnabled || isOffline}
                    />
                    <span className="ml-2">High</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
          
          {/* Strategy Selection */}
          <div>
            <h3 className="text-lg font-medium mb-2">Trading Strategies</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {availableStrategies.map((strategy) => (
                <label key={strategy.id} className="inline-flex items-center">
                  <input
                    type="checkbox"
                    className="form-checkbox"
                    checked={config.strategies.includes(strategy.id)}
                    onChange={() => handleStrategyChange(strategy.id)}
                    disabled={isEnabled || isOffline}
                  />
                  <span className="ml-2">{strategy.name}</span>
                </label>
              ))}
            </div>
          </div>
          
          {/* Market Selection */}
          <div>
            <h3 className="text-lg font-medium mb-2">Target Markets</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {targetSeries.map((series) => (
                <label key={series} className="inline-flex items-center">
                  <input
                    type="checkbox"
                    className="form-checkbox"
                    checked={config.marketSeries.includes(series)}
                    onChange={() => handleSeriesChange(series)}
                    disabled={isEnabled || isOffline}
                  />
                  <span className="ml-2">{series}</span>
                </label>
              ))}
            </div>
          </div>
          
          {/* Save Button */}
          <div className="flex justify-end">
            <button
              onClick={saveConfig}
              disabled={isEnabled || isOffline || isLoading}
              className="btn-primary disabled:opacity-50"
            >
              Save Configuration
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default YOLOTrading; 