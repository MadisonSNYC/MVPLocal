import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Import pages
import Dashboard from './pages/Dashboard';
import Portfolio from './pages/Portfolio';
import Strategies from './pages/Strategies';
import YOLOTrading from './pages/YOLOTrading';
import SocialFeed from './pages/SocialFeed';
import PerformanceTracking from './pages/PerformanceTracking';
import Settings from './pages/Settings';

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/portfolio" element={<Portfolio />} />
      <Route path="/strategies" element={<Strategies />} />
      <Route path="/yolo" element={<YOLOTrading />} />
      <Route path="/social" element={<SocialFeed />} />
      <Route path="/performance" element={<PerformanceTracking />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes; 