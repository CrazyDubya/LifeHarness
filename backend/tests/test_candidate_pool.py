"""Tests for the per-thread candidate pool: store, top-up, condense."""
import pytest
from unittest.mock import AsyncMock, patch

from app.models.thread import Thread
from app.models.question import QuestionCandidate
from app.services import candidate_pool


@pytest.fixture
def thread(db_session, test_user):
    t = Thread(
        user_id=test_user.id,
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


def test_store_and_get_pooled(db_session, thread):
    stored = candidate_pool.store_candidates(
        db_session, thread.id, [_cand(), _cand(move="go_deeper")]
    )
    assert len(stored) == 2
    pooled = candidate_pool.get_pooled(db_session, thread.id)
    assert len(pooled) == 2
    assert all(c.status == "pooled" for c in pooled)


def test_condense_dedupes_same_tags_and_text(db_session, thread):
    # Same move + time + topic + near-identical text: keep higher-probability one
    c1, c2 = candidate_pool.store_candidates(
        db_session, thread.id,
        [_cand(text="What did you do after school?"),
         _cand(text="  what did you DO after school?! ")],
    )
    c1.jev_probability = 0.7
    c2.jev_probability = 0.2
    db_session.commit()

    archived = candidate_pool.condense_pool(db_session, thread.id, cap=25)
    assert archived == 1
    db_session.refresh(c1)
    db_session.refresh(c2)
    assert c1.status == "pooled"
    assert c2.status == "archived"


def test_condense_keeps_distinct_questions_in_same_cell(db_session, thread):
    # Same move + time + topic but genuinely different questions: both survive
    candidate_pool.store_candidates(
        db_session, thread.id,
        [_cand(text="What did you do after school with friends?"),
         _cand(text="Who was the toughest kid on your block?")],
    )
    archived = candidate_pool.condense_pool(db_session, thread.id, cap=25)
    assert archived == 0
    assert len(candidate_pool.get_pooled(db_session, thread.id)) == 2


def test_condense_caps_pool(db_session, thread):
    cands = [
        _cand(text=f"Q{i}", topic_focus=[f"topic_{i}"])
        for i in range(30)
    ]
    stored = candidate_pool.store_candidates(db_session, thread.id, cands)
    # Give the first 25 high probability, last 5 low
    for i, c in enumerate(stored):
        c.jev_probability = 0.9 if i < 25 else 0.1
    db_session.commit()

    archived = candidate_pool.condense_pool(db_session, thread.id, cap=25)
    assert archived == 5
    assert len(candidate_pool.get_pooled(db_session, thread.id)) == 25
    # Low-probability leftovers were archived
    for c in stored[25:]:
        db_session.refresh(c)
        assert c.status == "archived"


def test_condense_noop_when_under_cap(db_session, thread):
    candidate_pool.store_candidates(
        db_session, thread.id,
        [_cand(text="Q1"), _cand(text="Q2", move="go_deeper",
                                 topic_focus=["friendships"])],
    )
    assert candidate_pool.condense_pool(db_session, thread.id, cap=25) == 0
    assert len(candidate_pool.get_pooled(db_session, thread.id)) == 2


def _ctx():
    return {
        "thread_root": "Growing up: Tell me about childhood",
        "profile_summary": {"age": 45},
        "recent_qa": [],
        "coverage_gaps": [],
        "allowed_time_buckets": ["10s", "20s"],
        "allowed_topic_buckets": ["work_career"],
    }


@pytest.mark.asyncio
async def test_top_up_calls_llm(db_session, thread, test_user_with_profile):
    _, profile = test_user_with_profile
    fake = [_cand(text="Fresh Q")]
    with patch.object(
        candidate_pool.llm_orchestrator,
        "generate_candidates",
        new=AsyncMock(return_value=fake),
    ) as mock_gen:
        stored = await candidate_pool.top_up_pool(
            db_session, thread, profile, context=_ctx(),
        )
    assert mock_gen.await_count == 1
    assert len(stored) == 1
    assert stored[0].text == "Fresh Q"


@pytest.mark.asyncio
async def test_ensure_pool_skips_llm_when_healthy(db_session, thread, test_user_with_profile):
    _, profile = test_user_with_profile
    candidate_pool.store_candidates(
        db_session, thread.id, [_cand(text=f"Q{i}") for i in range(10)]
    )
    with patch.object(
        candidate_pool.llm_orchestrator,
        "generate_candidates",
        new=AsyncMock(return_value=[_cand()]),
    ) as mock_gen:
        pooled = await candidate_pool.ensure_pool(
            db_session, thread, profile, context=_ctx(),
        )
    assert mock_gen.await_count == 0
    assert len(pooled) == 10


@pytest.mark.asyncio
async def test_ensure_pool_empty_when_llm_fails(db_session, thread, test_user_with_profile):
    _, profile = test_user_with_profile
    with patch.object(
        candidate_pool.llm_orchestrator,
        "generate_candidates",
        new=AsyncMock(return_value=[]),
    ):
        pooled = await candidate_pool.ensure_pool(
            db_session, thread, profile, context=_ctx(),
        )
    assert pooled == []


def test_mark_presented(db_session, thread):
    (c,) = candidate_pool.store_candidates(db_session, thread.id, [_cand()])
    candidate_pool.mark_presented(db_session, c)
    db_session.refresh(c)
    assert c.status == "presented"
    assert c.presented_at is not None
    assert candidate_pool.get_pooled(db_session, thread.id) == []
