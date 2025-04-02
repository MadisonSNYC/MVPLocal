import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface MarketsData {
  markets: {
    id: string;
    ticker: string;
    title: string;
    subtitle: string;
    yes_bid: number;
    yes_ask: number;
    no_bid: number;
    no_ask: number;
    last_price: number;
    close_time: string;
    volume_24h: number;
  }[];
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

interface MarketsContextType {
  marketsData: MarketsData;
  refreshMarkets: () => Promise<void>;
  getMarketDetails: (marketId: string) => Promise<any>;
  isOfflineMode: boolean;
}

const defaultMarketsData: MarketsData = {
  markets: [],
  isLoading: false,
  error: null,
  lastUpdated: null,
};

const MarketsContext = createContext<MarketsContextType | undefined>(undefined);

interface MarketsProviderProps {
  children: ReactNode;
}

export const MarketsProvider: React.FC<MarketsProviderProps> = ({ children }) => {
  const [marketsData, setMarketsData] = useState<MarketsData>(defaultMarketsData);
  const [isOfflineMode, setIsOfflineMode] = useState<boolean>(false);
  const [marketDetailsCache, setMarketDetailsCache] = useState<Record<string, any>>({});

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

  // Load cached markets data if available
  useEffect(() => {
    const cachedData = localStorage.getItem('marketsData');
    if (cachedData) {
      try {
        const parsedData = JSON.parse(cachedData);
        // Convert lastUpdated string back to Date object
        if (parsedData.lastUpdated) {
          parsedData.lastUpdated = new Date(parsedData.lastUpdated);
        }
        setMarketsData(parsedData);
      } catch (error) {
        console.error('Failed to parse cached markets data:', error);
      }
    }

    // Load cached market details
    const cachedDetails = localStorage.getItem('marketDetailsCache');
    if (cachedDetails) {
      try {
        setMarketDetailsCache(JSON.parse(cachedDetails));
      } catch (error) {
        console.error('Failed to parse cached market details:', error);
      }
    }
  }, []);

  // Fetch markets data from API
  const refreshMarkets = async () => {
    if (isOfflineMode) {
      setMarketsData(prev => ({
        ...prev,
        error: 'Cannot refresh markets in offline mode',
      }));
      return;
    }

    setMarketsData(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const data = await window.api.markets.getMarkets('active', 100);
      
      // Transform API data to our format
      const transformedData: MarketsData = {
        markets: data.markets.map((market: any) => ({
          id: market.id,
          ticker: market.ticker || '',
          title: market.title || 'Unknown Market',
          subtitle: market.subtitle || '',
          yes_bid: market.yes_bid || 0,
          yes_ask: market.yes_ask || 0,
          no_bid: market.no_bid || 0,
          no_ask: market.no_ask || 0,
          last_price: market.last_price || 0,
          close_time: market.close_time || '',
          volume_24h: market.volume_24h || 0,
        })),
        isLoading: false,
        error: null,
        lastUpdated: new Date(),
      };

      setMarketsData(transformedData);

      // Cache the data
      localStorage.setItem('marketsData', JSON.stringify(transformedData));
    } catch (error) {
      console.error('Failed to fetch markets data:', error);
      setMarketsData(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch markets data',
      }));
    }
  };

  // Get details for a specific market
  const getMarketDetails = async (marketId: string) => {
    // Check cache first
    if (marketDetailsCache[marketId]) {
      return marketDetailsCache[marketId];
    }

    if (isOfflineMode) {
      throw new Error('Cannot fetch market details in offline mode');
    }

    try {
      const details = await window.api.markets.getMarket(marketId);
      
      // Update cache
      const updatedCache = { ...marketDetailsCache, [marketId]: details };
      setMarketDetailsCache(updatedCache);
      
      // Save to localStorage
      localStorage.setItem('marketDetailsCache', JSON.stringify(updatedCache));
      
      return details;
    } catch (error) {
      console.error(`Failed to fetch details for market ${marketId}:`, error);
      throw error;
    }
  };

  // Initial fetch
  useEffect(() => {
    if (!isOfflineMode) {
      refreshMarkets();
    }
  }, [isOfflineMode]);

  return (
    <MarketsContext.Provider value={{ marketsData, refreshMarkets, getMarketDetails, isOfflineMode }}>
      {children}
    </MarketsContext.Provider>
  );
};

// Custom hook to use the markets context
export const useMarkets = (): MarketsContextType => {
  const context = useContext(MarketsContext);
  if (context === undefined) {
    throw new Error('useMarkets must be used within a MarketsProvider');
  }
  return context;
};
