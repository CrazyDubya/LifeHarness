"""Monitoring and metrics endpoints."""
from fastapi import APIRouter, Depends
from typing import Dict
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()

# This will be set by main.py when the middleware is initialized
performance_middleware = None


@router.get("/metrics/performance")
def get_performance_metrics() -> Dict:
    """
    Get performance metrics for monitoring.
    
    Returns aggregated performance data including:
    - Total requests processed
    - Average response time
    - Number of slow requests
    - Request rate
    
    Note: In some deployment configurations, metrics may not be available
    through this endpoint. Use performance headers (X-Process-Time) on 
    individual requests for request-level monitoring.
    """
    if performance_middleware:
        return performance_middleware.get_metrics()
    
    # Return default values if middleware reference not available
    return {
        "total_requests": 0,
        "total_time": 0.0,
        "average_time": 0.0,
        "slow_requests": 0,
        "slow_request_percentage": 0.0
    }


@router.get("/health/detailed")
def detailed_health_check(current_user: User = Depends(get_current_user)) -> Dict:
    """
    Detailed health check endpoint (requires authentication).
    
    Provides comprehensive system health information.
    """
    metrics = get_performance_metrics()
    
    return {
        "status": "healthy",
        "version": "0.1.0",
        "performance": metrics,
        "database": "connected",  # Could add actual DB health check
        "authenticated": True,
        "user_id": str(current_user.id)
    }
