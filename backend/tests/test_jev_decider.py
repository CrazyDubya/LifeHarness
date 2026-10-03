"""Tests for the Jev rank-and-pick decider and its deterministic fallback."""
import pytest
from unittest.mock import AsyncMock, patch

from app.models.thread import Thread
from app.models.question import QuestionCandidate
from app.services import jev_decider
from app.services import candidate_pool


@pytest.fixture
def thread(db_session, test_user):
    t = Thread(
        user_id=test_user.id,
        title="Growing up",
        root_prompt="Tell me about childhood",
        questions_since_last_freeform=3,
    )
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


@pytest.fixture
def profile_summary():
    return {"age": 45, "has_children": True, "avoid_topics": [],
            "intensity": "balanced"}


def _ctx(profile_summary, **kw):
    base = {
        "profile_summary": profile_summary,
        "recent_qa": [],
        "coverage_gaps": [],
        "coverage_slice": {},
        "fatigue": {},
        "recent_moves": [],
    }
    base.update(kw)
    return base


def _stored(db_session, thread, texts):
    cands = [
        {
            "text": t,
            "type": "short_answer",
            "time_focus": ["20s"],
            "topic_focus": ["work_career"],
            "move": "pivot_to_gap",
        }
        for t in texts
    ]
    return candidate_pool.store_candidates(db_session, thread.id, cands)


@pytest.mark.asyncio
async def test_rank_candidates_jev_orders_by_probability(
    db_session, thread, test_user_with_profile, profile_summary
):
    _, profile = test_user_with_profile
    stored = _stored(db_session, thread, ["QA", "QB", "QC"])
    probs = {
        str(stored[0].id): 0.1,
        str(stored[1].id): 0.7,
        str(stored[2].id): 0.2,
    }
    fake_answers = {"pick": {"choice": str(stored[1].id),
                             "confidence": 0.8, "probabilities": probs}}
    with patch.object(
        jev_decider, "_call_jev", new=AsyncMock(return_value=fake_answers)
    ):
        ranked, confidence, source = await jev_decider.rank_candidates(
            db_session, thread, profile, stored, _ctx(profile_summary)
        )
    assert source == "jev"
    assert confidence == 0.8
    assert [c.text for c, _ in ranked] == ["QB", "QC", "QA"]
    assert ranked[0][1] == 0.7


@pytest.mark.asyncio
async def test_rank_candidates_falls_back_when_jev_down(
    db_session, thread, test_user_with_profile, profile_summary
):
    _, profile = test_user_with_profile
    stored = _stored(db_session, thread, ["QA", "QB"])
    ctx = _ctx(
        profile_summary,
        coverage_slice={"20s": {"work_career": 5, "money_status": 90}},
    )
    # QA targets the emptiest cell; QB a saturated one
    stored[0].time_focus, stored[0].topic_focus = ["20s"], ["work_career"]
    stored[1].time_focus, stored[1].topic_focus = ["20s"], ["money_status"]
    db_session.commit()

    with patch.object(jev_decider, "_call_jev", new=AsyncMock(return_value=None)):
        ranked, confidence, source = await jev_decider.rank_candidates(
            db_session, thread, profile, stored, ctx
        )
    assert source == "deterministic_fallback"
    assert ranked[0][0].text == "QA"  # emptiest cell wins


@pytest.mark.asyncio
async def test_fallback_enforces_freeform_cadence(
    db_session, thread, test_user_with_profile, profile_summary
):
    _, profile = test_user_with_profile
    thread.questions_since_last_freeform = 9
    db_session.commit()
    stored = _stored(db_session, thread, ["Gap Q", "Freeform Q"])
    stored[0].move = "pivot_to_gap"
    stored[0].time_focus, stored[0].topic_focus = ["20s"], ["work_career"]
    stored[1].move = "freeform_reflection"
    stored[1].time_focus, stored[1].topic_focus = ["10s"], ["creativity_play"]
    db_session.commit()

    ctx = _ctx(profile_summary,
               coverage_slice={"20s": {"work_career": 50},
                               "10s": {"creativity_play": 80}})
    with patch.object(jev_decider, "_call_jev", new=AsyncMock(return_value=None)):
        ranked, _, source = await jev_decider.rank_candidates(
            db_session, thread, profile, stored, ctx
        )
    assert source == "deterministic_fallback"
    # Freeform is due (9 >= 8): cadence boost beats the coverage gap
    assert ranked[0][0].text == "Freeform Q"


@pytest.mark.asyncio
async def test_single_candidate_shortcut(
    db_session, thread, test_user_with_profile, profile_summary
):
    _, profile = test_user_with_profile
    (only,) = _stored(db_session, thread, ["Only Q"])
    with patch.object(
        jev_decider, "_call_jev", new=AsyncMock()
    ) as mock_jev:
        ranked, confidence, source = await jev_decider.rank_candidates(
            db_session, thread, profile, [only], _ctx(profile_summary)
        )
    assert mock_jev.await_count == 0  # no Jev call needed
    assert ranked == [(only, 1.0)]
    assert source == "jev_single"


@pytest.mark.asyncio
async def test_rank_candidates_empty_pool(
    db_session, thread, test_user_with_profile, profile_summary
):
    _, profile = test_user_with_profile
    ranked, _, source = await jev_decider.rank_candidates(
        db_session, thread, profile, [], _ctx(profile_summary)
    )
    assert ranked == []
    assert source == "deterministic_fallback"


def test_deterministic_rank_move_variety(db_session, thread):
    stored = _stored(db_session, thread, ["A", "B"])
    stored[0].move = "go_deeper"
    stored[1].move = "pivot_to_gap"
    db_session.commit()
    ranked = jev_decider.deterministic_rank(
        stored, {}, thread, recent_moves=["go_deeper", "go_deeper"]
    )
    # Same scores otherwise; the repeated move is penalized
    assert ranked[0][0].text == "B"
