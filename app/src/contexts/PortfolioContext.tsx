import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface PortfolioData {
  balance: {
    available_funds: number;
    total_value: number;
    portfolio_value: number;
  };
  positions: {
    market_id: string;
    market_title: string;
    yes_count: number;
    no_count: number;
    average_price: number;
    current_price: number;
    profit_loss: number;
    profit_loss_percentage: number;
  }[];
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

interface PortfolioContextType {
  portfolioData: PortfolioData;
  refreshPortfolio: () => Promise<void>;
  isOfflineMode: boolean;
}

const defaultPortfolioData: PortfolioData = {
  balance: {
    available_funds: 0,
    total_value: 0,
    portfolio_value: 0,
  },
  positions: [],
  isLoading: false,
  error: null,
  lastUpdated: null,
};

const PortfolioContext = createContext<PortfolioContextType | undefined>(undefined);

interface PortfolioProviderProps {
  children: ReactNode;
}

export const PortfolioProvider: React.FC<PortfolioProviderProps> = ({ children }) => {
  const [portfolioData, setPortfolioData] = useState<PortfolioData>(defaultPortfolioData);
  const [isOfflineMode, setIsOfflineMode] = useState<boolean>(false);

  // Check if we're in offline mode
  useEffect(() => {
    const checkOnlineStatus = () => {
      setIsOfflineMode(!navigator.onLine);
    };

    // Initial check
    checkOnlineStatus();

    // Add event listeners for online/offline status
    window.addEventListener('online', checkOnlineStatus);
    window.addEventListener('offline', checkOnlineStatus);

    // Check backend status
    const checkBackendStatus = async () => {
      try {
        const status = await window.electron.checkBackendStatus();
        setIsOfflineMode(status.status !== 'online');
      } catch (error) {
        setIsOfflineMode(true);
      }
    };

    checkBackendStatus();

    // Cleanup
    return () => {
      window.removeEventListener('online', checkOnlineStatus);
      window.removeEventListener('offline', checkOnlineStatus);
    };
  }, []);

  // Load cached portfolio data if available
  useEffect(() => {
    const cachedData = localStorage.getItem('portfolioData');
    if (cachedData) {
      try {
        const parsedData = JSON.parse(cachedData);
        // Convert lastUpdated string back to Date object
        if (parsedData.lastUpdated) {
          parsedData.lastUpdated = new Date(parsedData.lastUpdated);
        }
        setPortfolioData(parsedData);
      } catch (error) {
        console.error('Failed to parse cached portfolio data:', error);
      }
    }
  }, []);

  // Fetch portfolio data from API
  const refreshPortfolio = async () => {
    if (isOfflineMode) {
      setPortfolioData(prev => ({
        ...prev,
        error: 'Cannot refresh portfolio in offline mode',
      }));
      return;
    }

    setPortfolioData(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const data = await window.api.portfolio.getPortfolio();
      
      // Transform API data to our format
      const transformedData: PortfolioData = {
        balance: {
          available_funds: data.balance.available_funds || 0,
          total_value: data.balance.total_value || 0,
          portfolio_value: data.balance.portfolio_value || 0,
        },
        positions: data.positions.positions.map((position: any) => ({
          market_id: position.market_id,
          market_title: position.market_title || 'Unknown Market',
          yes_count: position.yes_count || 0,
          no_count: position.no_count || 0,
          average_price: position.average_price || 0,
          current_price: position.current_price || 0,
          profit_loss: position.profit_loss || 0,
          profit_loss_percentage: position.profit_loss_percentage || 0,
        })),
        isLoading: false,
        error: null,
        lastUpdated: new Date(),
      };

      setPortfolioData(transformedData);

      // Cache the data
      localStorage.setItem('portfolioData', JSON.stringify(transformedData));
    } catch (error) {
      console.error('Failed to fetch portfolio data:', error);
      setPortfolioData(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch portfolio data',
      }));
    }
  };

  // Initial fetch
  useEffect(() => {
    if (!isOfflineMode) {
      refreshPortfolio();
    }
  }, [isOfflineMode]);

  return (
    <PortfolioContext.Provider value={{ portfolioData, refreshPortfolio, isOfflineMode }}>
      {children}
    </PortfolioContext.Provider>
  );
};

// Custom hook to use the portfolio context
export const usePortfolio = (): PortfolioContextType => {
  const context = useContext(PortfolioContext);
  if (context === undefined) {
    throw new Error('usePortfolio must be used within a PortfolioProvider');
  }
  return context;
};
