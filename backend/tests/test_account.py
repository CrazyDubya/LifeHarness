"""Tests for the account data controls: export and deletion."""
from app.models.coverage import CoverageGrid
from app.models.life_entry import LifeEntry
from app.models.question import Answer, Question
from app.models.thread import Thread, ThreadFreeform
from app.models.user import User, UserProfile


def _register(client, email="acct@example.com", password="acctpass123"):
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_export_returns_full_account_data(client, db_session):
    token = _register(client)

    # Seed profile (register already created an empty one — update it), thread
    # with a freeform + question + answer, entry, coverage
    user = db_session.query(User).filter(User.email == "acct@example.com").one()
    profile = db_session.query(UserProfile).filter(UserProfile.user_id == user.id).one()
    profile.country = "USA"
    profile.life_snapshot = "grew up by the sea"
    thread = Thread(user_id=user.id, title="Childhood", root_prompt="tell me about childhood")
    db_session.add(thread)
    db_session.commit()
    db_session.refresh(thread)
    db_session.add(ThreadFreeform(thread_id=thread.id, index_in_thread=0, text="summer at the lake"))
    db_session.add(
        Question(thread_id=thread.id, index_in_thread=0, type="short_answer", text="first memory?")
    )
    db_session.commit()
    question = db_session.query(Question).filter(Question.thread_id == thread.id).one()
    db_session.add(Answer(question_id=question.id, user_id=user.id, free_text="the lake house"))
    db_session.add(
        LifeEntry(
            user_id=user.id,
            thread_id=thread.id,
            time_bucket="10s",
            timeframe_label="10s",
            headline="Lake summers",
            raw_text="summer at the lake",
            distilled="summers at the lake",
            visibility="self",
            seal_type="none",
        )
    )
    db_session.add(CoverageGrid(user_id=user.id, time_bucket="10s", topic_bucket="family_of_origin", score=3))
    db_session.commit()

    resp = client.get("/api/account/export", headers=_headers(token))
    assert resp.status_code == 200
    data = resp.json()

    assert data["user"]["email"] == "acct@example.com"
    assert "password_hash" not in data["user"]
    assert data["profile"]["country"] == "USA"
    assert len(data["threads"]) == 1
    assert data["threads"][0]["title"] == "Childhood"
    assert len(data["threads"][0]["freeforms"]) == 1
    assert len(data["threads"][0]["questions"]) == 1
    assert len(data["threads"][0]["questions"][0]["answers"]) == 1
    assert len(data["life_entries"]) == 1
    assert data["life_entries"][0]["headline"] == "Lake summers"
    assert len(data["coverage_grid"]) == 1


def test_export_requires_auth(client):
    resp = client.get("/api/account/export")
    assert resp.status_code in (401, 403)


def test_delete_account_removes_everything(client, db_session):
    token = _register(client, email="bye@example.com", password="byepass123")
    user = db_session.query(User).filter(User.email == "bye@example.com").one()
    thread = Thread(user_id=user.id, title="T", root_prompt="r")
    db_session.add(thread)
    db_session.commit()
    db_session.add(
        LifeEntry(
            user_id=user.id,
            time_bucket="20s",
            timeframe_label="20s",
            headline="H",
            raw_text="raw",
            distilled="dist",
            visibility="self",
            seal_type="none",
        )
    )
    db_session.add(CoverageGrid(user_id=user.id, time_bucket="20s", topic_bucket="friendships", score=1))
    db_session.commit()

    resp = client.request(
        "DELETE", "/api/account", headers=_headers(token), json={"password": "byepass123"}
    )
    assert resp.status_code == 204

    assert db_session.query(User).filter(User.email == "bye@example.com").count() == 0
    assert db_session.query(UserProfile).filter(UserProfile.user_id == user.id).count() == 0
    assert db_session.query(Thread).filter(Thread.user_id == user.id).count() == 0
    assert db_session.query(LifeEntry).filter(LifeEntry.user_id == user.id).count() == 0
    assert db_session.query(Answer).filter(Answer.user_id == user.id).count() == 0
    assert db_session.query(CoverageGrid).filter(CoverageGrid.user_id == user.id).count() == 0

    # Token is now useless
    resp = client.get("/api/account/export", headers=_headers(token))
    assert resp.status_code == 401


def test_delete_account_rejects_wrong_password(client, db_session):
    token = _register(client, email="keep@example.com", password="keeppass123")
    resp = client.request(
        "DELETE", "/api/account", headers=_headers(token), json={"password": "wrongpass"}
    )
    assert resp.status_code == 401
    assert db_session.query(User).filter(User.email == "keep@example.com").count() == 1
