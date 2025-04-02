// Preload script for Electron
// This script runs in a privileged context and can access Node.js APIs
// It exposes a limited set of functionality to the renderer process

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'electron',
  {
    getAppInfo: () => ipcRenderer.invoke('get-app-info'),
    checkBackendStatus: () => ipcRenderer.invoke('check-backend-status')
  }
);

// Expose API for communicating with the backend
contextBridge.exposeInMainWorld(
  'api',
  {
    // Base URL for the backend API
    baseUrl: 'http://localhost:5000',
    
    // Generic fetch wrapper for API calls
    async fetch(endpoint, options = {}) {
      try {
        const url = `http://localhost:5000${endpoint}`;
        const response = await fetch(url, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {})
          }
        });
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `API error: ${response.status}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error(`API error (${endpoint}):`, error);
        throw error;
      }
    },
    
    // Portfolio endpoints
    portfolio: {
      getPortfolio: () => window.api.fetch('/api/portfolio'),
      getBalance: () => window.api.fetch('/api/portfolio/balance'),
      getPositions: (marketId) => window.api.fetch(`/api/portfolio/positions${marketId ? `?market_id=${marketId}` : ''}`),
      getFills: (limit = 100, cursor) => window.api.fetch(`/api/portfolio/fills?limit=${limit}${cursor ? `&cursor=${cursor}` : ''}`)
    },
    
    // Market data endpoints
    markets: {
      getMarkets: (status, limit = 100, cursor) => {
        let url = `/api/markets?limit=${limit}`;
        if (status) url += `&status=${status}`;
        if (cursor) url += `&cursor=${cursor}`;
        return window.api.fetch(url);
      },
      getMarket: (marketId) => window.api.fetch(`/api/markets/${marketId}`)
    },
    
    // Trading endpoints
    orders: {
      createOrder: (orderData) => window.api.fetch('/api/orders', {
        method: 'POST',
        body: JSON.stringify(orderData)
      }),
      getOrders: (marketId, status, limit = 100, cursor) => {
        let url = `/api/orders?limit=${limit}`;
        if (marketId) url += `&market_id=${marketId}`;
        if (status) url += `&status=${status}`;
        if (cursor) url += `&cursor=${cursor}`;
        return window.api.fetch(url);
      },
      getOrder: (orderId) => window.api.fetch(`/api/orders/${orderId}`),
      cancelOrder: (orderId) => window.api.fetch(`/api/orders/${orderId}`, {
        method: 'DELETE'
      })
    },
    
    // Exchange information endpoints
    exchange: {
      getStatus: () => window.api.fetch('/api/exchange/status')
    },
    
    // AI recommendation endpoints
    recommendations: {
      getRecommendations: (strategy, maxRecommendations = 5, riskLevel = 'medium', forceRefresh = false) => {
        let url = `/api/recommendations?strategy=${strategy}&max_recommendations=${maxRecommendations}&risk_level=${riskLevel}`;
        if (forceRefresh) url += '&force_refresh=true';
        return window.api.fetch(url);
      },
      getStrategies: () => window.api.fetch('/api/recommendations/strategies')
    }
  }
);
