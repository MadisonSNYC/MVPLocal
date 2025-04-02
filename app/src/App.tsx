import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { PortfolioProvider } from './contexts/PortfolioContext';
import { MarketsProvider } from './contexts/MarketsContext';
import { OfflineProvider } from './contexts/OfflineContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Portfolio from './pages/Portfolio';
import Strategies from './pages/Strategies';
import SocialFeed from './pages/SocialFeed';
import PerformanceTracking from './pages/PerformanceTracking';
import YOLOTrading from './pages/YOLOTrading';

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <OfflineProvider>
        <PortfolioProvider>
          <MarketsProvider>
            <Router>
              <Layout>
                <Routes>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/portfolio" element={<Portfolio />} />
                  <Route path="/strategies" element={<Strategies />} />
                  <Route path="/social" element={<SocialFeed />} />
                  <Route path="/performance" element={<PerformanceTracking />} />
                  <Route path="/yolo" element={<YOLOTrading />} />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </Layout>
            </Router>
          </MarketsProvider>
        </PortfolioProvider>
      </OfflineProvider>
    </ThemeProvider>
  );
};

export default App;
