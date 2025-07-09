import time
import logging
from typing import Dict, List, Optional
from config import RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS

# Configure logging
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, max_requests: int = RATE_LIMIT_MAX_REQUESTS, window_seconds: int = RATE_LIMIT_WINDOW_SECONDS):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
        logger.info(f"Rate limiter initialized: {max_requests} requests per {window_seconds} seconds")
    
    async def check_rate_limit(self, api_key: str) -> bool:
        """
        Check if request is within rate limits
        
        Args:
            api_key: API key to check rate limit for
            
        Returns:
            True if request is allowed, False if rate limited
        """
        current_time = time.time()
        
        # Initialize if first request from this API key
        if api_key not in self.requests:
            self.requests[api_key] = []
        
        # Remove expired timestamps
        self.requests[api_key] = [
            t for t in self.requests[api_key]
            if t > current_time - self.window_seconds
        ]
        
        # Check if under limit
        if len(self.requests[api_key]) < self.max_requests:
            self.requests[api_key].append(current_time)
            return True
        
        # Rate limited
        logger.warning(f"Rate limit exceeded for API key: {api_key[:8]}...")
        return False
    
    def get_remaining_requests(self, api_key: str) -> Dict[str, int]:
        """
        Get remaining requests for an API key
        
        Args:
            api_key: API key to check
            
        Returns:
            Dictionary with remaining requests and reset time
        """
        current_time = time.time()
        
        if api_key not in self.requests:
            return {
                "remaining": self.max_requests,
                "reset_seconds": self.window_seconds
            }
        
        # Remove expired timestamps
        self.requests[api_key] = [
            t for t in self.requests[api_key]
            if t > current_time - self.window_seconds
        ]
        
        # Calculate remaining requests
        remaining = max(0, self.max_requests - len(self.requests[api_key]))
        
        # Calculate reset time
        if self.requests[api_key]:
            oldest_timestamp = min(self.requests[api_key])
            reset_seconds = max(0, self.window_seconds - (current_time - oldest_timestamp))
        else:
            reset_seconds = 0
        
        return {
            "remaining": remaining,
            "reset_seconds": int(reset_seconds)
        }

# Create a rate limiter instance
rate_limiter = RateLimiter() 