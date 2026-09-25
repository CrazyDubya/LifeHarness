"""Per-thread candidate question pool.

The LLM generates candidates in batches, tagged by move/time/topic. Candidates
sit in the pool until Jev ranks them each step; the winner is materialized into
a real Question. The pool is condensed when it grows past CANDIDATE_POOL_CAP
(default 25): near-duplicates merge, then lowest-probability leftovers archive.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.thread import Thread
from app.models.user import UserProfile
from app.models.question import QuestionCandidate
from app.services.llm_orchestrator import llm_orchestrator
from app.services.agent_personalities import get_persona, DEFAULT_PERSONA_KEY


def get_pooled(db: Session, thread_id) -> List[QuestionCandidate]:
    """All unused candidates for a thread, oldest first."""
    return (
        db.query(QuestionCandidate)
        .filter(
            QuestionCandidate.thread_id == thread_id,
            QuestionCandidate.status == "pooled",
        )
        .order_by(QuestionCandidate.created_at.asc())
        .all()
    )


def _dedupe_key(c: QuestionCandidate) -> tuple:
    return (
        c.move,
        tuple(sorted(c.time_focus or [])),
        tuple(sorted(c.topic_focus or [])),
    )


def condense_pool(db: Session, thread_id, cap: Optional[int] = None) -> int:
    """Shrink the pool to `cap` entries. Returns number archived.

    Near-duplicate removal always runs (same move + time/topic tags keep only
    the highest-probability one); the cap is enforced only when the pool is
    over it. Transparent and deterministic — no LLM call.
    """
    cap = cap or settings.CANDIDATE_POOL_CAP
    pooled = get_pooled(db, thread_id)
    archived = 0

    # 1. Drop near-duplicates: same move + same time/topic tags.
    seen: Dict[tuple, QuestionCandidate] = {}
    for c in pooled:
        key = _dedupe_key(c)
        existing = seen.get(key)
        if existing is None:
            seen[key] = c
        else:
            # Keep the higher-probability one (None counts as 0)
            keep, drop = (
                (c, existing)
                if (c.jev_probability or 0) > (existing.jev_probability or 0)
                else (existing, c)
            )
            seen[key] = keep
            drop.status = "archived"
            archived += 1

    pooled = [c for c in seen.values() if c.status == "pooled"]

    # 2. Over cap: archive lowest-probability leftovers (oldest ties).
    if len(pooled) > cap:
        pooled.sort(key=lambda c: (c.jev_probability or 0, c.created_at))
        for c in pooled[: len(pooled) - cap]:
            c.status = "archived"
            archived += 1

    if archived:
        db.commit()
    return archived


def store_candidates(
    db: Session,
    thread_id,
    candidates: List[Dict[str, Any]],
) -> List[QuestionCandidate]:
    """Persist freshly generated candidates into the pool."""
    stored = []
    for c in candidates:
        cand = QuestionCandidate(
            thread_id=thread_id,
            text=c["text"],
            type=c.get("type", "multiple_choice"),
            options=c.get("options"),
            time_focus=c.get("time_focus", []),
            topic_focus=c.get("topic_focus", []),
            move=c.get("move", "pivot_to_gap"),
            status="pooled",
        )
        db.add(cand)
        stored.append(cand)
    db.commit()
    for c in stored:
        db.refresh(c)
    return stored


async def top_up_pool(
    db: Session,
    thread: Thread,
    profile: UserProfile,
    context: Dict[str, Any],
    count: Optional[int] = None,
) -> List[QuestionCandidate]:
    """Generate a fresh batch of candidates and store them.

    `context` carries: thread_root, profile_summary, recent_qa, coverage_gaps,
    allowed_time_buckets, allowed_topic_buckets, persona.
    Returns the stored candidates (empty list if the LLM call failed).
    """
    count = count or settings.CANDIDATES_PER_TOPUP
    persona = get_persona(thread.persona or DEFAULT_PERSONA_KEY)

    generated = await llm_orchestrator.generate_candidates(
        thread_root=context["thread_root"],
        profile_summary=context["profile_summary"],
        recent_qa=context.get("recent_qa", []),
        coverage_gaps=context.get("coverage_gaps", []),
        allowed_time_buckets=context["allowed_time_buckets"],
        allowed_topic_buckets=context["allowed_topic_buckets"],
        persona=persona,
        count=count,
    )
    if not generated:
        return []
    return store_candidates(db, thread.id, generated)


async def ensure_pool(
    db: Session,
    thread: Thread,
    profile: UserProfile,
    context: Dict[str, Any],
) -> List[QuestionCandidate]:
    """Guarantee a usable pool: top up when low, condense when over cap."""
    pooled = get_pooled(db, thread.id)

    if len(pooled) < settings.CANDIDATE_POOL_MIN:
        fresh = await top_up_pool(db, thread, profile, context)
        pooled = get_pooled(db, thread.id)
        # LLM failed and pool still empty -> caller falls back to freeform
        if not pooled:
            return []

    if len(pooled) > settings.CANDIDATE_POOL_CAP:
        condense_pool(db, thread.id)
        pooled = get_pooled(db, thread.id)

    return pooled


def mark_presented(db: Session, candidate: QuestionCandidate) -> None:
    candidate.status = "presented"
    candidate.presented_at = datetime.utcnow()
    db.commit()


def record_probabilities(
    db: Session, ranked: List[tuple]
) -> None:
    """Persist Jev's last probabilities on the candidates (drives condense)."""
    for candidate, prob in ranked:
        candidate.jev_probability = prob
    db.commit()
