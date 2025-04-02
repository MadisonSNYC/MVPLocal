# Kalshi Trading Dashboard - User Guide

## Introduction

Welcome to the Kalshi Trading Dashboard, a powerful desktop application for trading on Kalshi markets with AI-powered recommendations. This application provides a comprehensive suite of tools for analyzing markets, executing trades, and tracking performance.

## Installation

### System Requirements

- **Operating System**: macOS Sequoia 15.3.1 or later (optimized for MacBook Air M3)
- **Python**: Version 3.10 or higher
- **Disk Space**: At least 500MB of free disk space

### Installation Steps

1. Extract the ZIP archive to a location on your Mac
2. Open Terminal and navigate to the extracted directory
3. Run the installation script:
   ```
   chmod +x install.sh
   ./install.sh
   ```
4. The script will check your system requirements and install necessary dependencies

## Configuration

### API Credentials

The application requires API credentials for Kalshi and OpenAI:

1. **Kalshi API Credentials**:
   - Log in to your Kalshi account
   - Navigate to Account Settings > API Keys
   - Create a new API key and note the API Key ID and Secret

2. **OpenAI API Key**:
   - Log in to your OpenAI account
   - Navigate to API Keys
   - Create a new API key

3. **Entering Credentials in the App**:
   - On first launch, you'll be prompted to enter your API credentials
   - These will be securely stored in the macOS Keychain
   - You can update credentials later in the Settings page

### Demo Mode

If you don't have API credentials or want to test the application without making real trades:

1. Start the application with the demo flag:
   ```
   ./start.sh --demo
   ```
2. Demo mode provides simulated market data, portfolio, and recommendations
3. All trading functionality is simulated, no real trades will be executed

## Getting Started

### Launching the Application

1. Run the start script:
   ```
   ./start.sh
   ```
2. This will start both the backend server and the Electron frontend
3. The application will automatically check for credentials and start in the appropriate mode

### Dashboard Overview

The Dashboard is your central hub for market information:

- **Market Overview**: View current prices and trends for the six target hourly markets
- **Portfolio Summary**: See your current positions and balance
- **Recent Recommendations**: Quick access to the latest AI-powered trade recommendations
- **Market Activity**: Recent trading activity and volume indicators

## Features

### AI-Powered Recommendations

The application provides sophisticated trade recommendations using multiple strategies:

1. **Accessing Recommendations**:
   - Navigate to the Strategies page
   - Select a strategy type (Momentum, Mean-Reversion, Arbitrage, etc.)
   - Adjust risk level (Low, Medium, High)
   - Click "Generate Recommendations"

2. **Understanding Recommendations**:
   - Each recommendation includes:
     - Market information
     - Recommended action (YES/NO)
     - Confidence level
     - Rationale
     - Target exit and stop loss prices

3. **Available Strategies**:
   - **Momentum**: Identifies markets with strong directional movement
   - **Mean-Reversion**: Looks for markets likely to return to average prices
   - **Arbitrage**: Detects price inconsistencies between related markets
   - **Volatility-Based**: Analyzes unusual price volatility patterns
   - **Sentiment-Driven**: Uses social feed data to gauge market sentiment
   - **Hybrid**: Combines multiple strategies for balanced recommendations

### YOLO Automated Trading Mode

YOLO mode allows for automated execution of trades based on AI recommendations:

1. **Configuring YOLO Mode**:
   - Navigate to the YOLO Trading page
   - Set maximum spend per trade
   - Choose risk tolerance level
   - Select preferred strategy
   - Enable YOLO mode

2. **Safety Features**:
   - Maximum spend cap prevents excessive losses
   - Risk tolerance settings adjust trade frequency and size
   - Automatic stop-loss placement
   - Ability to pause or disable at any time

3. **Monitoring YOLO Activity**:
   - Real-time log of automated trading activity
   - Performance metrics for automated trades
   - Email notifications for significant events (optional)

### Social Feed Integration

The Social Feed page provides insights from the Kalshi community:

1. **Activity Feed**:
   - View recent trades and comments from other traders
   - Filter by market or activity type
   - Identify trending markets and popular positions

2. **Market Insights**:
   - Sentiment analysis for each market (bullish/bearish)
   - Activity level indicators
   - Confidence metrics based on community consensus

### Performance Tracking

Track the effectiveness of different trading strategies:

1. **Performance Summary**:
   - Overall win/loss ratio
   - Total profit/loss
   - Number of trades by outcome

2. **Strategy Performance**:
   - Compare effectiveness of different strategies
   - View detailed metrics for each strategy
   - Filter by timeframe (day, week, month, all-time)

3. **Recommendation History**:
   - Complete history of all recommendations
   - Outcome tracking (win/loss)
   - Detailed performance analytics

### Offline Functionality

The application provides intermediate offline capability:

1. **Offline Features**:
   - View cached market data with timestamps
   - Access historical data and portfolio information
   - Review previous recommendations and performance metrics

2. **Synchronization**:
   - Automatic data refresh when connection is restored
   - Notification when returning to online mode

## Advanced Usage

### Command Line Options

The start script supports several command line options:

- `--demo`: Start in demo mode with simulated data
- `--dev`: Start in development mode for debugging
- `--reset`: Reset all settings and credentials
- `--help`: Display help information

### Logs and Troubleshooting

Log files are stored in the `logs` directory:

- `backend.log`: Backend server logs
- `frontend.log`: Electron application logs
- `credential_check.log`: Credential verification logs

If you encounter issues:

1. Check the log files for error messages
2. Ensure your API credentials are correct
3. Verify your internet connection
4. Try running in demo mode to isolate the problem

## Support and Feedback

For support or to provide feedback:

1. Check the documentation in the `docs` directory
2. Review the troubleshooting guide
3. Contact the developer with specific issues

## Legal and Compliance

- This application is for personal use only
- Trading on Kalshi involves financial risk
- The application does not provide financial advice
- AI recommendations should not be the sole basis for trading decisions
- Users are responsible for compliance with all applicable laws and regulations

---

Thank you for using the Kalshi Trading Dashboard! We hope it enhances your trading experience and helps you make more informed decisions.
