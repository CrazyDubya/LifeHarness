"""Jev rank-and-pick over the candidate pool.

Jev sees the pooled candidates (stored unused + fresh) with their tags, the
thread state, coverage gaps, and fatigue signals, and returns a full
probability ranking. The top candidate is presented; the rest stay pooled.

If Jev is unreachable (no key, timeout, HTTP error), a transparent
deterministic fallback ranks by coverage gaps, freeform cadence, and move
variety. The interview loop never blocks on the decider.
"""
from typing import Dict, Any, List, Tuple, Optional
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.thread import Thread
from app.models.user import UserProfile
from app.models.question import QuestionCandidate

BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

# Moves that count as "open reflection" for cadence purposes
FREEFORM_MOVES = {"freeform_reflection"}
# Suggest a freeform at least this often (Jev sees the cadence; the fallback
# enforces it deterministically)
FREEFORM_EVERY_N = 8


def _candidate_summary(c: QuestionCandidate) -> str:
    time = ",".join(c.time_focus or ["unspecified"])
    topic = ",".join(c.topic_focus or ["open"])
    text = (c.text or "")[:220]
    return f"move={c.move} | {time} x {topic} | {text}"


def build_jev_state(
    thread: Thread,
    profile_summary: Dict[str, Any],
    recent_qa: List[Dict[str, str]],
    coverage_gaps: List[Dict[str, Any]],
    fatigue: Dict[str, Any],
) -> str:
    lines = [
        f"Autobiography interview. Thread: '{thread.title}' "
        f"(persona={thread.persona}, intensity={profile_summary.get('intensity', 'balanced')}).",
        f"Profile: age={profile_summary.get('age')}, "
        f"has_children={profile_summary.get('has_children')}, "
        f"avoid={profile_summary.get('avoid_topics', [])}.",
        f"Thread progress: {thread.questions_asked} questions asked, "
        f"{thread.questions_since_last_freeform} since last freeform reflection.",
        f"Fatigue signals: avg_answer_len={fatigue.get('avg_answer_len')}, "
        f"trend={fatigue.get('answer_len_trend')}, skips={fatigue.get('skips')}.",
        "Recent exchanges:",
    ]
    for qa in recent_qa[-3:]:
        lines.append(f"  Q: {qa['q'][:160]}")
        lines.append(f"  A: {qa['a'][:160]}")
    lines.append("Emptiest coverage cells (time x topic = score/100):")
    for g in coverage_gaps[:8]:
        lines.append(f"  {g['time_bucket']} x {g['topic_bucket']} = {g['score']}")
    return "\n".join(lines)


async def _call_jev(state: str, criteria: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """POST a choice question to TypeSafe Jev. Returns the answers map."""
    if not settings.TYPESAFE_API_KEY:
        return None
    body = {
        "model": settings.JEV_MODEL,
        "state": state,
        "questions": {
            "pick": {
                "type": "choice",
                "instructions": (
                    "Rank these candidate next questions for the autobiography "
                    "interview. Prefer the candidate that best balances "
                    "conversational continuity (follow what's warm) with "
                    "steadily filling the emptiest coverage cells, while "
                    "respecting the user's avoid list and fatigue signals."
                ),
                "criteria": criteria,
            }
        },
    }
    headers = {
        "Authorization": f"Bearer {settings.TYPESAFE_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": BROWSER_UA,
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.TYPESAFE_API_BASE_URL.rstrip('/')}/v1/systemone",
                headers=headers,
                json=body,
                timeout=15.0,
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        print(f"Jev API error: {e}")
        return None


def deterministic_rank(
    candidates: List[QuestionCandidate],
    coverage_slice: Dict[str, Dict[str, int]],
    thread: Thread,
    recent_moves: List[str],
) -> List[Tuple[QuestionCandidate, float]]:
    """Transparent fallback ranking when Jev is unreachable.

    Score = coverage-gap weight (emptier cells first) + freeform cadence boost
    + move-variety penalty for repeating the last moves. Normalized to
    pseudo-probabilities.
    """
    scored = []
    for c in candidates:
        score = 0.0
        # Coverage gaps: average "emptiness" (100 - score) over tagged cells
        emptiness = []
        for t in c.time_focus or []:
            for topic in c.topic_focus or []:
                s = (coverage_slice.get(t) or {}).get(topic)
                if s is not None:
                    emptiness.append(100 - s)
        if emptiness:
            score += sum(emptiness) / len(emptiness)
        # Freeform cadence: due every FREEFORM_EVERY_N questions
        if c.move in FREEFORM_MOVES and thread.questions_since_last_freeform >= FREEFORM_EVERY_N:
            score += 60.0
        # Move variety: penalize repeating recent moves
        if recent_moves and c.move in recent_moves[-2:]:
            score -= 25.0
        scored.append((c, score))

    if not scored:
        return []
    # Shift to non-negative and normalize
    minimum = min(s for _, s in scored)
    shifted = [(c, s - minimum + 1.0) for c, s in scored]
    total = sum(s for _, s in shifted)
    ranked = [(c, s / total) for c, s in shifted]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


async def rank_candidates(
    db: Session,
    thread: Thread,
    profile: UserProfile,
    candidates: List[QuestionCandidate],
    context: Dict[str, Any],
) -> Tuple[List[Tuple[QuestionCandidate, float]], float, str]:
    """Rank pooled candidates. Returns (ranked, confidence, source).

    `source` is "jev" or "deterministic_fallback". `context` carries
    profile_summary, recent_qa, coverage_gaps, coverage_slice, fatigue,
    recent_moves.
    """
    if not candidates:
        return [], 0.0, "deterministic_fallback"
    if len(candidates) == 1:
        return [(candidates[0], 1.0)], 1.0, "jev_single"

    state = build_jev_state(
        thread,
        context["profile_summary"],
        context.get("recent_qa", []),
        context.get("coverage_gaps", []),
        context.get("fatigue", {}),
    )
    criteria = {str(c.id): _candidate_summary(c) for c in candidates}

    answers = await _call_jev(state, criteria)
    if answers and "pick" in answers:
        pick = answers["pick"]
        probs = pick.get("probabilities", {})
        confidence = float(pick.get("confidence", 0.0))
        by_id = {str(c.id): c for c in candidates}
        ranked = [
            (by_id[cid], float(probs.get(cid, 0.0)))
            for cid in probs
            if cid in by_id
        ]
        # Any candidate Jev didn't score keeps probability 0, appended last
        for c in candidates:
            if str(c.id) not in probs:
                ranked.append((c, 0.0))
        ranked.sort(key=lambda x: x[1], reverse=True)
        if ranked:
            return ranked, confidence, "jev"

    # Fallback: deterministic, transparent
    ranked = deterministic_rank(
        candidates,
        context.get("coverage_slice", {}),
        thread,
        context.get("recent_moves", []),
    )
    return ranked, 0.0, "deterministic_fallback"
