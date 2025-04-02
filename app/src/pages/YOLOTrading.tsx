import React, { useState, useEffect } from 'react';
import { useOffline } from '../contexts/OfflineContext';

interface YOLOSettings {
  strategy: string;
  riskLevel: string;
  maxSpendPerTrade: number;
  maxTradesPerHour: number;
  maxTotalSpend: number;
  marketConditions: Record<string, any>;
}

interface YOLOStatus {
  is_active: boolean;
  strategy: string;
  risk_level: string;
  max_spend_per_trade: number;
  max_trades_per_hour: number;
  max_total_spend: number;
  total_spent: number;
  trades_this_hour: number;
  total_trades: number;
  recent_trades: any[];
}

interface YOLOTrade {
  status: string;
  timestamp: string;
  market_id: string;
  market_title: string;
  action: string;
  contracts: number;
  cost: number;
  probability: number;
  target_exit: number;
  stop_loss: number;
  confidence: string;
  rationale: string;
  order_id: string;
  strategy: string;
  risk_level: string;
}

const YOLOTrading: React.FC = () => {
  const { isOffline } = useOffline();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [status, setStatus] = useState<YOLOStatus | null>(null);
  const [tradeHistory, setTradeHistory] = useState<YOLOTrade[]>([]);
  const [settings, setSettings] = useState<YOLOSettings>({
    strategy: 'hybrid',
    riskLevel: 'medium',
    maxSpendPerTrade: 10,
    maxTradesPerHour: 3,
    maxTotalSpend: 50,
    marketConditions: { exchange_open: true }
  });
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Fetch YOLO status on component mount and periodically
  useEffect(() => {
    const fetchStatus = async () => {
      if (isOffline) return;
      
      try {
        setIsLoading(true);
        const response = await window.api.fetch('/api/yolo/status');
        setStatus(response);
        setError(null);
      } catch (error) {
        console.error('Failed to fetch YOLO status:', error);
        setError('Failed to fetch YOLO status. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatus();
    
    // Set up polling for status updates if YOLO is active
    const intervalId = setInterval(() => {
      if (status?.is_active) {
        fetchStatus();
      }
    }, 30000); // Update every 30 seconds
    
    return () => clearInterval(intervalId);
  }, [isOffline, status?.is_active]);

  // Fetch trade history when status changes
  useEffect(() => {
    const fetchTradeHistory = async () => {
      if (isOffline || !status) return;
      
      try {
        const response = await window.api.fetch('/api/yolo/history');
        setTradeHistory(response.trades || []);
      } catch (error) {
        console.error('Failed to fetch trade history:', error);
      }
    };

    fetchTradeHistory();
  }, [isOffline, status]);

  // Start YOLO trading
  const startYOLOTrading = async () => {
    if (isOffline) {
      setError('Cannot start YOLO trading in offline mode');
      return;
    }
    
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await window.api.fetch('/api/yolo/start', {
        method: 'POST',
        body: JSON.stringify({
          strategy: settings.strategy,
          risk_level: settings.riskLevel,
          max_spend_per_trade: settings.maxSpendPerTrade,
          max_trades_per_hour: settings.maxTradesPerHour,
          max_total_spend: settings.maxTotalSpend,
          market_conditions: settings.marketConditions
        }),
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.status === 'success') {
        setSuccessMessage('YOLO trading mode started successfully');
        // Fetch updated status
        const statusResponse = await window.api.fetch('/api/yolo/status');
        setStatus(statusResponse);
      } else {
        setError(response.message || 'Failed to start YOLO trading');
      }
    } catch (error) {
      console.error('Failed to start YOLO trading:', error);
      setError('Failed to start YOLO trading. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Stop YOLO trading
  const stopYOLOTrading = async () => {
    if (isOffline) {
      setError('Cannot stop YOLO trading in offline mode');
      return;
    }
    
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await window.api.fetch('/api/yolo/stop', {
        method: 'POST'
      });
      
      if (response.status === 'success') {
        setSuccessMessage('YOLO trading mode stopped successfully');
        // Fetch updated status
        const statusResponse = await window.api.fetch('/api/yolo/status');
        setStatus(statusResponse);
      } else {
        setError(response.message || 'Failed to stop YOLO trading');
      }
    } catch (error) {
      console.error('Failed to stop YOLO trading:', error);
      setError('Failed to stop YOLO trading. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle settings changes
  const handleSettingChange = (setting: keyof YOLOSettings, value: any) => {
    setSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  // Clear messages after 5 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">YOLO Automated Trading</h1>
        <div className="flex space-x-2">
          {status?.is_active ? (
            <button
              onClick={stopYOLOTrading}
              disabled={isLoading || isOffline}
              className="bg-destructive text-destructive-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-destructive/90 disabled:opacity-50"
            >
              {isLoading ? 'Stopping...' : 'Stop YOLO Trading'}
            </button>
          ) : (
            <button
              onClick={startYOLOTrading}
              disabled={isLoading || isOffline}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
            >
              {isLoading ? 'Starting...' : 'Start YOLO Trading'}
            </button>
          )}
        </div>
      </div>

      {/* Error and Success Messages */}
      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md mb-4">
          {error}
        </div>
      )}
      
      {successMessage && (
        <div className="bg-green-100 text-green-800 px-4 py-3 rounded-md mb-4">
          {successMessage}
        </div>
      )}

      {/* YOLO Status */}
      {status && (
        <div className="bg-card rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">YOLO Status</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-sm text-muted-foreground">Status</p>
              <p className={`font-medium ${status.is_active ? 'text-green-500' : 'text-muted-foreground'}`}>
                {status.is_active ? 'Active' : 'Inactive'}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Strategy</p>
              <p className="font-medium">{status.strategy}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Risk Level</p>
              <p className="font-medium">{status.risk_level}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Trades</p>
              <p className="font-medium">{status.total_trades}</p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-sm text-muted-foreground">Max Spend Per Trade</p>
              <p className="font-medium">${status.max_spend_per_trade.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Max Trades Per Hour</p>
              <p className="font-medium">{status.max_trades_per_hour}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Max Total Spend</p>
              <p className="font-medium">${status.max_total_spend.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Spent</p>
              <p className="font-medium">${status.total_spent.toFixed(2)}</p>
            </div>
          </div>
          
          <div className="flex items-center">
            <div className="w-full bg-muted rounded-full h-2.5">
              <div 
                className="bg-primary h-2.5 rounded-full" 
                style={{ width: `${Math.min(100, (status.total_spent / status.max_total_spend) * 100)}%` }}
              ></div>
            </div>
            <span className="ml-2 text-sm text-muted-foreground">
              {Math.round((status.total_spent / status.max_total_spend) * 100)}%
            </span>
          </div>
        </div>
      )}

      {/* YOLO Settings */}
      <div className="bg-card rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">YOLO Settings</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium mb-2">Strategy</label>
            <select
              value={settings.strategy}
              onChange={(e) => handleSettingChange('strategy', e.target.value)}
              disabled={status?.is_active || isOffline}
              className="w-full px-3 py-2 bg-background border border-input rounded-md"
            >
              <option value="momentum">Momentum</option>
              <option value="mean-reversion">Mean Reversion</option>
              <option value="hybrid">Hybrid</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Risk Level</label>
            <select
              value={settings.riskLevel}
              onChange={(e) => handleSettingChange('riskLevel', e.target.value)}
              disabled={status?.is_active || isOffline}
              className="w-full px-3 py-2 bg-background border border-input rounded-md"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Max Spend Per Trade (${settings.maxSpendPerTrade.toFixed(2)})
            </label>
            <input
              type="range"
              min="1"
              max="50"
              step="1"
              value={settings.maxSpendPerTrade}
              onChange={(e) => handleSettingChange('maxSpendPerTrade', parseFloat(e.target.value))}
              disabled={status?.is_active || isOffline}
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Max Trades Per Hour ({settings.maxTradesPerHour})
            </label>
            <input
              type="range"
              min="1"
              max="10"
              step="1"
              value={settings.maxTradesPerHour}
              onChange={(e) => handleSettingChange('maxTradesPerHour', parseInt(e.target.value))}
              disabled={status?.is_active || isOffline}
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Max Total Spend (${settings.maxTotalSpend.toFixed(2)})
            </label>
            <input
              type="range"
              min="10"
              max="200"
              step="10"
              value={settings.maxTotalSpend}
              onChange={(e) => handleSettingChange('maxTotalSpend', parseFloat(e.target.value))}
              disabled={status?.is_active || isOffline}
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Market Conditions</label>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="exchange_open"
                checked={settings.marketConditions.exchange_open}
                onChange={(e) => handleSettingChange('marketConditions', {
                  ...settings.marketConditions,
                  exchange_open: e.target.checked
                })}
                disabled={status?.is_active || isOffline}
                className="mr-2"
              />
              <label htmlFor="exchange_open" className="text-sm">Only trade when exchange is open</label>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Trades */}
      <div className="bg-card rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Trades</h2>
        
        {tradeHistory.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            No trades have been executed yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Market</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Action</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Contracts</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Cost</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {tradeHistory.map((trade, index) => (
                  <tr key={index} className="hover:bg-muted/30">
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {new Date(trade.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {trade.market_title}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        trade.action === 'YES' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {trade.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {trade.contracts}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      ${trade.cost.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {trade.confidence}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default YOLOTrading;
