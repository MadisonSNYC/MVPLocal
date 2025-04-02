/**
 * Test script for the Electron application.
 * 
 * This script tests the functionality of the Electron application
 * by simulating user interactions and verifying the expected behavior.
 */

const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const assert = require('assert');

// Configure logging
const logFile = path.join(__dirname, '..', 'test_results', 'electron_app_test.log');
const logDir = path.dirname(logFile);

if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

const logger = {
  info: (message) => {
    const logMessage = `[INFO] ${new Date().toISOString()} - ${message}`;
    console.log(logMessage);
    fs.appendFileSync(logFile, logMessage + '\n');
  },
  error: (message) => {
    const logMessage = `[ERROR] ${new Date().toISOString()} - ${message}`;
    console.error(logMessage);
    fs.appendFileSync(logFile, logMessage + '\n');
  },
  warning: (message) => {
    const logMessage = `[WARNING] ${new Date().toISOString()} - ${message}`;
    console.warn(logMessage);
    fs.appendFileSync(logFile, logMessage + '\n');
  }
};

// Test results
const testResults = {
  appStart: false,
  backendConnection: false,
  rendererLoad: false,
  apiCommunication: false
};

// Start Python backend
function startPythonBackend() {
  logger.info('Starting Python backend...');
  
  const pythonPath = 'python3';
  const scriptPath = path.join(__dirname, '..', '..', 'backend', 'server.py');
  
  // Check if the script exists
  if (!fs.existsSync(scriptPath)) {
    logger.error(`Python script not found: ${scriptPath}`);
    return null;
  }
  
  // Spawn the Python process
  const pyProcess = spawn(pythonPath, [scriptPath], {
    stdio: ['ignore', 'pipe', 'pipe']
  });
  
  // Handle Python process output
  pyProcess.stdout.on('data', (data) => {
    logger.info(`[PYTHON]: ${data.toString().trim()}`);
  });
  
  pyProcess.stderr.on('data', (data) => {
    logger.error(`[PYTHON ERROR]: ${data.toString().trim()}`);
  });
  
  // Handle Python process exit
  pyProcess.on('close', (code) => {
    logger.info(`Python backend exited with code ${code}`);
  });
  
  // Wait for the backend to start
  return new Promise((resolve) => {
    setTimeout(() => {
      logger.info('Backend startup wait time elapsed');
      resolve(pyProcess);
    }, 5000);
  });
}

// Test the Electron application
async function testElectronApp() {
  logger.info('Testing Electron application...');
  
  let pyProcess = null;
  
  try {
    // Start the Python backend
    pyProcess = await startPythonBackend();
    
    if (!pyProcess) {
      logger.error('Failed to start Python backend');
      return false;
    }
    
    // Initialize the app
    logger.info('Initializing Electron app...');
    
    // Wait for app to be ready
    await app.whenReady();
    testResults.appStart = true;
    logger.info('Electron app initialized successfully');
    
    // Create a browser window
    const mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      show: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, '..', 'src', 'preload.js')
      }
    });
    
    // Load the index.html file
    const indexPath = path.join(__dirname, '..', 'public', 'index.html');
    
    if (fs.existsSync(indexPath)) {
      await mainWindow.loadFile(indexPath);
      testResults.rendererLoad = true;
      logger.info('Renderer loaded successfully');
    } else {
      logger.warning(`Index file not found: ${indexPath}`);
      logger.info('Loading about:blank instead');
      await mainWindow.loadURL('about:blank');
    }
    
    // Test backend connection
    try {
      const response = await fetch('http://localhost:5000/api/health');
      const data = await response.json();
      
      if (data.status === 'ok') {
        testResults.backendConnection = true;
        logger.info('Backend connection successful');
      } else {
        logger.warning('Backend connection returned unexpected status');
      }
    } catch (error) {
      logger.error(`Backend connection failed: ${error.message}`);
    }
    
    // Test API communication via preload
    try {
      const result = await mainWindow.webContents.executeJavaScript(`
        new Promise(async (resolve) => {
          try {
            if (window.api) {
              const response = await window.api.fetch('/api/health');
              resolve({ success: true, response });
            } else {
              resolve({ success: false, error: 'API not available in window object' });
            }
          } catch (error) {
            resolve({ success: false, error: error.toString() });
          }
        })
      `);
      
      if (result.success) {
        testResults.apiCommunication = true;
        logger.info('API communication successful');
      } else {
        logger.warning(`API communication failed: ${result.error}`);
      }
    } catch (error) {
      logger.error(`Failed to execute JavaScript in renderer: ${error.message}`);
    }
    
    // Save test results
    const resultsPath = path.join(__dirname, '..', 'test_results', 'electron_app_test.json');
    fs.writeFileSync(resultsPath, JSON.stringify(testResults, null, 2));
    logger.info(`Test results saved to ${resultsPath}`);
    
    // Check if all tests passed
    const allPassed = Object.values(testResults).every(result => result === true);
    
    if (allPassed) {
      logger.info('All tests passed!');
    } else {
      logger.warning('Some tests failed. Check the results file for details.');
    }
    
    return allPassed;
  } catch (error) {
    logger.error(`Test failed with error: ${error.message}`);
    return false;
  } finally {
    // Clean up
    if (pyProcess) {
      logger.info('Terminating Python backend...');
      pyProcess.kill();
    }
    
    // Quit the app
    logger.info('Quitting Electron app...');
    app.quit();
  }
}

// Run the test
testElectronApp().then(result => {
  process.exit(result ? 0 : 1);
}).catch(error => {
  logger.error(`Unhandled error: ${error.message}`);
  process.exit(1);
});
