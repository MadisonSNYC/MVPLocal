import React, { useEffect, useState } from 'react';
import { useMarkets } from '../contexts/MarketsContext';
import { usePortfolio } from '../contexts/PortfolioContext';
import { useOffline } from '../contexts/OfflineContext';
import { useApi } from '../contexts/ApiContext';

const Dashboard = () => {
  const { filteredMarkets, isLoading: marketsLoading, refreshMarkets } = useMarkets();
  const { portfolio, isLoading: portfolioLoading, refreshPortfolio } = usePortfolio();
  const { isOffline, cachedData } = useOffline();
  const { isConnected } = useApi();
  const [recommendations, setRecommendations] = useState([]);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);

  // Fetch recommendations
  useEffect(() => {
    const fetchRecommendations = async () => {
      if (isOffline) {
        if (cachedData.recommendations) {
          setRecommendations(cachedData.recommendations);
        }
        return;
      }

      setIsLoadingRecommendations(true);
      
      try {
        const response = await fetch('http://127.0.0.1:3001/api/recommendations') ;
        const data = await response.json();
        setRecommendations(data);
      } catch (error) {
        console.error('Failed to fetch recommendations:', error);
        
        // Use cached data if available
        if (cachedData.recommendations) {
          setRecommendations(cachedData.recommendations);
        }
      } finally {
        setIsLoadingRecommendations(false);
      }
    };

    fetchRecommendations();
  }, [isConnected, isOffline, cachedData.recommendations]);

  // Refresh data
  const handleRefresh = () => {
    refreshMarkets();
    refreshPortfolio();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Dashboard</h1>
        <button 
          onClick={handleRefresh}
          disabled={isOffline}
          className="btn-primary disabled:opacity-50"
        >
          Refresh Data
        </button>
      </div>

      {/* Portfolio Summary */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Portfolio Summary</h2>
        {portfolioLoading ? (
          <p>Loading portfolio data...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 dark:bg-blue-900 p-4 rounded-lg">
              <p className="text-sm text-gray-500 dark:text-gray-400">Balance</p>
              <p className="text-2xl font-bold">${portfolio.balance.toFixed(2)}</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900 p-4 rounded-lg">
              <p className="text-sm text-gray-500 dark:text-gray-400">Open Positions</p>
              <p className="text-2xl font-bold">{portfolio.positions.length}</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900 p-4 rounded-lg">
              <p className="text-sm text-gray-500 dark:text-gray-400">Pending Orders</p>
              <p className="text-2xl font-bold">{portfolio.orders.length}</p>
            </div>
          </div>
        )}
      </div>

      {/* Market Overview */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Market Overview</h2>
        {marketsLoading ? (
          <p>Loading markets data...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Market</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Series</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Yes Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">No Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Volume</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                {filteredMarkets.slice(0, 5).map((market) => (
                  <tr key={market.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{market.title}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{market.series}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">${market.yes_price.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">${market.no_price.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">${market.volume.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Top Recommendations */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Top Recommendations</h2>
        {isLoadingRecommendations ? (
          <p>Loading recommendations...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.slice(0, 4).map((rec) => (
              <div key={rec.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">{rec.market_title}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{rec.series}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    rec.confidence > 0.7 ? 'bg-green-100 text-green-800' : 
                    rec.confidence > 0.4 ? 'bg-yellow-100 text-yellow-800' : 
                    'bg-red-100 text-red-800'
                  }`}>
                    {Math.round(rec.confidence * 100)}% Confidence
                  </span>
                </div>
                <div className="mt-2">
                  <p className="text-sm">
                    <span className="font-medium">Recommendation:</span> {rec.position_type} {rec.outcome}
                  </p>
                  <p className="text-sm">
                    <span className="font-medium">Strategy:</span> {rec.strategy}
                  </p>
                  <p className="text-sm">
                    <span className="font-medium">Price:</span> ${rec.price.toFixed(2)}
                  </p>
                </div>
                <div className="mt-3">
                  <button className="btn-primary text-sm py-1 px-3">Place Order</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 