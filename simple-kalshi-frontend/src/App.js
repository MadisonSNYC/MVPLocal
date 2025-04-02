import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Portfolio from './pages/Portfolio';
import Strategies from './pages/Strategies';
import YOLOTrading from './pages/YOLOTrading';
import SocialFeed from './pages/SocialFeed';
import PerformanceTracking from './pages/PerformanceTracking';
import Settings from './pages/Settings';
import { ThemeProvider } from './contexts/ThemeContext';
import { ApiProvider } from './contexts/ApiContext';
import { OfflineProvider } from './contexts/OfflineContext';
import { MarketsProvider } from './contexts/MarketsContext';
import { PortfolioProvider } from './contexts/PortfolioContext';
import ConnectionStatus from './components/ConnectionStatus';

function App() {
  const [backendConnected, setBackendConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Check backend connection on startup
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const status = await window.api.checkBackendConnection();
        setBackendConnected(status.connected);
        setConnectionError(status.error);
      } catch (error) {
        setBackendConnected(false);
        setConnectionError(error.message);
      }
    };

    checkBackend();

    // Listen for backend status changes
    const unsubscribe = window.api.onBackendStatusChange((status) => {
      setBackendConnected(status.connected);
      setConnectionError(status.error);
    });

    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, []);

  // Redirect to settings if backend is not connected
  useEffect(() => {
    if (!backendConnected && location.pathname !== '/settings') {
      navigate('/settings', { state: { connectionError } });
    }
  }, [backendConnected, connectionError, navigate, location.pathname]);

  return (
    <ThemeProvider>
      <ApiProvider>
        <OfflineProvider>
          <MarketsProvider>
            <PortfolioProvider>
              <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
                <Sidebar />
                <div className="flex flex-col flex-1 overflow-hidden">
                  <Header />
                  <ConnectionStatus connected={backendConnected} error={connectionError} />
                  <main className="flex-1 overflow-y-auto p-4">
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/portfolio" element={<Portfolio />} />
                      <Route path="/strategies" element={<Strategies />} />
                      <Route path="/yolo" element={<YOLOTrading />} />
                      <Route path="/social" element={<SocialFeed />} />
                      <Route path="/performance" element={<PerformanceTracking />} />
                      <Route path="/settings" element={<Settings />} />
                    </Routes>
                  </main>
                </div>
              </div>
            </PortfolioProvider>
          </MarketsProvider>
        </OfflineProvider>
      </ApiProvider>
    </ThemeProvider>
  );
}

export default App; 