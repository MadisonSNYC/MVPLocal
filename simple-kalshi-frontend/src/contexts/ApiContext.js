import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

// Create context
const ApiContext = createContext();

// API provider component
export const ApiProvider = ({ children }) => {
  const [backendUrl, setBackendUrl] = useState('http://127.0.0.1:5000') ;
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Initialize API client
  const apiClient = axios.create({
    baseURL: backendUrl,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Update backend URL from Electron store
  useEffect(() => {
    const getBackendUrl = async () => {
      try {
        const url = await window.api.getBackendUrl();
        if (url) {
          setBackendUrl(url);
        }
      } catch (error) {
        console.error('Failed to get backend URL:', error);
      }
    };

    getBackendUrl();
  }, []);

  // Check connection when backend URL changes
  useEffect(() => {
    const checkConnection = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await apiClient.get('/api/health');
        setIsConnected(response.data.status === 'ok');
      } catch (error) {
        setIsConnected(false);
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };

    checkConnection();
  }, [backendUrl, apiClient]);

  // Update backend URL
  const updateBackendUrl = async (url) => {
    try {
      await window.api.setBackendUrl(url);
      setBackendUrl(url);
      return true;
    } catch (error) {
      setError(error.message);
      return false;
    }
  };

  // Generic API request function
  const apiRequest = async (method, endpoint, data = null) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiClient({
        method,
        url: endpoint,
        data,
      });
      
      return response.data;
    } catch (error) {
      setError(error.message || 'An error occurred');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ApiContext.Provider value={{
      backendUrl,
      isConnected,
      isLoading,
      error,
      updateBackendUrl,
      apiRequest,
    }}>
      {children}
    </ApiContext.Provider>
  );
};

// Custom hook to use API context
export const useApi = () => {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
}; 