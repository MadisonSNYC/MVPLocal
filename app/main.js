// Electron main process file
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const axios = require('axios');
const isDev = process.env.NODE_ENV === 'development';

// Global reference to the main window
let mainWindow;

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
  });

  // Load the index.html file
  if (isDev) {
    // In development, load from React development server
    mainWindow.loadURL('http://localhost:3000');
    // Open DevTools
    mainWindow.webContents.openDevTools();
  } else {
    // In production, load from built files
    mainWindow.loadFile(path.join(__dirname, 'build', 'index.html'));
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