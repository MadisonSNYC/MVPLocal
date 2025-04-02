import React, { useState, useEffect } from 'react';
import { usePortfolio } from '../contexts/PortfolioContext';
import { useMarkets } from '../contexts/MarketsContext';
import { useOffline } from '../contexts/OfflineContext';

const Dashboard: React.FC = () => {
  const { portfolioData, refreshPortfolio } = usePortfolio();
  const { marketsData, refreshMarkets } = useMarkets();
  const { isOffline } = useOffline();
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Refresh data on component mount
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      if (!isOffline) {
        try {
          await Promise.all([refreshPortfolio(), refreshMarkets()]);
        } catch (error) {
          console.error('Failed to load dashboard data:', error);
        }
      }
      setIsLoading(false);
    };

    loadData();
  }, [isOffline, refreshPortfolio, refreshMarkets]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Portfolio Summary Card */}
          <div className="bg-card rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Portfolio Summary</h2>
            <div className="grid grid-cols-2 gap-4">
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
                <p className="text-sm text-muted-foreground">Active Positions</p>
                <p className="text-2xl font-bold">{portfolioData.positions.length}</p>
              </div>
            </div>
            <div className="mt-4">
              <a href="/portfolio" className="text-primary text-sm hover:underline">View Portfolio →</a>
            </div>
          </div>
          
          {/* Active Markets Card */}
          <div className="bg-card rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Active Markets</h2>
            <div className="space-y-4">
              {marketsData.markets.slice(0, 5).map((market) => (
                <div key={market.id} className="flex justify-between items-center border-b border-border pb-2">
                  <div>
                    <p className="font-medium">{market.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(market.close_time).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">
                      YES: ${(market.yes_ask / 100).toFixed(2)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Volume: ${(market.volume_24h / 100).toFixed(2)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <a href="/markets" className="text-primary text-sm hover:underline">View All Markets →</a>
            </div>
          </div>
          
          {/* AI Recommendations Card */}
          <div className="bg-card rounded-lg shadow-md p-6 md:col-span-2">
            <h2 className="text-xl font-semibold mb-4">AI Trade Recommendations</h2>
            <div className="bg-accent/20 rounded-lg p-4 mb-4">
              <p className="text-sm">
                Get personalized trade recommendations based on market data and your selected strategy.
                Choose between Momentum and Mean-Reversion strategies to match your trading style.
              </p>
            </div>
            <div className="flex justify-between items-center">
              <div>
                <a href="/strategies" className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90">
                  View Recommendations
                </a>
              </div>
              <div className="flex items-center">
                <span className="text-sm text-muted-foreground mr-2">Strategies:</span>
                <span className="bg-accent/30 text-accent-foreground px-2 py-1 rounded text-xs mr-1">Momentum</span>
                <span className="bg-accent/30 text-accent-foreground px-2 py-1 rounded text-xs">Mean-Reversion</span>
              </div>
            </div>
          </div>
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

export default Dashboard;
