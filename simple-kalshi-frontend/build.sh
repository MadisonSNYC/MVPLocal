#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Kalshi Trading Dashboard...${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed. Please install Node.js and try again.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed. Please install npm and try again.${NC}"
    exit 1
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
npm install

# Build React app
echo -e "${YELLOW}Building React app...${NC}"
npm run build

# Package Electron app
echo -e "${YELLOW}Packaging Electron app...${NC}"
npm run package

echo -e "${GREEN}Build completed successfully!${NC}"
echo "You can find the packaged application in the dist directory." 