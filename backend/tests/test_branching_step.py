"""Integration: the step endpoint runs pool -> Jev rank -> present."""
import pytest
from unittest.mock import AsyncMock, patch

from app.models.thread import Thread
from app.services import candidate_pool
from app.services import jev_decider


@pytest.fixture
def profile_client(client, db_session, test_user_with_profile):
    user, profile = test_user_with_profile
    resp = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "testpassword123"},
    )
    token = resp.json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}, user, profile


@pytest.fixture
def thread(db_session, test_user_with_profile):
    user, _ = test_user_with_profile
    t = Thread(user_id=user.id, title="Growing up",
               root_prompt="Tell me about childhood")
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


def _fake_candidates():
    return [
        {"text": "Q deep?", "type": "short_answer", "move": "go_deeper",
         "time_focus": ["10s"], "topic_focus": ["family_of_origin"]},
        {"text": "Q gap?", "type": "multiple_choice",
         "options": [{"id": "A", "text": "x"}],
         "move": "pivot_to_gap",
         "time_focus": ["20s"], "topic_focus": ["work_career"]},
    ]


@pytest.mark.asyncio
async def test_step_presents_jev_winner(profile_client, thread, db_session):
    client, headers, _, _ = profile_client

    with patch.object(
        candidate_pool.llm_orchestrator, "generate_candidates",
        new=AsyncMock(return_value=_fake_candidates()),
    ), patch.object(
        jev_decider, "_call_jev",
        new=AsyncMock(return_value={
            "pick": {"choice": "x", "confidence": 0.75,
                     "probabilities": {}}
        }),
    ):
        # probabilities keyed by candidate id — fill after generation
        resp = client.post(f"/api/threads/{thread.id}/step",
                           json={"control": "continue"}, headers=headers)

    # The mocked Jev probabilities were empty, so both candidates score 0.0
    # and stable order picks the first stored one.
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["done"] is False
    assert body["question"]["text"] == "Q deep?"
    assert body["move"] == "go_deeper"
    assert body["decision_source"] == "jev"
    assert body["jev_confidence"] == 0.75


@pytest.mark.asyncio
async def test_step_falls_back_to_freeform_when_llm_down(
    profile_client, thread
):
    client, headers, _, _ = profile_client
    with patch.object(
        candidate_pool.llm_orchestrator, "generate_candidates",
        new=AsyncMock(return_value=[]),
    ):
        resp = client.post(f"/api/threads/{thread.id}/step",
                           json={"control": "continue"}, headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["done"] is False
    assert body["question"]["type"] == "short_answer"
    assert body["decision_source"] == "fallback_no_candidates"
    # series suggestion is optional; a fresh thread must not suggest ending
    assert body["series_suggestion"] is None
