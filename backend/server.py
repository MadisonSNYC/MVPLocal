"""
Entry point for the FastAPI backend application.

This module initializes the FastAPI application and includes all routes.
"""

import logging
from fastapi import FastAPI
from app.main import app
from app.recommendation_routes import router as recommendation_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("server")

# Include recommendation routes
app.include_router(recommendation_router)

# Add startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Kalshi Trading Dashboard API")

# Add shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Kalshi Trading Dashboard API")

if __name__ == "__main__":
    import uvicorn
    import argparse
    from app.config import config
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Kalshi Trading Dashboard API")
    parser.add_argument("--host", type=str, help="Host to bind to")
    parser.add_argument("--port", type=int, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    
    # Get server configuration, command line args override config
    host = args.host if args.host else config.get("server", "host")
    port = args.port if args.port else config.get("server", "port")
    debug = args.debug if args.debug else config.get("server", "debug")
    reload = args.reload if args.reload else config.get("server", "reload")
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("server:app", host=host, port=port, reload=reload)
