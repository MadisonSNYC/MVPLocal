import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface OfflineContextType {
  isOffline: boolean;
  lastOnlineTime: Date | null;
  setManualOfflineMode: (value: boolean) => void;
  isManualOfflineMode: boolean;
}

const OfflineContext = createContext<OfflineContextType | undefined>(undefined);

interface OfflineProviderProps {
  children: ReactNode;
}

export const OfflineProvider: React.FC<OfflineProviderProps> = ({ children }) => {
  const [isNetworkOffline, setIsNetworkOffline] = useState<boolean>(!navigator.onLine);
  const [isBackendOffline, setIsBackendOffline] = useState<boolean>(false);
  const [isManualOfflineMode, setIsManualOfflineMode] = useState<boolean>(
    localStorage.getItem('manualOfflineMode') === 'true'
  );
  const [lastOnlineTime, setLastOnlineTime] = useState<Date | null>(null);

  // Check if we're offline due to network or backend issues
  const isOffline = isNetworkOffline || isBackendOffline || isManualOfflineMode;

  // Load last online time from localStorage
  useEffect(() => {
    const savedTime = localStorage.getItem('lastOnlineTime');
    if (savedTime) {
      setLastOnlineTime(new Date(savedTime));
    }
  }, []);

  // Update last online time when going offline
  useEffect(() => {
    if (!isOffline) {
      const now = new Date();
      setLastOnlineTime(now);
      localStorage.setItem('lastOnlineTime', now.toISOString());
    }
  }, [isOffline]);

  // Handle manual offline mode
  const setManualOfflineMode = (value: boolean) => {
    setIsManualOfflineMode(value);
    localStorage.setItem('manualOfflineMode', value.toString());
  };

  // Monitor network status
  useEffect(() => {
    const handleOnline = () => setIsNetworkOffline(false);
    const handleOffline = () => setIsNetworkOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Check backend status periodically
  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const status = await window.electron.checkBackendStatus();
        setIsBackendOffline(status.status !== 'online');
      } catch (error) {
        setIsBackendOffline(true);
      }
    };

    // Initial check
    checkBackendStatus();

    // Set up interval for periodic checks
    const intervalId = setInterval(checkBackendStatus, 30000); // Check every 30 seconds

    return () => clearInterval(intervalId);
  }, []);

  return (
    <OfflineContext.Provider 
      value={{ 
        isOffline, 
        lastOnlineTime, 
        setManualOfflineMode, 
        isManualOfflineMode 
      }}
    >
      {children}
    </OfflineContext.Provider>
  );
};

// Custom hook to use the offline context
export const useOffline = (): OfflineContextType => {
  const context = useContext(OfflineContext);
  if (context === undefined) {
    throw new Error('useOffline must be used within an OfflineProvider');
  }
  return context;
};
