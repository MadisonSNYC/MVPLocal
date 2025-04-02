# Kalshi Trading Dashboard

A simple production-ready Electron application for trading on Kalshi markets with AI-powered recommendations.

## Features

- Dashboard with market overview
- Portfolio management
- AI-powered trade recommendations
- YOLO automated trading mode
- Social feed integration
- Performance tracking
- Dark mode support
- Offline capability

## Installation

### Prerequisites

- Node.js 14+
- npm 6+
- Python 3.8+

### Setup

1. Clone this repository
2. Install dependencies:
```bash
cd simple-kalshi-frontend
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Build the application:
```bash
./build.sh
```

## Configuration

Configure the application through the Settings page:

- Backend URL: URL of the FastAPI backend server (default: http://127.0.0.1:3001)
- Kalshi API credentials: Your Kalshi API key ID and private key
- OpenAI API key: For AI-powered recommendations
- Refresh interval: How often to refresh market data
- Dark/Light mode: Toggle theme

## Architecture

The Kalshi Trading Dashboard consists of two main components:

1. **Electron Frontend** (this repository): A React-based UI that provides a user interface for trading and managing your portfolio.
2. **FastAPI Backend**: Handles API communication with Kalshi, processes data, and provides recommendations.

## Development

### Project Structure

```
simple-kalshi-frontend/
├── assets/                  # Application assets
├── public/                  # Static files
├── src/
│   ├── components/          # React components
│   ├── contexts/            # React context providers
│   ├── pages/               # Application pages
│   ├── utils/               # Utility functions
│   ├── App.js               # Main application component
│   ├── index.js             # Entry point for React
│   └── routes.js            # Route definitions
├── main.js                  # Electron main process
├── preload.js               # Electron preload script
├── package.json             # Project configuration
└── build.sh                 # Build script
```

### Building for Production

To build the application for production:

1. Ensure all dependencies are installed:
```bash
cd simple-kalshi-frontend
npm install
```

2. Run the build script:
```bash
./build.sh
```

3. The build process will:
   - Build the React application with optimized production settings
   - Package the application into an Electron executable
   - Create an installer for your platform (macOS, Windows, or Linux)

4. After the build is complete, you'll find the packaged application in the `dist` directory.

For specific platforms:

**macOS:**
```bash
npm run package -- --mac
```

**Windows:**
```bash
npm run package -- --win
```

**Linux:**
```bash
npm run package -- --linux
```

5. Make sure to set up the backend server before running the production build. The application will attempt to connect to the backend at the URL specified in the Settings page.

## License

MIT 