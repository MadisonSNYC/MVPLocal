import React, { useState, useEffect } from 'react';
import { useOffline } from '../contexts/OfflineContext';

interface PerformanceMetrics {
  strategy: string;
  win_count: number;
  loss_count: number;
  open_count: number;
  win_rate: number;
  avg_profit: number;
  avg_loss: number;
  total_profit_loss: number;
  accuracy: number;
  last_updated: number;
}

interface PerformanceSummary {
  total_recommendations: number;
  total_wins: number;
  total_losses: number;
  total_open: number;
  win_rate: number;
  total_profit_loss: number;
  last_updated: number;
}

interface Recommendation {
  id: string;
  market_id: string;
  strategy: string;
  action: string;
  entry_price: number;
  target_exit: number;
  stop_loss: number;
  confidence: string;
  timestamp: number;
  status: string;
  exit_price: number | null;
  exit_timestamp: number | null;
  result: string | null;
  profit_loss: number | null;
  notes: string;
}

const PerformanceTracking: React.FC = () => {
  const { isOffline } = useOffline();
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [strategyPerformance, setStrategyPerformance] = useState<PerformanceMetrics[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('all');
  const [selectedStrategy, setSelectedStrategy] = useState<string | null>(null);
  const [timeframePerformance, setTimeframePerformance] = useState<any>(null);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  // Fetch performance summary
  useEffect(() => {
    const fetchPerformanceData = async () => {
      if (isOffline) {
        setIsLoading(false);
        return;
      }
      
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch summary
        const summaryResponse = await window.api.fetch('/api/performance/summary');
        setSummary(summaryResponse);
        
        // Fetch strategy performance
        const strategyResponse = await window.api.fetch('/api/performance/strategies');
        setStrategyPerformance(strategyResponse.strategies || []);
        
        // Fetch recommendations
        const recommendationsResponse = await window.api.fetch('/api/performance/recommendations?limit=50');
        setRecommendations(recommendationsResponse.recommendations || []);
        
      } catch (error) {
        console.error('Failed to fetch performance data:', error);
        setError('Failed to fetch performance data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchPerformanceData();
  }, [isOffline]);

  // Fetch timeframe performance when timeframe or strategy changes
  useEffect(() => {
    const fetchTimeframePerformance = async () => {
      if (isOffline) {
        return;
      }
      
      try {
        const url = `/api/performance/timeframe?timeframe=${selectedTimeframe}${selectedStrategy ? `&strategy=${selectedStrategy}` : ''}`;
        const response = await window.api.fetch(url);
        setTimeframePerformance(response);
      } catch (error) {
        console.error('Failed to fetch timeframe performance:', error);
      }
    };

    if (selectedTimeframe) {
      fetchTimeframePerformance();
    }
  }, [selectedTimeframe, selectedStrategy, isOffline]);

  // Simulate historical data
  const simulateHistoricalData = async () => {
    if (isOffline) {
      setError('Cannot simulate data in offline mode');
      return;
    }
    
    try {
      setIsSimulating(true);
      setError(null);
      
      await window.api.fetch('/api/performance/simulate', {
        method: 'POST',
        body: JSON.stringify({ num_recommendations: 50 }),
        headers: { 'Content-Type': 'application/json' }
      });
      
      // Refresh data
      window.location.reload();
    } catch (error) {
      console.error('Failed to simulate historical data:', error);
      setError('Failed to simulate historical data. Please try again.');
    } finally {
      setIsSimulating(false);
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp: number): string => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  };

  // Format currency
  const formatCurrency = (value: number | null): string => {
    if (value === null) return 'N/A';
    return `$${value.toFixed(2)}`;
  };

  // Format percentage
  const formatPercentage = (value: number): string => {
    return `${value.toFixed(1)}%`;
  };

  // Get status badge color
  const getStatusBadgeColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open':
        return 'bg-blue-100 text-blue-800';
      case 'closed':
        return 'bg-green-100 text-green-800';
      case 'expired':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get result badge color
  const getResultBadgeColor = (result: string | null) => {
    if (!result) return 'bg-gray-100 text-gray-800';
    
    switch (result.toLowerCase()) {
      case 'win':
        return 'bg-green-100 text-green-800';
      case 'loss':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get profit/loss color
  const getProfitLossColor = (value: number | null) => {
    if (value === null) return 'text-gray-500';
    return value >= 0 ? 'text-green-600' : 'text-red-600';
  };

  // Render performance summary
  const renderSummary = () => {
    if (!summary) return null;
    
    return (
      <div className="bg-card rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Performance Summary</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm text-muted-foreground">Total Recommendations</p>
            <p className="text-2xl font-bold">{summary.total_recommendations}</p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground">Win Rate</p>
            <p className="text-2xl font-bold text-green-600">{formatPercentage(summary.win_rate)}</p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground">Total Profit/Loss</p>
            <p className={`text-2xl font-bold ${getProfitLossColor(summary.total_profit_loss)}`}>
              {formatCurrency(summary.total_profit_loss)}
            </p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground">Wins</p>
            <p className="text-2xl font-bold text-green-600">{summary.total_wins}</p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground">Losses</p>
            <p className="text-2xl font-bold text-red-600">{summary.total_losses}</p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground">Open Positions</p>
            <p className="text-2xl font-bold text-blue-600">{summary.total_open}</p>
          </div>
        </div>
        
        <p className="mt-4 text-sm text-muted-foreground">
          Last updated: {formatTimestamp(summary.last_updated)}
        </p>
      </div>
    );
  };

  // Render strategy performance
  const renderStrategyPerformance = () => {
    if (!strategyPerformance.length) return null;
    
    return (
      <div className="bg-card rounded-lg shadow-md overflow-hidden mb-6">
        <div className="p-4 bg-muted/50 border-b border-border">
          <h2 className="text-lg font-medium">Strategy Performance</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/30">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">Strategy</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Win Rate</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Accuracy</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Wins</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Losses</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Open</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Avg Profit</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Avg Loss</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Total P/L</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {strategyPerformance.map((strategy) => (
                <tr 
                  key={strategy.strategy} 
                  className="hover:bg-muted/30 cursor-pointer"
                  onClick={() => setSelectedStrategy(strategy.strategy === selectedStrategy ? null : strategy.strategy)}
                >
                  <td className="px-4 py-3 text-sm font-medium">
                    {strategy.strategy.charAt(0).toUpperCase() + strategy.strategy.slice(1)}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span className={strategy.win_rate >= 50 ? 'text-green-600' : 'text-red-600'}>
                      {formatPercentage(strategy.win_rate)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {formatPercentage(strategy.accuracy)}
                  </td>
                  <td className="px-4 py-3 text-sm text-green-600">
                    {strategy.win_count}
                  </td>
                  <td className="px-4 py-3 text-sm text-red-600">
                    {strategy.loss_count}
                  </td>
                  <td className="px-4 py-3 text-sm text-blue-600">
                    {strategy.open_count}
                  </td>
                  <td className="px-4 py-3 text-sm text-green-600">
                    {formatCurrency(strategy.avg_profit)}
                  </td>
                  <td className="px-4 py-3 text-sm text-red-600">
                    {formatCurrency(strategy.avg_loss)}
                  </td>
                  <td className={`px-4 py-3 text-sm ${getProfitLossColor(strategy.total_profit_loss)}`}>
                    {formatCurrency(strategy.total_profit_loss)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  // Render timeframe performance
  const renderTimeframePerformance = () => {
    if (!timeframePerformance) return null;
    
    return (
      <div className="bg-card rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Performance by Timeframe</h2>
          
          <div className="flex space-x-2">
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="px-3 py-2 bg-background border border-input rounded-md text-sm"
            >
              <option value="all">All Time</option>
              <option value="day">Last 24 Hours</option>
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
            </select>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <p className="text-sm text-muted-foreground">Win Rate</p>
            <p className={`text-2xl font-bold ${timeframePerformance.win_rate >= 50 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercentage(timeframePerformance.win_rate)}
            </p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground">Total Profit/Loss</p>
            <p className={`text-2xl font-bold ${getProfitLossColor(timeframePerformance.total_profit_loss)}`}>
              {formatCurrency(timeframePerformance.total_profit_loss)}
            </p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground">Recommendations</p>
            <p className="text-2xl font-bold">{timeframePerformance.recommendation_count}</p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground">Win/Loss Ratio</p>
            <p className="text-2xl font-bold">
              {timeframePerformance.win_count}:{timeframePerformance.loss_count}
            </p>
          </div>
        </div>
        
        <p className="mt-4 text-sm text-muted-foreground">
          Showing data for: {selectedStrategy ? `${selectedStrategy.charAt(0).toUpperCase() + selectedStrategy.slice(1)} strategy` : 'All strategies'}
        </p>
      </div>
    );
  };

  // Render recommendations
  const renderRecommendations = () => {
    if (!recommendations.length) return null;
    
    return (
      <div className="bg-card rounded-lg shadow-md overflow-hidden">
        <div className="p-4 bg-muted/50 border-b border-border flex justify-between items-center">
          <h2 className="text-lg font-medium">Recent Recommendations</h2>
          
          <button
            onClick={simulateHistoricalData}
            disabled={isSimulating || isOffline}
            className="bg-primary text-primary-foreground px-3 py-1 rounded-md text-sm font-medium hover:bg-primary/90 disabled:opacity-50 flex items-center"
          >
            {isSimulating ? (
              <>
                <span className="inline-block animate-spin rounded-full h-3 w-3 border-2 border-current border-r-transparent mr-1"></span>
                Simulating...
              </>
            ) : (
              'Simulate Data'
            )}
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/30">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">Strategy</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Action</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Entry Price</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Exit Price</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Result</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Profit/Loss</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {recommendations.map((rec) => (
                <tr key={rec.id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 text-sm font-medium">
                    {rec.strategy.charAt(0).toUpperCase() + rec.strategy.slice(1)}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      rec.action === 'YES' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {rec.action}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {rec.entry_price}¢
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {rec.exit_price ? `${rec.exit_price}¢` : 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(rec.status)}`}>
                      {rec.status.charAt(0).toUpperCase() + rec.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {rec.result ? (
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getResultBadgeColor(rec.result)}`}>
                        {rec.result.charAt(0).toUpperCase() + rec.result.slice(1)}
                      </span>
                    ) : 'N/A'}
                  </td>
                  <td className={`px-4 py-3 text-sm ${getProfitLossColor(rec.profit_loss)}`}>
                    {rec.profit_loss !== null ? `${rec.profit_loss > 0 ? '+' : ''}${rec.profit_loss.toFixed(2)}¢` : 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {formatTimestamp(rec.timestamp)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Performance Tracking</h1>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md mb-4">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary border-r-transparent"></div>
          <p className="mt-2 text-muted-foreground">Loading performance data...</p>
        </div>
      )}

      {/* Content */}
      {!isLoading && (
        <>
          {renderSummary()}
          {renderTimeframePerformance()}
          {renderStrategyPerformance()}
          {renderRecommendations()}
        </>
      )}
    </div>
  );
};

export default PerformanceTracking;
