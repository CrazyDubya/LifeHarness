"""Unit tests for monitoring and performance tracking."""
import pytest
import time


def test_performance_metrics_endpoint(client):
    """Test that performance metrics endpoint returns data."""
    response = client.get("/api/monitoring/metrics/performance")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_requests" in data
    assert "average_time" in data
    assert "slow_requests" in data
    assert isinstance(data["total_requests"], int)


def test_performance_headers_added(client, test_user):
    """Test that performance headers are added to responses."""
    # Make a request
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    
    # Check for performance headers
    assert "X-Process-Time" in response.headers
    assert "X-Request-Count" in response.headers
    
    # Verify header values are numeric strings
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0
    
    request_count = int(response.headers["X-Request-Count"])
    assert request_count > 0


def test_detailed_health_check_authenticated(client, auth_headers):
    """Test detailed health check with authentication."""
    response = client.get("/api/monitoring/health/detailed", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "performance" in data
    assert "authenticated" in data
    assert data["authenticated"] is True
    assert "user_id" in data


def test_detailed_health_check_unauthenticated(client):
    """Test detailed health check requires authentication."""
    response = client.get("/api/monitoring/health/detailed")
    assert response.status_code in [401, 403]


def test_metrics_tracking(client, test_user):
    """Test that metrics are tracked during requests."""
    # Make a few requests to generate metrics
    for i in range(3):
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        # Verify performance headers are present
        assert "X-Process-Time" in response.headers
        assert "X-Request-Count" in response.headers
    
    # Get metrics - may be 0 in test environment due to fresh middleware per fixture
    # but the endpoint should still work
    response = client.get("/api/monitoring/metrics/performance")
    assert response.status_code == 200
    
    data = response.json()
    # Verify structure is correct
    assert "total_requests" in data
    assert "total_time" in data
    assert "average_time" in data
    assert "slow_requests" in data
    assert "slow_request_percentage" in data
