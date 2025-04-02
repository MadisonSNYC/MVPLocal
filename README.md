# Kalshi Trading Dashboard

A comprehensive desktop application for trading on the Kalshi prediction markets platform, built with React, Electron, and FastAPI.

## Features

- Kalshi markets data visualization
- Portfolio management
- AI-powered trading recommendations
- Social feed integration
- Performance tracking
- Automated trading strategies
- YOLO trading mode

## Tech Stack

- **Frontend**: React, Electron, Tailwind CSS
- **Backend**: Python FastAPI
- **Data storage**: SQL databases
- **Search**: Elasticsearch
- **AI**: OpenAI API integration

## Setup

1. Clone this repository
2. Install dependencies:
```
npm install
```
3. Start the application in development mode:
```
npm run dev
```

## Building for Production

To build the application for production:

```
./build.sh
```

This will create a packaged application in the `dist` directory.

## Configuration

The application requires the following configuration:

- Kalshi API credentials (API Key ID and Private Key)
- OpenAI API key (for AI-powered recommendations)

These can be configured in the Settings page of the application.

## License

This project is licensed under the MIT License. 