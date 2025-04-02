"""
Kalshi API Client Module

This module provides a unified client for interacting with the Kalshi API.
It handles authentication, request signing, and provides methods for all
required API endpoints.
"""

import time
import base64
import json
import logging
from typing import Dict, List, Optional, Any, Union
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("kalshi_api_client")

class KalshiApiClient:
    """
    Unified client for interacting with the Kalshi API.
    Handles authentication, request signing, and provides methods for all required endpoints.
    """
    
    def __init__(
        self, 
        api_key_id: str, 
        private_key_path: str, 
        base_url: str = "https://api.kalshi.com/trade-api/v2",
        demo_mode: bool = False,
        max_retries: int = 3,
        retry_delay: int = 1
    ):
        """
        Initialize the Kalshi API client.
        
        Args:
            api_key_id: The Kalshi API key ID
            private_key_path: Path to the RSA private key file
            base_url: Base URL for the Kalshi API
            demo_mode: Whether to use the demo environment
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        self.api_key_id = api_key_id
        self.private_key_path = private_key_path
        
        # Use demo URL if in demo mode
        if demo_mode:
            self.base_url = "https://demo-api.kalshi.co/trade-api/v2"
        else:
            self.base_url = base_url
            
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.private_key = None
        
        # Load the private key
        self._load_private_key()
        
        logger.info(f"Initialized Kalshi API client with base URL: {self.base_url}")
        
    def _load_private_key(self) -> None:
        """Load the RSA private key from file."""
        try:
            with open(self.private_key_path, "rb") as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(), 
                    password=None
                )
            logger.info(f"Successfully loaded private key from {self.private_key_path}")
        except Exception as e:
            logger.error(f"Failed to load private key: {str(e)}")
            raise ValueError(f"Failed to load private key: {str(e)}")
    
    def _sign_request(self, method: str, path: str) -> Dict[str, str]:
        """
        Sign a request using RSA-PSS.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            
        Returns:
            Dictionary of headers for the request
        """
        ts = str(int(time.time() * 1000))
        message = ts + method.upper() + path
        
        try:
            signature = self.private_key.sign(
                message.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.DIGEST_LENGTH
                ),
                hashes.SHA256()
            )
            sig_b64 = base64.b64encode(signature).decode('utf-8')
            
            return {
                "KALSHI-ACCESS-KEY": self.api_key_id,
                "KALSHI-ACCESS-TIMESTAMP": ts,
                "KALSHI-ACCESS-SIGNATURE": sig_b64,
                "Content-Type": "application/json"
            }
        except Exception as e:
            logger.error(f"Failed to sign request: {str(e)}")
            raise ValueError(f"Failed to sign request: {str(e)}")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Kalshi API with retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            
        Returns:
            API response as a dictionary
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._sign_request(method, endpoint)
        
        # Convert data to JSON string if provided
        json_data = json.dumps(data) if data else None
        
        retries = 0
        while retries <= self.max_retries:
            try:
                logger.debug(f"Making {method} request to {url}")
                
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    data=json_data
                )
                
                # Log response status
                logger.debug(f"Response status: {response.status_code}")
                
                # Check for rate limiting
                if response.status_code == 429:
                    logger.warning("Rate limited. Retrying after delay.")
                    time.sleep(self.retry_delay * (2 ** retries))  # Exponential backoff
                    retries += 1
                    continue
                
                # Raise for other error status codes
                response.raise_for_status()
                
                # Parse and return JSON response
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {str(e)}")
                
                if retries < self.max_retries:
                    logger.info(f"Retrying ({retries+1}/{self.max_retries})...")
                    time.sleep(self.retry_delay)
                    retries += 1
                else:
                    logger.error("Max retries reached. Giving up.")
                    raise
        
        # This should not be reached, but just in case
        raise RuntimeError("Failed to make request after retries")
    
    # Portfolio endpoints
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Get the user's balance.
        
        Returns:
            Dictionary containing balance information
        """
        return self._make_request("GET", "/portfolio/balance")
    
    def get_positions(self, market_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the user's positions.
        
        Args:
            market_id: Optional market ID to filter positions
            
        Returns:
            Dictionary containing positions information
        """
        params = {"market_id": market_id} if market_id else None
        return self._make_request("GET", "/portfolio/positions", params=params)
    
    def get_fills(
        self, 
        limit: int = 100, 
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the user's trade fills (history).
        
        Args:
            limit: Maximum number of fills to return
            cursor: Pagination cursor
            
        Returns:
            Dictionary containing fills information
        """
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        
        return self._make_request("GET", "/portfolio/fills", params=params)
    
    # Market data endpoints
    
    def get_markets(
        self, 
        status: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get available markets.
        
        Args:
            status: Filter by market status (active, settled, etc.)
            limit: Maximum number of markets to return
            cursor: Pagination cursor
            
        Returns:
            Dictionary containing markets information
        """
        params = {"limit": limit}
        if status:
            params["status"] = status
        if cursor:
            params["cursor"] = cursor
            
        return self._make_request("GET", "/markets", params=params)
    
    def get_market(self, market_id: str) -> Dict[str, Any]:
        """
        Get details for a specific market.
        
        Args:
            market_id: Market ID
            
        Returns:
            Dictionary containing market details
        """
        return self._make_request("GET", f"/markets/{market_id}")
    
    # Trading endpoints
    
    def create_order(
        self,
        market_id: str,
        side: str,  # "yes" or "no"
        type: str,  # "limit" or "market"
        size: int,
        price: Optional[int] = None,  # Required for limit orders, in cents
        client_order_id: Optional[str] = None,
        time_in_force: Optional[str] = None,  # "gtc" (default) or "ioc"
        yes_position: Optional[int] = None,
        no_position: Optional[int] = None,
        reduce_only: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Create a new order.
        
        Args:
            market_id: Market ID
            side: Order side ("yes" or "no")
            type: Order type ("limit" or "market")
            size: Order size
            price: Order price in cents (required for limit orders)
            client_order_id: Optional client-provided order ID
            time_in_force: Time in force ("gtc" or "ioc")
            yes_position: Target yes position
            no_position: Target no position
            reduce_only: Whether the order should only reduce position
            
        Returns:
            Dictionary containing order information
        """
        data = {
            "market_id": market_id,
            "side": side,
            "type": type,
            "size": size
        }
        
        # Add optional parameters if provided
        if price is not None:
            data["price"] = price
        if client_order_id:
            data["client_order_id"] = client_order_id
        if time_in_force:
            data["time_in_force"] = time_in_force
        if yes_position is not None:
            data["yes_position"] = yes_position
        if no_position is not None:
            data["no_position"] = no_position
        if reduce_only is not None:
            data["reduce_only"] = reduce_only
            
        return self._make_request("POST", "/portfolio/orders", data=data)
    
    def get_orders(
        self,
        market_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the user's orders.
        
        Args:
            market_id: Optional market ID to filter orders
            status: Optional status to filter orders
            limit: Maximum number of orders to return
            cursor: Pagination cursor
            
        Returns:
            Dictionary containing orders information
        """
        params = {"limit": limit}
        if market_id:
            params["market_id"] = market_id
        if status:
            params["status"] = status
        if cursor:
            params["cursor"] = cursor
            
        return self._make_request("GET", "/portfolio/orders", params=params)
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get details for a specific order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Dictionary containing order details
        """
        return self._make_request("GET", f"/portfolio/orders/{order_id}")
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Dictionary containing cancellation result
        """
        return self._make_request("DELETE", f"/portfolio/orders/{order_id}")
    
    # Exchange information endpoints
    
    def get_exchange_status(self) -> Dict[str, Any]:
        """
        Get the exchange status.
        
        Returns:
            Dictionary containing exchange status information
        """
        return self._make_request("GET", "/exchange/status")
