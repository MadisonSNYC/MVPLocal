import React, { createContext, useState, useContext, useEffect } from 'react';
import { useApi } from './ApiContext';
import { useOffline } from './OfflineContext';

// Create context
const PortfolioContext = createContext();

// Portfolio provider component
export const PortfolioProvider = ({ children }) => {
  const { apiRequest, isConnected } = useApi();
  const { isOffline, cachedData, cacheData } = useOffline();
  const [portfolio, setPortfolio] = useState({
    balance: 0,
    positions: [],
    orders: [],
    history: []
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch portfolio data
  const fetchPortfolio = async () => {
    // If offline, use cached data
    if (isOffline) {
      if (cachedData.portfolio) {
        setPortfolio(cachedData.portfolio);
      }
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await apiRequest('get', '/api/portfolio');
      setPortfolio(data);
      
      // Cache the data for offline use
      cacheData('portfolio', data);
    } catch (error) {
      setError(error.message || 'Failed to fetch portfolio');
      
      // If we have cached data, use it as fallback
      if (cachedData.portfolio) {
        setPortfolio(cachedData.portfolio);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Place an order
  const placeOrder = async (order) => {
    if (isOffline) {
      setError('Cannot place orders while offline');
      return null;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await apiRequest('post', '/api/orders', order);
      
      // Refresh portfolio to get updated positions and orders
      await fetchPortfolio();
      
      return result;
    } catch (error) {
      setError(error.message || 'Failed to place order');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // Cancel an order
  const cancelOrder = async (orderId) => {
    if (isOffline) {
      setError('Cannot cancel orders while offline');
      return false;
    }

    setIsLoading(true);
    setError(null);

    try {
      await apiRequest('delete', `/api/orders/${orderId}`);
      
      // Refresh portfolio to get updated orders
      await fetchPortfolio();
      
      return true;
    } catch (error) {
      setError(error.message || 'Failed to cancel order');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch portfolio on mount and when connection status changes
  useEffect(() => {
    fetchPortfolio();
  }, [isConnected]);

  return (
    <PortfolioContext.Provider value={{
      portfolio,
      isLoading,
      error,
      refreshPortfolio: fetchPortfolio,
      placeOrder,
      cancelOrder
    }}>
      {children}
    </PortfolioContext.Provider>
  );
};

// Custom hook to use portfolio context
export const usePortfolio = () => {
  const context = useContext(PortfolioContext);
  if (context === undefined) {
    throw new Error('usePortfolio must be used within a PortfolioProvider');
  }
  return context;
}; 