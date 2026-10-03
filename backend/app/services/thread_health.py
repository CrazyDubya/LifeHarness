"""Thread-health matrix: transparent, algorithmic, never forces anything.

Tracks depth, breadth, topic density, and user fatigue per thread. When the
matrix trips, the step response *suggests* wrapping up and proposes the next
series from the biggest coverage gaps. The user decides; Jev has no say here
by design — ending a thread is a suggestion, never a model fiat.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.thread import Thread
from app.models.question import Question, Answer
from app.models.user import UserProfile

# Suggestion thresholds (transparent constants, easy to tune)
MIN_DEPTH_FOR_SUGGESTION = 10      # don't suggest ending a young thread
BREADTH_SATURATION = 6             # distinct time x topic cells touched
DENSITY_SATURATION = 70            # avg coverage in thread focus cells
FATIGUE_LEN_DROP = 0.5            # recent answers < 50% of earlier length
FATIGUE_SKIPS = 3                 # empty answers in recent window


def _thread_answers(db: Session, thread: Thread) -> List[Answer]:
    qids = [q.id for q in db.query(Question).filter(
        Question.thread_id == thread.id).all()]
    if not qids:
        return []
    return (
        db.query(Answer)
        .filter(Answer.question_id.in_(qids))
        .order_by(Answer.created_at.asc())
        .all()
    )


def compute_health(db: Session, thread: Thread) -> Dict[str, Any]:
    """Compute the health matrix for a thread."""
    questions = (
        db.query(Question)
        .filter(Question.thread_id == thread.id)
        .order_by(Question.index_in_thread.asc())
        .all()
    )

    # Breadth: distinct (time, topic) cells the thread's questions touched
    cells = set()
    for q in questions:
        for t in q.time_focus or ["unspecified"]:
            for topic in q.topic_focus or ["open"]:
                cells.add((t, topic))

    answers = _thread_answers(db, thread)
    lengths = [len((a.free_text or "").strip()) for a in answers]
    skips = sum(
        1 for a in answers
        if not (a.free_text or "").strip() and not a.choice_id
    )

    if len(lengths) >= 6:
        recent = sum(lengths[-3:]) / 3
        earlier = sum(lengths[-6:-3]) / 3
        trend = (recent / earlier) if earlier > 0 else 1.0
    elif lengths:
        trend = 1.0
    else:
        trend = 1.0

    avg_len = sum(lengths) / len(lengths) if lengths else 0

    return {
        "depth": thread.questions_asked,
        "breadth": len(cells),
        "cells": sorted(cells),
        "avg_answer_len": round(avg_len, 1),
        "answer_len_trend": round(trend, 2),
        "skips": skips,
        "answers_count": len(answers),
    }


def should_suggest_new_series(
    health: Dict[str, Any],
    focus_density: float,
) -> tuple[bool, str]:
    """Decide whether to suggest wrapping up. Returns (suggest, reason).

    Pure function of the matrix — no model involved.
    """
    if health["depth"] < MIN_DEPTH_FOR_SUGGESTION:
        return False, ""
    saturated = health["breadth"] >= BREADTH_SATURATION
    dense = focus_density >= DENSITY_SATURATION
    tired = (
        health["answer_len_trend"] < FATIGUE_LEN_DROP
        or health["skips"] >= FATIGUE_SKIPS
    )
    if saturated and (dense or tired):
        reasons = []
        if saturated:
            reasons.append(f"covered {health['breadth']} distinct areas")
        if dense:
            reasons.append("focus areas are well documented")
        if tired:
            reasons.append("answers are getting shorter")
        return True, (
            "This thread has " + ", ".join(reasons)
            + " — it may be a good moment to start a fresh series."
        )
    return False, ""


def get_focus_density(
    db: Session,
    thread: Thread,
    coverage_slice: Dict[str, Dict[str, int]],
) -> float:
    """Average coverage score across the thread's focus cells."""
    times = thread.time_focus or list(coverage_slice.keys())
    topics = thread.topic_focus or []
    if not topics:
        topics = list({t for m in coverage_slice.values() for t in m})
    scores = [
        coverage_slice.get(t, {}).get(topic, 0)
        for t in times
        for topic in topics
    ]
    return sum(scores) / len(scores) if scores else 0.0


def propose_next_series(
    coverage_gaps: List[Dict[str, Any]],
    profile: UserProfile,
) -> Optional[Dict[str, Any]]:
    """Propose the next series from the biggest coverage gaps.

    Respects the profile avoid-list and the children rule.
    """
    avoid = set(profile.avoid_topics or [])
    for g in coverage_gaps:
        topic = g["topic_bucket"]
        if topic in avoid:
            continue
        if topic == "children" and not profile.has_children:
            continue
        time_bucket = g["time_bucket"]
        return {
            "title": f"{time_bucket} · {topic.replace('_', ' ')}",
            "time_focus": [time_bucket],
            "topic_focus": [topic],
            "reason": (
                f"Least documented area so far "
                f"(coverage {g['score']}/100)."
            ),
        }
    return None


def series_suggestion(
    db: Session,
    thread: Thread,
    profile: UserProfile,
    coverage_slice: Dict[str, Dict[str, int]],
    coverage_gaps: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Full suggestion payload, or None. Suggestion only — never a force."""
    health = compute_health(db, thread)
    density = get_focus_density(db, thread, coverage_slice)
    suggest, reason = should_suggest_new_series(health, density)
    if not suggest:
        return None
    nxt = propose_next_series(coverage_gaps, profile)
    return {
        "suggest_new_series": True,
        "reason": reason,
        "health": health,
        "next_series": nxt,
    }
