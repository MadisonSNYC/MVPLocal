const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'api', {
    // Backend communication
    getBackendUrl: () => {
      console.log('Getting backend URL...');
      return ipcRenderer.invoke('get-backend-url');
    },
    setBackendUrl: (url) => {
      console.log(`Setting backend URL to: ${url}`);
      return ipcRenderer.invoke('set-backend-url', url);
    },
    checkBackendConnection: () => {
      console.log('Checking backend connection...');
      return ipcRenderer.invoke('check-backend');
    },
    
    // Listen for backend status updates
    onBackendStatusChange: (callback) => {
      console.log('Setting up backend status change listener...');
      ipcRenderer.on('backend-status', (_, status) => {
        console.log('Backend status changed:', status);
        callback(status);
      });
      return () => {
        console.log('Removing backend status listeners...');
        ipcRenderer.removeAllListeners('backend-status');
      };
    }
  }
); 