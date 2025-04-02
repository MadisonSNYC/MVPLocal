import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';
import { useTheme } from '../contexts/ThemeContext';

const Settings = () => {
  const { backendUrl, updateBackendUrl, isConnected } = useApi();
  const { theme, toggleTheme } = useTheme();
  
  const [settings, setSettings] = useState({
    apiKeyId: '',
    privateKey: '',
    openaiApiKey: '',
    refreshInterval: 60,
    demoMode: false
  });
  const [newBackendUrl, setNewBackendUrl] = useState(backendUrl);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Fetch current settings
  useEffect(() => {
    const fetchSettings = async () => {
      if (!isConnected) return;

      setIsLoading(true);
      setError(null);

      try {
        const data = await window.api.getSettings();
        setSettings({
          ...settings,
          ...data,
          // Don't show actual private key, just placeholder if it exists
          privateKey: data.privateKey ? '••••••••••••••••' : '',
          apiKeyId: data.apiKeyId || '',
          openaiApiKey: data.openaiApiKey ? '••••••••••••••••' : ''
        });
      } catch (error) {
        setError('Failed to fetch settings');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSettings();
  }, [isConnected]);

  // Handle input change
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings({
      ...settings,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  // Save settings
  const saveSettings = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await window.api.saveSettings(settings);
      setSuccessMessage('Settings saved successfully');
      
      // If backend URL changed, update it
      if (newBackendUrl !== backendUrl) {
        await updateBackendUrl(newBackendUrl);
      }
    } catch (error) {
      setError('Failed to save settings: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Settings</h1>
      </div>

      <form onSubmit={saveSettings} className="space-y-6">
        {/* API Configuration */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">API Configuration</h2>
          
          {error && (
            <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4">
              <p>{error}</p>
            </div>
          )}
          
          {successMessage && (
            <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-4">
              <p>{successMessage}</p>
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Backend URL
              </label>
              <input
                type="text"
                value={newBackendUrl}
                onChange={(e) => setNewBackendUrl(e.target.value)}
                className="input-field w-full"
                placeholder="http://localhost:3001"
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                URL of the FastAPI backend server
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Kalshi API Key ID
              </label>
              <input
                type="text"
                name="apiKeyId"
                value={settings.apiKeyId}
                onChange={handleInputChange}
                className="input-field w-full"
                placeholder="Enter your Kalshi API Key ID"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Kalshi Private Key
              </label>
              <textarea
                name="privateKey"
                value={settings.privateKey}
                onChange={handleInputChange}
                className="input-field w-full h-24"
                placeholder="Enter your Kalshi private key (RSA private key in PEM format) "
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Your private key is stored securely in the macOS Keychain and never transmitted
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                OpenAI API Key
              </label>
              <input
                type="text"
                name="openaiApiKey"
                value={settings.openaiApiKey}
                onChange={handleInputChange}
                className="input-field w-full"
                placeholder="Enter your OpenAI API key"
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Required for AI-powered trade recommendations
              </p>
            </div>
          </div>
        </div>

        {/* Application Settings */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Application Settings</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Refresh Interval (seconds)
              </label>
              <input
                type="number"
                name="refreshInterval"
                min="10"
                max="300"
                value={settings.refreshInterval}
                onChange={handleInputChange}
                className="input-field w-full"
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                How often to refresh market data (10-300 seconds)
              </p>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="demoMode"
                name="demoMode"
                checked={settings.demoMode}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="demoMode" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                Enable Demo Mode
              </label>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Demo mode uses simulated data and doesn't require API credentials
            </p>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="darkMode"
                checked={theme === 'dark'}
                onChange={toggleTheme}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="darkMode" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                Dark Mode
              </label>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary disabled:opacity-50"
          >
            {isLoading ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Settings; 