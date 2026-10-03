"""Question engine: candidate pool + Jev ranking + health matrix.

Each step:
  1. Build context (recent Q&A, coverage gaps, fatigue, cadence).
  2. Ensure the per-thread candidate pool is stocked (LLM top-up, condense at cap).
  3. Jev ranks the pooled candidates; the winner is materialized into a Question.
  4. The thread-health matrix may suggest (never force) starting a new series.

The old random freeform injection is gone: freeform cadence is a signal Jev
sees and the deterministic fallback enforces.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.thread import Thread, ThreadFreeform
from app.models.question import Question, Answer, QuestionCandidate
from app.models.life_entry import LifeEntry
from app.models.user import UserProfile
from app.services.coverage_service import get_coverage_slice
from app.services.agent_personalities import get_persona, DEFAULT_PERSONA_KEY
from app.services.candidate_pool import (
    ensure_pool,
    mark_presented,
    record_probabilities,
)
from app.services.jev_decider import rank_candidates, FREEFORM_MOVES
from app.services import thread_health


def get_allowed_buckets(profile: UserProfile, thread: Thread) -> tuple[List[str], List[str]]:
    """Determine allowed time and topic buckets based on profile"""
    current_year = datetime.now().year
    user_age = current_year - profile.year_of_birth if profile.year_of_birth else 30

    # Time buckets
    allowed_time = []
    if user_age >= 10:
        allowed_time.append("pre10")
    if user_age >= 10:
        allowed_time.append("10s")
    if user_age >= 20:
        allowed_time.append("20s")
    if user_age >= 30:
        allowed_time.append("30s")
    if user_age >= 40:
        allowed_time.append("40s")
    if user_age >= 50:
        allowed_time.append("50plus")

    # Topic buckets
    all_topics = [
        "family_of_origin", "friendships", "romantic_love", "children",
        "work_career", "money_status", "health_body", "creativity_play",
        "beliefs_values", "crises_turning_points"
    ]

    allowed_topics = []
    avoid_topics = profile.avoid_topics or []

    for topic in all_topics:
        # Skip if in avoid list
        if topic in avoid_topics:
            continue

        # Special rule for children
        if topic == "children":
            # Only allow if user has children OR thread explicitly focuses on children
            if not profile.has_children and "children" not in (thread.topic_focus or []):
                continue

        allowed_topics.append(topic)

    return allowed_time, allowed_topics


def build_context_digest(
    db: Session,
    thread: Thread,
    allowed_time: List[str],
    allowed_topics: List[str]
) -> Dict[str, Any]:
    """Summarize recent life entries and freeforms to maintain continuity"""

    digest: Dict[str, Any] = {"time_topic_summaries": [], "recent_freeforms": []}

    # Recent life entries grouped by time/topic
    recent_entries = (
        db.query(LifeEntry)
        .filter(LifeEntry.user_id == thread.user_id)
        .order_by(LifeEntry.created_at.desc())
        .limit(30)
        .all()
    )

    grouped: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

    for entry in recent_entries:
        if allowed_time and entry.time_bucket not in allowed_time:
            continue

        topics = entry.topic_buckets or ["general"]
        for topic in topics:
            if allowed_topics and topic not in allowed_topics:
                continue

            grouped.setdefault(entry.time_bucket, {}).setdefault(topic, []).append(
                {
                    "headline": entry.headline,
                    "timeframe": entry.timeframe_label,
                    "summary": entry.distilled,
                    "tone": entry.emotional_tone,
                    "tags": entry.tags,
                }
            )

    for time_bucket, topic_map in grouped.items():
        for topic, items in topic_map.items():
            digest["time_topic_summaries"].append(
                {
                    "time_bucket": time_bucket,
                    "topic": topic,
                    "highlights": items[:3],
                }
            )

    # Recent freeforms as contextual notes
    freeforms = (
        db.query(ThreadFreeform)
        .filter(ThreadFreeform.thread_id == thread.id)
        .order_by(ThreadFreeform.index_in_thread.desc())
        .limit(5)
        .all()
    )

    for freeform in reversed(freeforms):
        digest["recent_freeforms"].append(
            {
                "index": freeform.index_in_thread,
                "text": freeform.text[:400],
                "assumed_time": (thread.time_focus or ["unspecified"]),
                "assumed_topics": (thread.topic_focus or ["open"]),
            }
        )

    return digest


def get_recent_qa(db: Session, thread: Thread, limit: int = 5) -> List[Dict[str, str]]:
    recent_questions = db.query(Question).filter(
        Question.thread_id == thread.id
    ).order_by(Question.index_in_thread.desc()).limit(limit).all()

    recent_qa = []
    for q in reversed(recent_questions):
        answer = db.query(Answer).filter(Answer.question_id == q.id).first()
        if answer:
            answer_text = answer.free_text or f"Choice: {answer.choice_id}"
            recent_qa.append({"q": q.text, "a": answer_text})
    return recent_qa


def get_coverage_gaps(
    coverage_slice: Dict[str, Dict[str, int]]
) -> List[Dict[str, Any]]:
    """Flatten the coverage slice into gaps sorted emptiest-first."""
    gaps = [
        {"time_bucket": t, "topic_bucket": topic, "score": score}
        for t, topics in coverage_slice.items()
        for topic, score in topics.items()
    ]
    gaps.sort(key=lambda g: g["score"])
    return gaps


def get_recent_moves(db: Session, thread: Thread, limit: int = 5) -> List[str]:
    presented = (
        db.query(QuestionCandidate)
        .filter(
            QuestionCandidate.thread_id == thread.id,
            QuestionCandidate.status == "presented",
        )
        .order_by(QuestionCandidate.presented_at.desc())
        .limit(limit)
        .all()
    )
    return [c.move for c in reversed(presented)]


def build_profile_summary(profile: UserProfile) -> Dict[str, Any]:
    current_year = datetime.now().year
    user_age = current_year - profile.year_of_birth if profile.year_of_birth else None
    return {
        "age": user_age,
        "has_children": profile.has_children or False,
        "avoid_topics": profile.avoid_topics or [],
        "intensity": profile.intensity or "balanced",
    }


def build_step_context(
    db: Session, thread: Thread, profile: UserProfile
) -> Dict[str, Any]:
    """Assemble everything the pool, Jev, and health matrix need."""
    allowed_time, allowed_topics = get_allowed_buckets(profile, thread)
    coverage_slice = get_coverage_slice(db, profile.user_id, allowed_time, allowed_topics)
    coverage_gaps = get_coverage_gaps(coverage_slice)
    recent_qa = get_recent_qa(db, thread)
    health = thread_health.compute_health(db, thread)
    fatigue = {
        "avg_answer_len": health["avg_answer_len"],
        "answer_len_trend": health["answer_len_trend"],
        "skips": health["skips"],
    }
    profile_summary = build_profile_summary(profile)

    return {
        "thread_root": f"{thread.title}: {thread.root_prompt}",
        "profile_summary": profile_summary,
        "recent_qa": recent_qa,
        "coverage_gaps": coverage_gaps,
        "coverage_slice": coverage_slice,
        "allowed_time_buckets": allowed_time,
        "allowed_topic_buckets": allowed_topics,
        "fatigue": fatigue,
        "recent_moves": get_recent_moves(db, thread),
        "health": health,
    }


def create_freeform_question(
    db: Session,
    thread: Thread,
    index: int
) -> Question:
    """Last-resort fallback: a freeform prompt when generation fails."""
    freeform_prompts = [
        "Take a moment to write about a memory that stands out from this period of your life.",
        "Describe a turning point or significant moment you haven't mentioned yet.",
        "What's something from this time that you want to remember forever?",
        "Write about someone who mattered to you during this period.",
        "Describe a place that was important to you then.",
        "What were you hoping for or dreaming about at this time?",
        "Tell me about a challenge or struggle from this era.",
        "What brought you joy during this period?",
    ]

    import random
    text = random.choice(freeform_prompts)

    question = Question(
        thread_id=thread.id,
        index_in_thread=index,
        type="short_answer",
        text=text,
        options=None,
        time_focus=thread.time_focus,
        topic_focus=thread.topic_focus,
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question


def materialize_candidate(
    db: Session, thread: Thread, candidate: QuestionCandidate
) -> Question:
    """Turn the winning candidate into a real Question."""
    question = Question(
        thread_id=thread.id,
        index_in_thread=thread.questions_asked,
        type=candidate.type,
        text=candidate.text,
        options=candidate.options,
        time_focus=candidate.time_focus,
        topic_focus=candidate.topic_focus,
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    mark_presented(db, candidate)

    # Freeform cadence is tracked off presented moves now
    if candidate.move in FREEFORM_MOVES:
        thread.questions_since_last_freeform = 0
        db.commit()

    return question


async def generate_next_question(
    db: Session,
    thread: Thread,
    profile: UserProfile
) -> Tuple[Question, Dict[str, Any]]:
    """Generate the next question via candidate pool + Jev ranking.

    Returns (question, info) where info carries move, jev_confidence,
    decision_source, and an optional series_suggestion.
    """
    ctx = build_step_context(db, thread, profile)

    pooled = await ensure_pool(db, thread, profile, ctx)

    info: Dict[str, Any] = {
        "move": None,
        "jev_confidence": 0.0,
        "decision_source": "fallback_no_candidates",
        "series_suggestion": None,
    }

    if not pooled:
        question = create_freeform_question(db, thread, thread.questions_asked)
        info["move"] = "freeform_reflection"
    else:
        ranked, confidence, source = await rank_candidates(
            db, thread, profile, pooled, ctx
        )
        if not ranked:
            question = create_freeform_question(db, thread, thread.questions_asked)
            info["move"] = "freeform_reflection"
        else:
            record_probabilities(db, ranked)
            winner = ranked[0][0]
            question = materialize_candidate(db, thread, winner)
            info["move"] = winner.move
            info["jev_confidence"] = confidence
            info["decision_source"] = source

    info["series_suggestion"] = thread_health.series_suggestion(
        db, thread, profile, ctx["coverage_slice"], ctx["coverage_gaps"]
    )

    return question, info
