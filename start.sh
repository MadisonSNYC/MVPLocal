#!/bin/bash
# Single launch script for Kalshi Trading Dashboard
# This script starts both the Electron frontend and FastAPI backend simultaneously

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Kalshi Trading Dashboard Launcher      ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

# Configuration
BACKEND_PORT=8000  # Default port (changed from 5000 to avoid conflict with AirPlay on macOS)
BACKEND_HOST="127.0.0.1"
BACKEND_DIR="./backend"
APP_DIR="./app"
LOG_DIR="/Users/madisonrayesutton/Downloads/dist/logs"
PID_FILE="./kalshi-dashboard.pid"

# Function to kill processes on a specific port
kill_process_on_port() {
    local PORT=$1
    echo -e "${YELLOW}Checking if port $PORT is in use...${NC}"
    
    if command -v lsof &>/dev/null; then
        # Get PID of process using the port
        local PID=$(lsof -ti:$PORT)
        if [ ! -z "$PID" ]; then
            echo -e "${YELLOW}Found process using port $PORT, killing PID: $PID${NC}"
            kill -9 $PID 2>/dev/null
            sleep 1
        fi
    fi
}

# Load environment variables from .env file if it exists
if [ -f "config/.env" ]; then
    echo "Loading configuration from config/.env..."
    export $(grep -v '^#' config/.env | xargs)
    # Override default port if .env provides it
    if [ -n "$SERVER_PORT" ]; then
        BACKEND_PORT=$SERVER_PORT
        echo "Using port $BACKEND_PORT from config/.env"
    else
        BACKEND_PORT=8000   # default to 8000
        echo "Using default port $BACKEND_PORT (no SERVER_PORT found in config/.env)"
    fi
    # Override default host if .env provides it
    if [ -n "$SERVER_HOST" ]; then
        BACKEND_HOST=$SERVER_HOST
        echo "Using host $BACKEND_HOST from config/.env"
    else
        echo "Using default host $BACKEND_HOST (no SERVER_HOST found in config/.env)"
    fi
else
    echo "No config/.env file found, using default port $BACKEND_PORT and host $BACKEND_HOST"
fi

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"
touch "$LOG_DIR/backend.log"
touch "$LOG_DIR/frontend.log"
touch "$LOG_DIR/credential_check.log"

# Function to check if a process is running
is_process_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null; then
            return 0 # Process is running
        fi
    fi
    return 1 # Process is not running
}

# Function to kill existing processes
kill_existing_processes() {
    echo -e "${YELLOW}Stopping existing processes...${NC}"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null; then
            echo "Killing process $PID..."
            kill "$PID" 2>/dev/null
            sleep 2
            
            # Force kill if still running
            if ps -p "$PID" > /dev/null; then
                echo "Force killing process $PID..."
                kill -9 "$PID" 2>/dev/null
            fi
        fi
        rm "$PID_FILE"
    fi
    
    # Check for any remaining Python or Node processes related to our app
    PYTHON_PIDS=$(ps aux | grep "[p]ython.*server.py" | awk '{print $2}')
    if [ ! -z "$PYTHON_PIDS" ]; then
        echo "Killing Python backend processes..."
        for PID in $PYTHON_PIDS; do
            kill "$PID" 2>/dev/null
        done
    fi
    
    NODE_PIDS=$(ps aux | grep "[n]ode.*electron" | awk '{print $2}')
    if [ ! -z "$NODE_PIDS" ]; then
        echo "Killing Electron processes..."
        for PID in $NODE_PIDS; do
            kill "$PID" 2>/dev/null
        done
    fi
}

# Function to start the backend
start_backend() {
    echo -e "${BLUE}Starting FastAPI backend server...${NC}"
    echo -e "${BLUE}Using host: $BACKEND_HOST and port: $BACKEND_PORT${NC}"
    cd "$BACKEND_DIR"
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        echo "Activating Python virtual environment..."
        source venv/bin/activate
    fi
    
    # Start the backend server
    python server.py --port "$BACKEND_PORT" --host "$BACKEND_HOST" > "$LOG_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PID_FILE"
    
    echo -e "${GREEN}Backend server started with PID $BACKEND_PID${NC}"
    echo "Backend logs available at: $LOG_DIR/backend.log"
    
    # Return to original directory
    cd - > /dev/null
    
    # Wait for backend to start
    echo "Waiting for backend to initialize..."
    sleep 3
    
    # Check if backend is running
    if ! ps -p "$BACKEND_PID" > /dev/null; then
        echo -e "${RED}Error: Backend failed to start. Check logs at $LOG_DIR/backend.log${NC}"
        exit 1
    fi
    
    # Check if backend is responding
    echo "Checking backend connection..."
    if command -v curl &>/dev/null; then
        if ! curl -s "http://$BACKEND_HOST:$BACKEND_PORT/api/health" > /dev/null; then
            echo -e "${YELLOW}Warning: Backend health check failed. Application may not function correctly.${NC}"
        else
            echo -e "${GREEN}Backend health check passed.${NC}"
        fi
    else
        echo -e "${YELLOW}Warning: curl not found, skipping backend health check.${NC}"
    fi
}

