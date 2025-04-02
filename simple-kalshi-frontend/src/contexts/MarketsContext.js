import React, { createContext, useState, useContext, useEffect } from 'react';
import { useApi } from './ApiContext';
import { useOffline } from './OfflineContext';

// Create context
const MarketsContext = createContext();

// Markets provider component
export const MarketsProvider = ({ children }) => {
  const { apiRequest, isConnected } = useApi();
  const { isOffline, cachedData, cacheData } = useOffline();
  const [markets, setMarkets] = useState([]);
  const [filteredMarkets, setFilteredMarkets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState({
    series: [],
    search: '',
    timeframe: 'hourly'
  });

  // Target market series for the MVP
  const targetSeries = [
    'KXNASDAQ100U', // Nasdaq (Hourly)
    'KXINXU',       // S&P 500 (Hourly)
    'KXETHD',       // Ethereum Price (Hourly)
    'KXETH',        // Ethereum Price Range (Hourly)
    'KXBTCD',       // Bitcoin Price (Hourly)
    'KXBTC'         // Bitcoin Price Range (Hourly)
  ];

  // Fetch markets data
  const fetchMarkets = async () => {
    // If offline, use cached data
    if (isOffline) {
      if (cachedData.markets) {
        setMarkets(cachedData.markets);
        applyFilters(cachedData.markets);
      }
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await apiRequest('get', '/api/markets');
      setMarkets(data);
      
      // Cache the data for offline use
      cacheData('markets', data);
      
      // Apply filters
      applyFilters(data);
    } catch (error) {
      setError(error.message || 'Failed to fetch markets');
      
      // If we have cached data, use it as fallback
      if (cachedData.markets) {
        setMarkets(cachedData.markets);
        applyFilters(cachedData.markets);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Apply filters to markets
  const applyFilters = (marketsData) => {
    let filtered = [...marketsData];
    
    // Filter by series
    if (filter.series.length > 0) {
      filtered = filtered.filter(market => filter.series.includes(market.series));
    } else {
      // Default to target series for MVP
      filtered = filtered.filter(market => targetSeries.includes(market.series));
    }
    
    // Filter by search term
    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      filtered = filtered.filter(market => 
        market.title.toLowerCase().includes(searchLower) ||
        market.ticker.toLowerCase().includes(searchLower) ||
        market.series.toLowerCase().includes(searchLower)
      );
    }
    
    // Filter by timeframe
    if (filter.timeframe === 'hourly') {
      filtered = filtered.filter(market => market.timeframe === 'hourly');
    } else if (filter.timeframe === 'daily') {
      filtered = filtered.filter(market => market.timeframe === 'daily');
    }
    
    setFilteredMarkets(filtered);
  };

  // Update filters
  const updateFilter = (newFilter) => {
    setFilter(prev => {
      const updated = { ...prev, ...newFilter };
      applyFilters(markets);
      return updated;
    });
  };

  // Fetch markets on mount and when connection status changes
  useEffect(() => {
    fetchMarkets();
  }, [isConnected]);

  // Apply filters when markets or filter changes
  useEffect(() => {
    applyFilters(markets);
  }, [markets, filter]);

  return (
    <MarketsContext.Provider value={{
      markets,
      filteredMarkets,
      isLoading,
      error,
      filter,
      updateFilter,
      refreshMarkets: fetchMarkets,
      targetSeries
    }}>
      {children}
    </MarketsContext.Provider>
  );
};

// Custom hook to use markets context
export const useMarkets = () => {
  const context = useContext(MarketsContext);
  if (context === undefined) {
    throw new Error('useMarkets must be used within a MarketsProvider');
  }
  return context;
}; 