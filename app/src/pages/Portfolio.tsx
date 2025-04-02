import React, { useState, useEffect } from 'react';
import { usePortfolio } from '../contexts/PortfolioContext';
import { useOffline } from '../contexts/OfflineContext';

const Portfolio: React.FC = () => {
  const { portfolioData, refreshPortfolio } = usePortfolio();
  const { isOffline } = useOffline();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [selectedPosition, setSelectedPosition] = useState<string | null>(null);

  // Refresh data on component mount
  useEffect(() => {
    const loadData = async () => {
      if (!isOffline && !portfolioData.isLoading) {
        setIsLoading(true);
        try {
          await refreshPortfolio();
        } catch (error) {
          console.error('Failed to load portfolio data:', error);
        }
        setIsLoading(false);
      }
    };

    loadData();
  }, [isOffline, refreshPortfolio, portfolioData.isLoading]);

  // Calculate total profit/loss
  const totalProfitLoss = portfolioData.positions.reduce(
    (total, position) => total + position.profit_loss,
    0
  );

  // Sort positions by profit/loss
  const sortedPositions = [...portfolioData.positions].sort(
    (a, b) => b.profit_loss - a.profit_loss
  );

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Portfolio</h1>
        <button
          onClick={() => refreshPortfolio()}
          disabled={isLoading || isOffline}
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
        >
          {isLoading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Portfolio Summary */}
      <div className="bg-card rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Summary</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Available Funds</p>
            <p className="text-2xl font-bold">${(portfolioData.balance.available_funds / 100).toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Total Value</p>
            <p className="text-2xl font-bold">${(portfolioData.balance.total_value / 100).toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Portfolio Value</p>
            <p className="text-2xl font-bold">${(portfolioData.balance.portfolio_value / 100).toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Total P/L</p>
            <p className={`text-2xl font-bold ${totalProfitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              ${(totalProfitLoss / 100).toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      {/* Positions Table */}
      <div className="bg-card rounded-lg shadow-md overflow-hidden">
        <h2 className="text-xl font-semibold p-6 pb-4">Positions</h2>
        
        {portfolioData.positions.length === 0 ? (
          <div className="p-6 text-center text-muted-foreground">
            No positions found. Start trading to see your positions here.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Market</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Position</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Avg. Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Current Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">P/L</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {sortedPositions.map((position) => (
                  <tr 
                    key={position.market_id}
                    className={`hover:bg-muted/30 cursor-pointer ${selectedPosition === position.market_id ? 'bg-muted/50' : ''}`}
                    onClick={() => setSelectedPosition(position.market_id === selectedPosition ? null : position.market_id)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {position.market_title}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {position.yes_count > 0 ? `${position.yes_count} YES` : `${position.no_count} NO`}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      ${(position.average_price / 100).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      ${(position.current_price / 100).toFixed(2)}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${position.profit_loss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      ${(position.profit_loss / 100).toFixed(2)} ({position.profit_loss_percentage.toFixed(2)}%)
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Position Details (when selected) */}
      {selectedPosition && (
        <div className="mt-6 bg-card rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Position Details</h2>
          {sortedPositions.filter(p => p.market_id === selectedPosition).map(position => (
            <div key={`detail-${position.market_id}`}>
              <h3 className="text-lg font-medium mb-2">{position.market_title}</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-sm text-muted-foreground">Position</p>
                  <p className="font-medium">
                    {position.yes_count > 0 ? `${position.yes_count} YES` : `${position.no_count} NO`}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Average Price</p>
                  <p className="font-medium">${(position.average_price / 100).toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Current Price</p>
                  <p className="font-medium">${(position.current_price / 100).toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">P/L</p>
                  <p className={`font-medium ${position.profit_loss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    ${(position.profit_loss / 100).toFixed(2)} ({position.profit_loss_percentage.toFixed(2)}%)
                  </p>
                </div>
              </div>
              <div className="flex space-x-2">
                <button className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 disabled:opacity-50" disabled={isOffline}>
                  Close Position
                </button>
                <button className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-secondary/90 disabled:opacity-50" disabled={isOffline}>
                  View Market
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Last updated info */}
      <div className="mt-6 text-sm text-muted-foreground">
        {isOffline ? (
          <p>Offline mode - showing cached data</p>
        ) : (
          <p>
            Last updated: {portfolioData.lastUpdated ? 
              new Date(portfolioData.lastUpdated).toLocaleString() : 
              'Never'}
          </p>
        )}
      </div>
    </div>
  );
};

export default Portfolio;