# Function to start the frontend
start_frontend() {
    echo -e "${BLUE}Starting Electron frontend...${NC}"
    cd "$APP_DIR"
    
    # Create logs directory if it doesn't exist
    mkdir -p "$LOG_DIR"
    
    # Check if we're in development or production mode
    if [ -d "node_modules" ] && [ -f "package.json" ]; then
        # Development mode
        echo "Starting in development mode..."
        npm start > "$LOG_DIR/frontend.log" 2>&1 &
        FRONTEND_PID=$!
        echo -e "${GREEN}Frontend started in development mode with PID $FRONTEND_PID${NC}"
    else
        # Production mode
        echo "Looking for production build..."
        if [ -d "KalshiTradingDashboard.app" ]; then
            # macOS app bundle
            echo "Found macOS app bundle, opening..."
            open KalshiTradingDashboard.app
            echo -e "${GREEN}Frontend started (macOS app)${NC}"
        elif [ -f "KalshiTradingDashboard" ]; then
            # Linux executable
            echo "Found Linux executable, running..."
            ./KalshiTradingDashboard > "$LOG_DIR/frontend.log" 2>&1 &
            FRONTEND_PID=$!
            echo -e "${GREEN}Frontend started (Linux) with PID $FRONTEND_PID${NC}"
        elif [ -f "KalshiTradingDashboard.exe" ]; then
            # Windows executable
            echo "Found Windows executable, running..."
            ./KalshiTradingDashboard.exe > "$LOG_DIR/frontend.log" 2>&1 &
            FRONTEND_PID=$!
            echo -e "${GREEN}Frontend started (Windows) with PID $FRONTEND_PID${NC}"
        else
            echo -e "${YELLOW}Warning: Could not find Electron application.${NC}"
            echo "Checking for development environment..."
            
            if [ -f "package.json" ]; then
                echo "Found package.json, attempting to start in development mode..."
                # Install dependencies if needed
                if [ ! -d "node_modules" ]; then
                    echo "Installing dependencies (this may take a while)..."
                    npm install
                fi
                
                # Start in development mode
                npm start > "$LOG_DIR/frontend.log" 2>&1 &
                FRONTEND_PID=$!
                echo -e "${GREEN}Frontend started in development mode with PID $FRONTEND_PID${NC}"
            else
                echo -e "${RED}Error: Could not find Electron application or development environment.${NC}"
                echo "Please make sure the application is built correctly or development environment is set up."
                return 1
            fi
        fi
    fi
    
    echo "Frontend logs available at: $LOG_DIR/frontend.log"
    
    # Return to original directory
    cd - > /dev/null
    return 0
}

# Function to check for credentials
check_credentials() {
    echo -e "${BLUE}Checking for API credentials...${NC}"
    
    # Check if credentials are configured
    cd "$BACKEND_DIR"
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Run credential check script
    python -c "
import sys
sys.path.append('./app')
try:
    from keychain_manager import CredentialManager
    cm = CredentialManager()
    has_creds = cm.has_credentials()
    if not has_creds:
        print('no_credentials')
    else:
        print('has_credentials')
except Exception as e:
    print(f'error: {str(e)}')
" > "$LOG_DIR/credential_check.log" 2>&1
    
    CRED_CHECK=$(cat "$LOG_DIR/credential_check.log")
    
    # Return to original directory
    cd - > /dev/null
    
    if [[ "$CRED_CHECK" == "no_credentials" ]]; then
        echo -e "${YELLOW}Warning: API credentials not found.${NC}"
        echo -e "${YELLOW}The application will start in demo mode.${NC}"
        echo -e "${YELLOW}You can configure credentials in the application settings.${NC}"
        
        # Enable demo mode
        cd "$BACKEND_DIR"
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi
        python -c "
import sys
sys.path.append('./app')
try:
    from demo_mode import DemoModeManager
    dm = DemoModeManager()
    dm.enable_demo_mode()
    print('Demo mode enabled')
except Exception as e:
    print(f'Error enabling demo mode: {str(e)}')
"
        cd - > /dev/null
    elif [[ "$CRED_CHECK" == "has_credentials" ]]; then
        echo -e "${GREEN}API credentials found.${NC}"
        echo -e "${GREEN}Application will start in production mode.${NC}"
    else
        echo -e "${YELLOW}Warning: Could not check credentials. See $LOG_DIR/credential_check.log${NC}"
        echo -e "${YELLOW}The application will start, but may not function correctly.${NC}"
    fi
}

