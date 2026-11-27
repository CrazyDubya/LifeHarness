"""A step answer may only target a question in the caller's own thread."""
from app.core.security import get_password_hash
from app.models.question import Answer, Question
from app.models.thread import Thread
from app.models.user import User, UserProfile


def _user(db, email):
    u = User(email=email, password_hash=get_password_hash("testpassword123"))
    db.add(u)
    db.commit()
    db.refresh(u)
    db.add(UserProfile(user_id=u.id, year_of_birth=1990, country="USA",
                       primary_language="English", has_children=False, intensity="balanced"))
    db.commit()
    return u


def _headers(client, u):
    r = client.post("/api/auth/login", json={"email": u.email, "password": "testpassword123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_step_rejects_question_from_another_users_thread(client, db_session):
    a, b = _user(db_session, "a@example.com"), _user(db_session, "b@example.com")
    ta = Thread(user_id=a.id, title="A", root_prompt="r")
    tb = Thread(user_id=b.id, title="B", root_prompt="r")
    db_session.add_all([ta, tb])
    db_session.commit()
    qa = Question(thread_id=ta.id, index_in_thread=0, type="short_answer", text="A question")
    db_session.add(qa)
    db_session.commit()

    resp = client.post(
        f"/api/threads/{tb.id}/step",
        json={"control": "continue",
              "last_answer": {"question_id": str(qa.id), "free_text": "injected"}},
        headers=_headers(client, b),
    )

    assert resp.status_code == 404
    assert db_session.query(Answer).filter(Answer.question_id == qa.id).count() == 0
    hist = client.get(f"/api/threads/{ta.id}/history", headers=_headers(client, a))
    assert hist.json() == []
