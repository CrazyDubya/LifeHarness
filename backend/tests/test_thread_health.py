"""Tests for the thread-health matrix: suggest, never force."""
import pytest

from app.models.thread import Thread
from app.models.question import Question, Answer
from app.services import thread_health


@pytest.fixture
def thread(db_session, test_user):
    t = Thread(
        user_id=test_user.id,
        title="Growing up",
        root_prompt="Tell me about childhood",
        time_focus=["10s", "20s"],
        topic_focus=["family_of_origin", "friendships"],
        questions_asked=12,
    )
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


def _add_qa(db_session, thread, user, n, text_len=120, choice=None):
    for i in range(n):
        q = Question(
            thread_id=thread.id,
            index_in_thread=i,
            type="multiple_choice",
            text=f"Q{i}",
            time_focus=["10s"] if i % 2 == 0 else ["20s"],
            topic_focus=["family_of_origin"] if i % 2 == 0 else ["friendships"],
        )
        db_session.add(q)
        db_session.commit()
        db_session.refresh(q)
        a = Answer(
            question_id=q.id,
            user_id=user.id,
            choice_id=choice,
            free_text="x" * text_len if text_len else None,
        )
        db_session.add(a)
    db_session.commit()


def test_compute_health_empty_thread(db_session, thread):
    health = thread_health.compute_health(db_session, thread)
    assert health["depth"] == 12
    assert health["breadth"] == 0
    assert health["answer_len_trend"] == 1.0


def test_compute_health_breadth_and_trend(db_session, thread, test_user):
    # 6 long answers then 3 short ones -> declining trend
    _add_qa(db_session, thread, test_user, 6, text_len=200)
    _add_qa(db_session, thread, test_user, 3, text_len=40)
    health = thread_health.compute_health(db_session, thread)
    assert health["breadth"] == 2  # (10s,family) + (20s,friendships)
    assert health["answer_len_trend"] < thread_health.FATIGUE_LEN_DROP


def test_no_suggestion_for_young_thread(db_session, thread):
    thread.questions_asked = 4
    health = {"depth": 4, "breadth": 10, "answer_len_trend": 0.2, "skips": 5}
    suggest, _ = thread_health.should_suggest_new_series(health, 90.0)
    assert suggest is False


def test_suggestion_when_saturated_and_tired():
    health = {"depth": 15, "breadth": 8, "answer_len_trend": 0.3, "skips": 1}
    suggest, reason = thread_health.should_suggest_new_series(health, 75.0)
    assert suggest is True
    assert "shorter" in reason


def test_no_suggestion_when_fresh_and_broad():
    health = {"depth": 15, "breadth": 8, "answer_len_trend": 1.1, "skips": 0}
    suggest, _ = thread_health.should_suggest_new_series(health, 20.0)
    assert suggest is False


def test_propose_next_series_skips_avoid(test_user_with_profile):
    _, profile = test_user_with_profile
    profile.avoid_topics = ["money_status"]
    gaps = [
        {"time_bucket": "20s", "topic_bucket": "money_status", "score": 0},
        {"time_bucket": "30s", "topic_bucket": "health_body", "score": 5},
    ]
    nxt = thread_health.propose_next_series(gaps, profile)
    assert nxt["topic_focus"] == ["health_body"]
    assert nxt["time_focus"] == ["30s"]


def test_propose_next_series_respects_children_rule(test_user_with_profile):
    _, profile = test_user_with_profile
    assert profile.has_children is False
    gaps = [{"time_bucket": "30s", "topic_bucket": "children", "score": 0}]
    assert thread_health.propose_next_series(gaps, profile) is None


def test_series_suggestion_fires_and_proposes(
    db_session, thread, test_user_with_profile
):
    """Saturated + tired thread -> suggestion with a proposed next series."""
    user, profile = test_user_with_profile
    cells = [("10s", "family_of_origin"), ("20s", "friendships"),
             ("30s", "work_career"), ("20s", "money_status"),
             ("10s", "creativity_play"), ("30s", "beliefs_values")]
    for i, (t, topic) in enumerate(cells * 2):  # 12 questions, 6 cells
        q = Question(
            thread_id=thread.id, index_in_thread=i, type="short_answer",
            text=f"Q{i}", time_focus=[t], topic_focus=[topic],
        )
        db_session.add(q)
        db_session.commit()
        db_session.refresh(q)
        # Short answers -> fatigue trend drops
        db_session.add(Answer(question_id=q.id, user_id=user.id,
                              free_text="ok"))
    thread.questions_asked = 12
    db_session.commit()

    coverage_slice = {
        t: {topic: 85 for _, topic in cells for t in ["10s", "20s", "30s"]}
        for t in ["10s", "20s", "30s"]
    }
    gaps = [{"time_bucket": "40s", "topic_bucket": "health_body", "score": 5}]
    suggestion = thread_health.series_suggestion(
        db_session, thread, profile, coverage_slice, gaps
    )
    assert suggestion is not None
    assert suggestion["suggest_new_series"] is True
    assert suggestion["next_series"]["topic_focus"] == ["health_body"]


def test_series_suggestion_never_forces(db_session, thread, test_user_with_profile):
    """The matrix only ever suggests; the thread itself is untouched."""
    user, profile = test_user_with_profile
    _add_qa(db_session, thread, user, 9, text_len=30)
    coverage_slice = {
        t: {topic: 80 for topic in ["family_of_origin", "friendships"]}
        for t in ["10s", "20s"]
    }
    gaps = [{"time_bucket": "30s", "topic_bucket": "health_body", "score": 5}]
    suggestion = thread_health.series_suggestion(
        db_session, thread, profile, coverage_slice, gaps
    )
    # Either None (not saturated) or a suggestion payload — never an action
    assert suggestion is None or suggestion["suggest_new_series"] is True
    # Thread was not closed, archived, or modified by the matrix
    db_session.refresh(thread)
    assert thread.questions_asked == 12
