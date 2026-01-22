"""Integration tests for the complete authentication flow."""
import pytest


def test_complete_registration_and_login_flow(client):
    """Test the complete user journey from registration to login."""
    # Step 1: Register a new user
    registration_data = {
        "email": "integration@example.com",
        "password": "IntegrationTest123!"
    }
    
    reg_response = client.post("/api/auth/register", json=registration_data)
    assert reg_response.status_code == 200
    reg_data = reg_response.json()
    assert "access_token" in reg_data
    first_token = reg_data["access_token"]
    
    # Step 2: Create a profile with the first token
    headers = {"Authorization": f"Bearer {first_token}"}
    profile_data = {
        "year_of_birth": 1985,
        "country": "USA",
        "primary_language": "English",
        "has_children": False,
        "intensity": "balanced"
    }
    
    profile_response = client.post(
        "/api/profile",
        json=profile_data,
        headers=headers
    )
    assert profile_response.status_code == 200
    
    # Step 3: Login again with same credentials
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": registration_data["email"],
            "password": registration_data["password"]
        }
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    second_token = login_data["access_token"]
    
    # Step 4: Retrieve profile with new token
    new_headers = {"Authorization": f"Bearer {second_token}"}
    get_profile_response = client.get("/api/profile", headers=new_headers)
    assert get_profile_response.status_code == 200
    retrieved_profile = get_profile_response.json()
    assert retrieved_profile["year_of_birth"] == 1985
    assert retrieved_profile["country"] == "USA"


def test_complete_thread_workflow(client, auth_headers, db_session):
    """Test creating thread, listing threads, and retrieving a specific thread."""
    # Step 1: Create first thread
    thread1_data = {
        "title": "My Childhood",
        "root_prompt": "Tell me about your childhood experiences"
    }
    
    create_response1 = client.post(
        "/api/threads",
        json=thread1_data,
        headers=auth_headers
    )
    assert create_response1.status_code == 200
    thread1 = create_response1.json()
    thread1_id = thread1["id"]
    
    # Step 2: Create second thread
    thread2_data = {
        "title": "My Career",
        "root_prompt": "Tell me about your career journey"
    }
    
    create_response2 = client.post(
        "/api/threads",
        json=thread2_data,
        headers=auth_headers
    )
    assert create_response2.status_code == 200
    thread2 = create_response2.json()
    thread2_id = thread2["id"]
    
    # Step 3: List all threads
    list_response = client.get("/api/threads", headers=auth_headers)
    assert list_response.status_code == 200
    threads = list_response.json()
    assert len(threads) == 2
    thread_ids = [t["id"] for t in threads]
    assert thread1_id in thread_ids
    assert thread2_id in thread_ids
    
    # Step 4: Get specific thread
    get_response = client.get(f"/api/threads/{thread1_id}", headers=auth_headers)
    assert get_response.status_code == 200
    retrieved_thread = get_response.json()
    assert retrieved_thread["id"] == thread1_id
    assert retrieved_thread["title"] == "My Childhood"
    assert retrieved_thread["root_prompt"] == thread1_data["root_prompt"]


def test_profile_update_persistence(client, auth_headers):
    """Test that profile updates are persisted correctly."""
    # Step 1: Create initial profile
    initial_profile = {
        "year_of_birth": 1990,
        "country": "Canada",
        "primary_language": "English",
        "has_children": False,
        "intensity": "light"
    }
    
    create_response = client.post(
        "/api/profile",
        json=initial_profile,
        headers=auth_headers
    )
    assert create_response.status_code == 200
    
    # Step 2: Retrieve it
    get_response1 = client.get("/api/profile", headers=auth_headers)
    assert get_response1.status_code == 200
    profile1 = get_response1.json()
    assert profile1["country"] == "Canada"
    assert profile1["has_children"] is False
    
    # Step 3: Update profile
    updated_profile = {
        "year_of_birth": 1990,
        "country": "Mexico",
        "primary_language": "Spanish",
        "has_children": True,
        "intensity": "deep"
    }
    
    update_response = client.post(
        "/api/profile",
        json=updated_profile,
        headers=auth_headers
    )
    assert update_response.status_code == 200
    
    # Step 4: Retrieve again and verify changes
    get_response2 = client.get("/api/profile", headers=auth_headers)
    assert get_response2.status_code == 200
    profile2 = get_response2.json()
    assert profile2["country"] == "Mexico"
    assert profile2["primary_language"] == "Spanish"
    assert profile2["has_children"] is True
    assert profile2["intensity"] == "deep"
