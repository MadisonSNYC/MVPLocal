// Electron main process file
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const axios = require('axios');
const isDev = process.env.NODE_ENV === 'development';

// Global reference to the main window
let mainWindow;

// Function to wait for the React development server
function waitForReactDevServer(callback) {
  const serverUrl = 'http://localhost:3000';
  let attempts = 30; // 30 attempts with 1-second delay = 30 seconds timeout
  
  const checkServer = () => {
    axios.get(serverUrl)
      .then(() => {
        console.log('React development server is ready!');
        callback();
      })
      .catch(() => {
        attempts--;
        if (attempts <= 0) {
          console.error('Timed out waiting for React development server');
          callback(new Error('Timed out waiting for React development server'));
        } else {
          console.log(`Waiting for React development server... ${attempts} attempts left`);
          setTimeout(checkServer, 1000);
        }
      });
  };
  
  checkServer();
}

// Create the main browser window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'src', 'preload.js')
    },
    titleBarStyle: 'hiddenInset', // For macOS native feel
    backgroundColor: '#1a1a1a', // Dark background for initial load
    show: false // Hide until ready
  });

  // Load the index.html file
  if (isDev) {
    // In development, load from React development server
    console.log('Development mode: Waiting for React dev server...');
    waitForReactDevServer((err) => {
      if (err) {
        console.error('Failed to connect to React dev server:', err);
        app.quit();
        return;
      }
      
      mainWindow.loadURL('http://localhost:3000');
      // Open DevTools
      mainWindow.webContents.openDevTools();
      mainWindow.show();
    });
  } else {
    // In production, load from built files
    mainWindow.loadFile(path.join(__dirname, 'build', 'index.html'));
    mainWindow.show();
  }

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Initialize the app
app.whenReady().then(() => {
  // Create the main window
  createWindow();

  // On macOS, recreate the window when the dock icon is clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit the app when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC handlers for communication with the renderer process
ipcMain.handle('get-app-info', () => {
  return {
    version: app.getVersion(),
    platform: process.platform,
    isDev: isDev
  };
});

// Handle backend status check
ipcMain.handle('check-backend-status', async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/health');
    return { status: 'online', data: response.data };
  } catch (error) {
    return { status: 'offline', error: error.message };
  }
}); 