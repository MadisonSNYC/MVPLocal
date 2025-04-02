// Electron main process file
const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const isDev = process.env.NODE_ENV === 'development';

// Global reference to the main window
let mainWindow;
// Global reference to the Python backend process
let pyProcess;

// Create the main browser window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    titleBarStyle: 'hiddenInset', // For macOS native feel
    backgroundColor: '#1a1a1a', // Dark background for initial load
  });

  // Load the index.html file
  if (isDev) {
    // In development, load from development server
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

// Start the Python backend process
function startPythonBackend() {
  const pythonPath = isDev ? 'python3' : path.join(process.resourcesPath, 'python', 'bin', 'python3');
  const scriptPath = isDev ? 
    path.join(__dirname, '..', 'backend', 'server.py') : 
    path.join(process.resourcesPath, 'backend', 'server.py');

  console.log(`Starting Python backend: ${pythonPath} ${scriptPath}`);

  // Check if the script exists
  if (!fs.existsSync(scriptPath)) {
    console.error(`Python script not found: ${scriptPath}`);
    app.quit();
    return;
  }

  // Spawn the Python process
  pyProcess = spawn(pythonPath, [scriptPath], {
    stdio: ['ignore', 'pipe', 'pipe']
  });

  // Handle Python process output
  pyProcess.stdout.on('data', (data) => {
    console.log(`[PYTHON]: ${data.toString()}`);
  });

  pyProcess.stderr.on('data', (data) => {
    console.error(`[PYTHON ERROR]: ${data.toString()}`);
  });

  // Handle Python process exit
  pyProcess.on('close', (code) => {
    console.log(`Python backend exited with code ${code}`);
    if (code !== 0 && !app.isQuitting) {
      console.error('Python backend crashed. Restarting...');
      startPythonBackend();
    }
  });
}

// Initialize the app
app.whenReady().then(() => {
  // Start the Python backend
  startPythonBackend();
  
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

// Set a flag when the app is about to quit
app.on('before-quit', () => {
  app.isQuitting = true;
});

// Clean up the Python process when the app is quitting
app.on('will-quit', (event) => {
  if (pyProcess && !pyProcess.killed) {
    event.preventDefault();
    console.log('Terminating Python backend...');
    pyProcess.kill();
    setTimeout(() => {
      app.quit();
    }, 500);
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
    const response = await fetch('http://localhost:5000/api/health');
    const data = await response.json();
    return { status: 'online', data };
  } catch (error) {
    return { status: 'offline', error: error.message };
  }
});
