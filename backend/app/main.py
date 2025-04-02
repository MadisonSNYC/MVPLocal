"""
Update to the main FastAPI application to include all new routes.

This module updates the main FastAPI application to include all routes
for the enhanced features: performance tracking, social feed, and YOLO trading.
"""

import logging
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import get_kalshi_client from dependencies to avoid circular imports
from app.dependencies import get_kalshi_client

# Import routes after dependencies to avoid circular imports
from app import recommendation_routes
from app import enhanced_recommendation_routes
from app import yolo_trading_routes
from app import social_feed_routes
from app import performance_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

# Create FastAPI app
app = FastAPI(
    title="Kalshi Trading Dashboard API",
    description="API for the Kalshi Trading Dashboard Electron application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app", "public")

# Serve favicon
@app.get("/favicon.ico")
async def favicon():
    favicon_path = os.path.join(frontend_dir, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return {"status": "favicon not found"}

# Include routers
app.include_router(recommendation_routes.router)
app.include_router(enhanced_recommendation_routes.router, prefix="/enhanced")
app.include_router(yolo_trading_routes.router)
app.include_router(social_feed_routes.router)
app.include_router(performance_routes.router)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Dictionary with status
    """
    return {"status": "ok"}

# Exchange status endpoint
@app.get("/api/exchange/status")
async def get_exchange_status(kalshi_client=Depends(get_kalshi_client)):
    """
    Get Kalshi exchange status.
    
    Args:
        kalshi_client: Kalshi API client instance
        
    Returns:
        Exchange status from Kalshi API
    """
    return kalshi_client.get_exchange_status()

# Mount static files after all API routes are defined
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Catch-all route to serve index.html for any other route - MUST BE LAST
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        return {"detail": "API endpoint not found"}
        
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Not Found"}
