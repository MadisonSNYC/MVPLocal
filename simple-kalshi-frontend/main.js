const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const Store = require('electron-store');
const axios = require('axios');

// Initialize settings storage
const store = new Store();

// Backend API URL
const BACKEND_URL = store.get('backendUrl') || 'http://127.0.0.1:5000';

// Keep a global reference of the window object to avoid garbage collection
let mainWindow;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: !isDev // Disable web security in dev for easier API access
    },
    backgroundColor: '#f5f5f5',
    show: false, // Hide until ready-to-show
    icon: path.join(__dirname, 'assets', 'icon.png'),
    titleBarStyle: 'hiddenInset', // Gives a more native macOS look
    backgroundColor: '#1a1a1a' // Dark background to prevent white flash
  });

  // Load the app
  const startUrl = `file://${path.join(__dirname, 'build', 'index.html')}`;
  
  console.log('Loading URL:', startUrl);
  console.log('App directory:', __dirname);
  console.log('Build path:', path.join(__dirname, 'build'));
  
  mainWindow.loadURL(startUrl);

  // Show when ready and maximize
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.maximize();
    
    // Always open DevTools for debugging
    mainWindow.webContents.openDevTools();
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Create window when Electron is ready
app.whenReady().then(() => {
  createWindow();

  // Check backend connection
  checkBackendConnection();

  // Re-create window on macOS when dock icon is clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Check backend connection
async function checkBackendConnection() {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/health`);
    if (response.data.status === 'ok') {
      console.log('Backend connection successful');
      mainWindow.webContents.send('backend-status', { connected: true });
    } else {
      console.error('Backend returned unexpected status');
      mainWindow.webContents.send('backend-status', { connected: false, error: 'Unexpected status' });
    }
  } catch (error) {
    console.error('Backend connection failed:', error.message);
    mainWindow.webContents.send('backend-status', { connected: false, error: error.message });
  }
}

// IPC handlers for communication with the renderer process

// Get API settings
ipcMain.handle('get-api-settings', () => {
  return {
    apiUrl: store.get('apiUrl', 'http://127.0.0.1:5000'),
    apiKey: store.get('apiKey', '')
  };
});

// Save API settings
ipcMain.handle('save-api-settings', (event, settings) => {
  store.set('apiUrl', settings.apiUrl);
  store.set('apiKey', settings.apiKey);
  return true;
});

// Show an open file dialog
ipcMain.handle('open-file-dialog', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: [
      { name: 'PEM Files', extensions: ['pem'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  
  if (!canceled && filePaths.length > 0) {
    return filePaths[0];
  }
  return null;
});

// Get backend URL
ipcMain.handle('get-backend-url', () => {
  return BACKEND_URL;
});

// Set backend URL
ipcMain.handle('set-backend-url', (event, url) => {
  store.set('backendUrl', url);
  return url;
});

// Check backend connection
ipcMain.handle('check-backend', async () => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/health`);
    return { connected: response.data.status === 'ok' };
  } catch (error) {
    return { connected: false, error: error.message };
  }
}); 