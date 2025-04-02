import React, { createContext, useState, useContext, useEffect } from 'react';
import { useApi } from './ApiContext';

// Create context
const OfflineContext = createContext();

// Offline provider component
export const OfflineProvider = ({ children }) => {
  const { isConnected } = useApi();
  const [isOffline, setIsOffline] = useState(!isConnected);
  const [cachedData, setCachedData] = useState({
    markets: null,
    portfolio: null,
    recommendations: null,
    lastUpdated: null
  });

  // Update offline status when connection changes
  useEffect(() => {
    setIsOffline(!isConnected);
  }, [isConnected]);

  // Load cached data from localStorage on mount
  useEffect(() => {
    const loadCachedData = () => {
      try {
        const savedData = localStorage.getItem('cachedData');
        if (savedData) {
          setCachedData(JSON.parse(savedData));
        }
      } catch (error) {
        console.error('Failed to load cached data:', error);
      }
    };

    loadCachedData();
  }, []);

  // Save data to cache
  const cacheData = (key, data) => {
    setCachedData(prev => {
      const updated = {
        ...prev,
        [key]: data,
        lastUpdated: new Date().toISOString()
      };
      
      // Save to localStorage
      localStorage.setItem('cachedData', JSON.stringify(updated));
      
      return updated;
    });
  };

  // Clear cache
  const clearCache = () => {
    setCachedData({
      markets: null,
      portfolio: null,
      recommendations: null,
      lastUpdated: null
    });
    localStorage.removeItem('cachedData');
  };

  return (
    <OfflineContext.Provider value={{
      isOffline,
      cachedData,
      cacheData,
      clearCache
    }}>
      {children}
    </OfflineContext.Provider>
  );
};

// Custom hook to use offline context
export const useOffline = () => {
  const context = useContext(OfflineContext);
  if (context === undefined) {
    throw new Error('useOffline must be used within an OfflineProvider');
  }
  return context;
}; 