# Function to check system requirements
check_system_requirements() {
    echo -e "${BLUE}Checking system requirements...${NC}"
    
    # Check if running on macOS
    if [[ "$(uname)" == "Darwin" ]]; then
        echo -e "${GREEN}Running on macOS.${NC}"
        
        # Check macOS version
        MACOS_VERSION=$(sw_vers -productVersion)
        echo "macOS version: $MACOS_VERSION"
        
        # Check if running on Apple Silicon
        if [[ "$(uname -m)" == "arm64" ]]; then
            echo "Running on Apple Silicon."
        else
            echo "Running on Intel processor."
        fi
    else
        echo -e "${YELLOW}Warning: Not running on macOS. Some features may not work correctly.${NC}"
    fi
    
    # Check Python version
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo "$PYTHON_VERSION"
        
        # Check if version is at least 3.10
        PYTHON_VERSION_NUM=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION_NUM | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION_NUM | cut -d'.' -f2)
        
        if [ $PYTHON_MAJOR -lt 3 ] || ([ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -lt 10 ]); then
            echo -e "${YELLOW}Warning: Python 3.10 or higher is recommended.${NC}"
        fi
    else
        echo -e "${RED}Error: Python 3 not found. Please install Python 3.10 or higher.${NC}"
        exit 1
    fi
    
    # Check Node.js version
    if command -v node &>/dev/null; then
        NODE_VERSION=$(node --version)
        echo "Node.js $NODE_VERSION"
        
        # Check if version is at least 18
        NODE_VERSION_NUM=$(node --version | cut -c2-)
        NODE_MAJOR=$(echo $NODE_VERSION_NUM | cut -d'.' -f1)
        
        if [ $NODE_MAJOR -lt 18 ]; then
            echo -e "${YELLOW}Warning: Node.js 18 or higher is recommended.${NC}"
        fi
    else
        echo -e "${YELLOW}Warning: Node.js not found. This may be fine in production mode.${NC}"
    fi
}

# Main execution
# Check if help flag is provided
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --demo       Start in demo mode"
    echo "  --dev        Start in development mode"
    echo "  --reset      Reset all settings and credentials"
    echo "  --help, -h   Show this help message"
    exit 0
fi

# Check if reset flag is provided
if [[ "$1" == "--reset" ]]; then
    echo -e "${YELLOW}Resetting all settings and credentials...${NC}"
    
    # Kill existing processes
    kill_existing_processes
    
    # Remove credentials
    cd "$BACKEND_DIR"
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    python -c "
import sys
sys.path.append('./app')
try:
    from keychain_manager import CredentialManager
    cm = CredentialManager()
    cm.delete_all_credentials()
    print('Credentials deleted')
    
    from demo_mode import DemoModeManager
    dm = DemoModeManager()
    dm.enable_demo_mode()
    print('Demo mode enabled')
except Exception as e:
    print(f'Error: {str(e)}')
"
    cd - > /dev/null
    
    echo -e "${GREEN}Reset complete. The application will start in demo mode.${NC}"
fi

# Check if demo flag is provided
if [[ "$1" == "--demo" ]]; then
    echo -e "${BLUE}Starting in demo mode...${NC}"
    
    # Enable demo mode
    cd "$BACKEND_DIR"
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    python -c "
import sys
sys.path.append('./app')
try:
    from demo_mode import DemoModeManager
    dm = DemoModeManager()
    dm.enable_demo_mode()
    print('Demo mode enabled')
except Exception as e:
    print(f'Error enabling demo mode: {str(e)}')
"
    cd - > /dev/null
fi

# Kill any existing processes
kill_existing_processes

# Check system requirements
check_system_requirements

# Kill any process using our target port
kill_process_on_port $BACKEND_PORT

# Check for credentials
check_credentials

# Start the backend
start_backend

# Start the frontend application
start_frontend || {
    echo -e "${RED}Failed to start frontend application.${NC}"
    echo "Check logs at $LOG_DIR/frontend.log for more information."
    exit 1
}

echo ""
echo -e "${GREEN}Kalshi Trading Dashboard started successfully!${NC}"
echo -e "${BLUE}Press Ctrl+C to stop the application${NC}"

# Wait for user to press Ctrl+C
trap "echo -e '${YELLOW}Stopping Kalshi Trading Dashboard...${NC}'; kill_existing_processes; echo -e '${GREEN}Application stopped.${NC}'; exit 0" INT
while true; do
    sleep 1
done
