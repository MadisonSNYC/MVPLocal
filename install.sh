#!/bin/bash
# Installation script for Kalshi Trading Dashboard

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Kalshi Trading Dashboard Installation  ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${YELLOW}Warning: This application is optimized for macOS.${NC}"
    echo -e "${YELLOW}Some features may not work correctly on other platforms.${NC}"
    echo ""
fi

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "$PYTHON_VERSION"
    
    # Check if version is at least 3.10
    PYTHON_VERSION_NUM=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION_NUM | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION_NUM | cut -d'.' -f2)
    
    if [ $PYTHON_MAJOR -lt 3 ] || ([ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -lt 10 ]); then
        echo -e "${YELLOW}Warning: Python 3.10 or higher is recommended.${NC}"
        echo "The application may still work, but some features might be unstable."
        
        # Ask user if they want to continue
        read -p "Continue with installation anyway? (y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation aborted."
            exit 1
        fi
    else
        echo -e "${GREEN}Python version check passed.${NC}"
    fi
else
    echo -e "${RED}Error: Python 3 not found.${NC}"
    echo "Please install Python 3.10 or higher before continuing."
    exit 1
fi

# Create Python virtual environment
echo -e "${BLUE}Setting up Python environment...${NC}"
cd backend
if [ -d "venv" ]; then
    echo "Virtual environment already exists, updating..."
    if command -v python3 -m venv &>/dev/null; then
        python3 -m venv venv --clear
    else
        python3 -m virtualenv venv --clear
    fi
else
    echo "Creating new virtual environment..."
    if command -v python3 -m venv &>/dev/null; then
        python3 -m venv venv
    else
        python3 -m virtualenv venv
    fi
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip

# Install each required package directly
pip install fastapi>=0.95.0 uvicorn>=0.21.1 pydantic>=1.10.7 python-dotenv>=1.0.0 \
    requests>=2.28.2 cryptography>=40.0.1 numpy>=1.24.2 pandas>=2.0.0 \
    openai>=0.27.4 pytest>=7.3.1 python-dateutil>=2.8.2 pytz>=2023.3

# Check for errors
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install Python dependencies.${NC}"
    echo "Please check your internet connection and try again."
    exit 1
fi

# Deactivate virtual environment
deactivate
cd ..

# Create logs directory
echo -e "${BLUE}Creating logs directory...${NC}"
mkdir -p logs

# Set up configuration
echo -e "${BLUE}Setting up configuration...${NC}"
if [ ! -f "config/.env" ]; then
    echo "Creating default configuration file..."
    cat > config/.env << EOL
# Kalshi Trading Dashboard Configuration

# API Endpoints
KALSHI_API_URL=https://trading-api.kalshi.com/v1

# Credentials will be stored in macOS Keychain
# These are just placeholders and will be replaced by the application
KALSHI_API_KEY_ID=your_api_key_id
KALSHI_API_KEY_SECRET=your_api_key_secret
OPENAI_API_KEY=your_openai_api_key

# Backend Configuration
BACKEND_PORT=3001
BACKEND_HOST=127.0.0.1

# Feature Flags
ENABLE_YOLO_MODE=true
ENABLE_SOCIAL_FEED=true
ENABLE_PERFORMANCE_TRACKING=true
ENABLE_DEMO_MODE=false

# Trading Configuration
DEFAULT_STRATEGY=hybrid
DEFAULT_RISK_LEVEL=medium
REFRESH_INTERVAL=60
EOL
fi

# Make scripts executable
echo -e "${BLUE}Setting permissions...${NC}"
chmod +x start.sh

# Final message
echo ""
echo -e "${GREEN}Installation completed successfully!${NC}"
echo ""
echo "To start the application, run:"
echo -e "${BLUE}./start.sh${NC}"
echo ""
echo "For demo mode (no API credentials required), run:"
echo -e "${BLUE}./start.sh --demo${NC}"
echo ""
echo "For more information, see the documentation in the docs directory."
echo -e "${BLUE}docs/user_guide.md${NC}"
echo ""
echo -e "${YELLOW}Note: On first run, you will be prompted to enter your API credentials.${NC}"
echo -e "${YELLOW}These will be securely stored in the macOS Keychain.${NC}"
