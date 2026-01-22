"""Unit tests for user profile endpoints."""
import pytest


def test_get_profile_unauthenticated(client):
    """Test that getting profile without auth fails."""
    response = client.get("/api/profile")
    # Note: 403 is returned by FastAPI when credentials are invalid
    assert response.status_code in [401, 403]


def test_create_profile(client, auth_headers):
    """Test profile creation."""
    profile_data = {
        "year_of_birth": 1985,
        "country": "Canada",
        "primary_language": "English",
        "has_children": True,
        "intensity": "deep",
        "life_snapshot": "A software engineer living in Toronto."
    }
    
    response = client.post(
        "/api/profile",
        json=profile_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["year_of_birth"] == 1985
    assert data["country"] == "Canada"
    assert data["has_children"] is True


def test_get_profile(client, test_user_with_profile, db_session):
    """Test getting existing profile."""
    user, profile = test_user_with_profile
    
    # Login to get token
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": user.email,
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/profile", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["year_of_birth"] == 1990
    assert data["country"] == "USA"
    assert data["has_children"] is False


def test_update_profile(client, test_user_with_profile, db_session):
    """Test updating an existing profile."""
    user, profile = test_user_with_profile
    
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": user.email,
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Update profile
    update_data = {
        "year_of_birth": 1990,
        "country": "Mexico",
        "primary_language": "Spanish",
        "has_children": True,
        "intensity": "light"
    }
    
    response = client.post(
        "/api/profile",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["country"] == "Mexico"
    assert data["primary_language"] == "Spanish"
    assert data["has_children"] is True
    assert data["intensity"] == "light"
