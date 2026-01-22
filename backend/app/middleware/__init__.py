"""Performance monitoring middleware for FastAPI."""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor request performance and log slow requests."""
    
    def __init__(self, app: ASGIApp, slow_request_threshold: float = 1.0):
        """
        Initialize performance monitoring middleware.
        
        Args:
            app: The ASGI application
            slow_request_threshold: Threshold in seconds to log slow requests (default: 1.0s)
        """
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.request_count = 0
        self.total_time = 0.0
        self.slow_requests = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process each request and measure performance."""
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Update metrics
        self.request_count += 1
        self.total_time += duration
        
        # Log slow requests
        if duration > self.slow_request_threshold:
            self.slow_requests += 1
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} "
                f"took {duration:.2f}s (threshold: {self.slow_request_threshold}s)"
            )
        else:
            logger.debug(
                f"Request completed: {request.method} {request.url.path} "
                f"in {duration:.3f}s"
            )
        
        # Add performance headers to response
        response.headers["X-Process-Time"] = str(duration)
        response.headers["X-Request-Count"] = str(self.request_count)
        
        return response
    
    def get_metrics(self) -> dict:
        """Get current performance metrics."""
        avg_time = self.total_time / self.request_count if self.request_count > 0 else 0
        return {
            "total_requests": self.request_count,
            "total_time": self.total_time,
            "average_time": avg_time,
            "slow_requests": self.slow_requests,
            "slow_request_percentage": (
                (self.slow_requests / self.request_count * 100) 
                if self.request_count > 0 else 0
            )
        }
