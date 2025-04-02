import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';
import { useOffline } from '../contexts/OfflineContext';

const PerformanceTracking = () => {
  const { apiRequest, isConnected } = useApi();
  const { isOffline, cachedData, cacheData } = useOffline();
  
  const [performanceData, setPerformanceData] = useState({
    summary: {
      totalTrades: 0,
      winRate: 0,
      profitLoss: 0,
      averageReturn: 0
    },
    strategyPerformance: [],
    recommendations: []
  });
  const [timeframe, setTimeframe] = useState('all');
  const [strategyFilter, setStrategyFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch performance data
  useEffect(() => {
    const fetchPerformanceData = async () => {
      if (isOffline) {
        if (cachedData.performance) {
          setPerformanceData(cachedData.performance);
        }
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const data = await apiRequest('get', `/api/performance?timeframe=${timeframe}&strategy=${strategyFilter}`);
        setPerformanceData(data);
        cacheData('performance', data);
      } catch (error) {
        setError('Failed to fetch performance data');
        if (cachedData.performance) {
          setPerformanceData(cachedData.performance);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchPerformanceData();
  }, [timeframe, strategyFilter, isConnected, isOffline]);

  // Format currency
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  // Format percentage
  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'win':
        return 'text-green-600';
      case 'loss':
        return 'text-red-600';
      case 'open':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Performance Tracking</h1>
        {isOffline && (
          <span className="px-2 py-1 text-xs font-medium rounded-md bg-yellow-100 text-yellow-800">
            Offline Mode - Showing Cached Data
          </span>
        )}
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col md:flex-row md:justify-between md:items-center space-y-4 md:space-y-0">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Timeframe
            </label>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="input-field"
              disabled={isLoading}
            >
              <option value="all">All Time</option>
              <option value="day">Last 24 Hours</option>
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Strategy
            </label>
            <select
              value={strategyFilter}
              onChange={(e) => setStrategyFilter(e.target.value)}
              className="input-field"
              disabled={isLoading}
            >
              <option value="all">All Strategies</option>
              <option value="momentum">Momentum</option>
              <option value="mean-reversion">Mean Reversion</option>
              <option value="arbitrage">Arbitrage</option>
              <option value="volatility">Volatility-Based</option>
              <option value="sentiment">Sentiment-Driven</option>
            </select>
          </div>
        </div>
      </div>

      {/* Performance Summary */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Performance Summary</h2>
        
        {isLoading ? (
          <p>Loading performance data...</p>
        ) : error ? (
          <p className="text-red-500">{error}</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg">
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Trades</p>
              <p className="text-2xl font-bold">{performanceData.summary.totalTrades}</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900 p-4 rounded-lg">
              <p className="text-sm text-gray-500 dark:text-gray-400">Win Rate</p>
              <p className="text-2xl font-bold">{formatPercentage(performanceData.summary.winRate)}</p>
            </div>
            <div className={`${performanceData.summary.profitLoss >= 0 ? 'bg-green-50 dark:bg-green-900' : 'bg-red-50 dark:bg-red-900'} p-4 rounded-lg`}>
              <p className="text-sm text-gray-500 dark:text-gray-400">Profit/Loss</p>
              <p className={`text-2xl font-bold ${performanceData.summary.profitLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(performanceData.summary.profitLoss)}
              </p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900 p-4 rounded-lg">
              <p className="text-sm text-gray-500 dark:text-gray-400">Average Return</p>
              <p className="text-2xl font-bold">{formatPercentage(performanceData.summary.averageReturn)}</p>
            </div>
          </div>
        )}
      </div>

      {/* Strategy Performance */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Strategy Performance</h2>
        
        {isLoading ? (
          <p>Loading strategy performance...</p>
        ) : error ? (
          <p className="text-red-500">{error}</p>
        ) : performanceData.strategyPerformance.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400">No strategy performance data available.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Strategy
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Trades
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Win Rate
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Profit/Loss
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Avg. Return
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                {performanceData.strategyPerformance.map((strategy) => (
                  <tr key={strategy.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {strategy.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {strategy.trades}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatPercentage(strategy.winRate)}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${strategy.profitLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(strategy.profitLoss)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatPercentage(strategy.averageReturn)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recommendation History */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Recommendation History</h2>
        
        {isLoading ? (
          <p>Loading recommendation history...</p>
        ) : error ? (
          <p className="text-red-500">{error}</p>
        ) : performanceData.recommendations.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400">No recommendation history available.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Date
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Market
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Strategy
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Position
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Entry
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Exit
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    P/L
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                {performanceData.recommendations.map((rec) => (
                  <tr key={rec.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(rec.timestamp).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {rec.market}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {rec.strategy}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {rec.position_type} {rec.outcome}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      ${rec.entry_price.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {rec.exit_price ? `$${rec.exit_price.toFixed(2)}` : '-'}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${rec.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {rec.profit_loss ? formatCurrency(rec.profit_loss) : '-'}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getStatusColor(rec.status)}`}>
                      {rec.status.charAt(0).toUpperCase() + rec.status.slice(1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default PerformanceTracking; 