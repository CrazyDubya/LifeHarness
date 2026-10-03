"""Tests for the latency guards: generation timeout and thread pre-warm."""
import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest

from app.models.thread import Thread
from app.models.question import QuestionCandidate
from app.services import candidate_pool
from app.core import database


@pytest.fixture
def thread(db_session, test_user_with_profile):
    user, _ = test_user_with_profile
    t = Thread(
        user_id=user.id,
        title="Growing up",
        root_prompt="Tell me about childhood",
    )
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


def _cand(**kw):
    base = {
        "text": "A question?",
        "type": "multiple_choice",
        "options": [{"id": "A", "text": "Yes"}, {"id": "OTHER", "text": "Other"}],
        "time_focus": ["20s"],
        "topic_focus": ["work_career"],
        "move": "pivot_to_gap",
    }
    base.update(kw)
    return base


def _persona():
    return {"name": "Test", "voice": "plain", "probing_style": "direct"}


async def _slow_call(*args, **kwargs):
    await asyncio.sleep(30)
    return None


@pytest.mark.asyncio
async def test_generate_candidates_timeout_returns_empty_fast(monkeypatch):
    """A stalled Token Broker call is cut off instead of hanging the step."""
    monkeypatch.setattr(
        "app.services.llm_orchestrator.settings.CANDIDATE_GEN_TIMEOUT_S", 0.2
    )
    with patch.object(
        candidate_pool.llm_orchestrator, "_call_api", new=AsyncMock(side_effect=_slow_call)
    ):
        start = time.monotonic()
        result = await candidate_pool.llm_orchestrator.generate_candidates(
            thread_root="Growing up",
            profile_summary={},
            recent_qa=[],
            coverage_gaps=[],
            allowed_time_buckets=["10s"],
            allowed_topic_buckets=["work_career"],
            persona=_persona(),
            count=4,
        )
        elapsed = time.monotonic() - start
    assert result == []
    assert elapsed < 5, f"timeout did not fire promptly ({elapsed:.1f}s)"


@pytest.mark.asyncio
async def test_ensure_pool_uses_existing_pool_when_generation_times_out(
    db_session, thread, test_user_with_profile, monkeypatch
):
    """On timeout the step falls back to ranking already-pooled candidates."""
    _, profile = test_user_with_profile
    candidate_pool.store_candidates(
        db_session, thread.id, [_cand(text="Q1"), _cand(text="Q2")]
    )
    monkeypatch.setattr(
        "app.services.llm_orchestrator.settings.CANDIDATE_GEN_TIMEOUT_S", 0.2
    )
    with patch.object(
        candidate_pool.llm_orchestrator, "_call_api", new=AsyncMock(side_effect=_slow_call)
    ):
        pooled = await candidate_pool.ensure_pool(
            db_session, thread, profile, context={
                "thread_root": "Growing up",
                "profile_summary": {},
                "recent_qa": [],
                "coverage_gaps": [],
                "allowed_time_buckets": ["10s"],
                "allowed_topic_buckets": ["work_career"],
            },
        )
    assert len(pooled) == 2  # existing pool, no fresh candidates, no hang


def _patch_session_local(db_session):
    """Route warm_pool_for_thread's private session at the test database."""
    return patch.object(database, "SessionLocal", return_value=db_session)


def test_warm_pool_fills_empty_thread(db_session, thread, test_user_with_profile):
    user, _ = test_user_with_profile
    thread_id = thread.id  # capture before warm closes its (shared, in tests) session
    fake = [_cand(text="Warm Q1"), _cand(text="Warm Q2", move="go_deeper")]
    with (
        _patch_session_local(db_session),
        patch.object(
            candidate_pool.llm_orchestrator,
            "generate_candidates",
            new=AsyncMock(return_value=fake),
        ) as mock_gen,
    ):
        stored = candidate_pool.warm_pool_for_thread(thread_id, user.id)
    assert mock_gen.await_count == 1
    assert stored == 2
    assert len(candidate_pool.get_pooled(db_session, thread_id)) == 2


def test_warm_pool_skips_when_pool_exists(db_session, thread, test_user_with_profile):
    user, _ = test_user_with_profile
    thread_id = thread.id
    candidate_pool.store_candidates(db_session, thread_id, [_cand(text="Q1")])
    with (
        _patch_session_local(db_session),
        patch.object(
            candidate_pool.llm_orchestrator,
            "generate_candidates",
            new=AsyncMock(return_value=[_cand()]),
        ) as mock_gen,
    ):
        stored = candidate_pool.warm_pool_for_thread(thread_id, user.id)
    assert stored == 0
    assert mock_gen.await_count == 0
    assert len(candidate_pool.get_pooled(db_session, thread_id)) == 1


def test_warm_pool_never_raises(db_session, thread, test_user_with_profile):
    user, _ = test_user_with_profile
    thread_id = thread.id
    with (
        _patch_session_local(db_session),
        patch(
            "app.services.question_engine.build_step_context",
            side_effect=RuntimeError("boom"),
        ),
    ):
        assert candidate_pool.warm_pool_for_thread(thread_id, user.id) == 0


def test_warm_pool_unknown_thread_returns_zero(db_session, test_user_with_profile):
    from uuid import uuid4

    user, _ = test_user_with_profile
    with _patch_session_local(db_session):
        assert candidate_pool.warm_pool_for_thread(uuid4(), user.id) == 0
