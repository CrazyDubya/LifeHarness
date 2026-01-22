"""Unit tests for thread management."""
import pytest
from app.models.thread import Thread


def test_create_thread(client, auth_headers, db_session):
    """Test creating a new thread."""
    thread_data = {
        "title": "My College Years",
        "root_prompt": "Tell me about your experiences in college"
    }
    
    response = client.post(
        "/api/threads",
        json=thread_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My College Years"
    assert data["root_prompt"] == thread_data["root_prompt"]
    assert "id" in data
    # ThreadOut doesn't have a status field, it has questions_asked
    assert data["questions_asked"] == 0


def test_list_threads(client, auth_headers, test_user, db_session):
    """Test listing user's threads."""
    # Create a couple of threads
    thread1 = Thread(
        user_id=test_user.id,
        title="Thread 1",
        root_prompt="First thread"
    )
    thread2 = Thread(
        user_id=test_user.id,
        title="Thread 2",
        root_prompt="Second thread"
    )
    db_session.add(thread1)
    db_session.add(thread2)
    db_session.commit()
    
    response = client.get("/api/threads", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] in ["Thread 1", "Thread 2"]


def test_get_single_thread(client, auth_headers, test_user, db_session):
    """Test getting a specific thread."""
    thread = Thread(
        user_id=test_user.id,
        title="Test Thread",
        root_prompt="Test prompt"
    )
    db_session.add(thread)
    db_session.commit()
    db_session.refresh(thread)
    
    response = client.get(f"/api/threads/{thread.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # The API returns id as string representation of UUID
    assert data["id"] == str(thread.id)
    assert data["title"] == "Test Thread"


def test_thread_unauthorized_access(client, test_user, db_session):
    """Test that threads can't be accessed without authentication."""
    thread = Thread(
        user_id=test_user.id,
        title="Private Thread",
        root_prompt="Should not be accessible"
    )
    db_session.add(thread)
    db_session.commit()
    db_session.refresh(thread)
    
    response = client.get(f"/api/threads/{thread.id}")
    # FastAPI returns 403 when credentials are invalid
    assert response.status_code in [401, 403]
