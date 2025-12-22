import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.thread import Thread, ThreadFreeform
from app.models.question import Question, Answer
from app.models.life_entry import LifeEntry
from app.models.user import UserProfile
from app.services.llm_orchestrator import llm_orchestrator
from app.services.coverage_service import get_coverage_slice
from app.services.agent_personalities import get_persona, DEFAULT_PERSONA_KEY


def select_next_target(
    coverage_slice: Dict[str, Dict[str, int]],
    recent_questions: List[Question]
) -> Optional[Dict[str, Any]]:
    """Pick the next time/topic slice to focus on.

    Prefers the lowest-scored coverage slice that hasn't been asked about in the
    most recent questions. If all low slices were recently asked, returns the
    lowest overall.
    """

    candidates: List[tuple[str, str, int]] = []
    for time_bucket, topics in coverage_slice.items():
        for topic_bucket, score in topics.items():
            candidates.append((time_bucket, topic_bucket, score))

    if not candidates:
        return None

    # Track recently asked time/topic pairs
    recent_pairs = set()
    for question in recent_questions:
        times = question.time_focus or []
        topics = question.topic_focus or []
        if not times or not topics:
            continue
        for time_bucket in times:
            for topic_bucket in topics:
                recent_pairs.add((time_bucket, topic_bucket))

    candidates.sort(key=lambda c: (c[2], c[0], c[1]))

    for time_bucket, topic_bucket, score in candidates:
        if (time_bucket, topic_bucket) not in recent_pairs:
            return {
                "time_bucket": time_bucket,
                "topic_bucket": topic_bucket,
                "score": score
            }

    # Fall back to the lowest-scored slice even if recently asked
    time_bucket, topic_bucket, score = candidates[0]
    return {
        "time_bucket": time_bucket,
        "topic_bucket": topic_bucket,
        "score": score
    }


def should_inject_freeform(thread: Thread) -> bool:
    """Determine if we should inject a freeform prompt"""
    n = thread.questions_since_last_freeform
    if n < 5:
        return False
    # Random threshold between 5-10
    threshold = random.randint(5, 10)
    return n >= threshold


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


def create_freeform_question(
    db: Session,
    thread: Thread,
    index: int
) -> Question:
    """Create a freeform reflection question"""
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


async def generate_next_question(
    db: Session,
    thread: Thread,
    profile: UserProfile
) -> Optional[Question]:
    """Generate the next question for a thread using LLM"""

    # Get recent Q&A
    recent_questions = db.query(Question).filter(
        Question.thread_id == thread.id
    ).order_by(Question.index_in_thread.desc()).limit(5).all()

    recent_qa = []
    for q in reversed(recent_questions):
        answer = db.query(Answer).filter(Answer.question_id == q.id).first()
        if answer:
            answer_text = answer.free_text or f"Choice: {answer.choice_id}"
            recent_qa.append({"q": q.text, "a": answer_text})

    # Get thread freeforms
    freeforms = db.query(ThreadFreeform).filter(
        ThreadFreeform.thread_id == thread.id
    ).all()

    thread_freeforms = [
        {"index": f.index_in_thread, "text": f.text}
        for f in freeforms
    ]

    # Get allowed buckets
    allowed_time, allowed_topics = get_allowed_buckets(profile, thread)

    # Get coverage and choose next target slice
    coverage_slice = get_coverage_slice(db, profile.user_id, allowed_time, allowed_topics)
    target_focus = select_next_target(coverage_slice, recent_questions)

    # Persona metadata
    persona = get_persona(thread.persona or DEFAULT_PERSONA_KEY)

    # Build profile summary
    current_year = datetime.now().year
    user_age = current_year - profile.year_of_birth if profile.year_of_birth else None

    profile_summary = {
        "age": user_age,
        "has_children": profile.has_children or False,
        "avoid_topics": profile.avoid_topics or [],
        "intensity": profile.intensity or "balanced"
    }

    context_digest = build_context_digest(db, thread, allowed_time, allowed_topics)

    # Call LLM
    result = await llm_orchestrator.generate_question(
        thread_root=f"{thread.title}: {thread.root_prompt}",
        profile_summary=profile_summary,
        thread_freeforms=thread_freeforms,
        recent_qa=recent_qa,
        coverage_slice=coverage_slice,
        context_digest=context_digest,
        allowed_time_buckets=allowed_time,
        allowed_topic_buckets=allowed_topics,
        persona=persona,
        target_focus=target_focus
    )

    if not result or "question" not in result:
        return None

    q_data = result["question"]

    # Persist the targeted focus even if the LLM omits it
    raw_time_focus = q_data.get("time_focus")
    raw_topic_focus = q_data.get("topic_focus")

    time_focus = (
        list(raw_time_focus)
        if isinstance(raw_time_focus, list)
        else [raw_time_focus]
        if isinstance(raw_time_focus, str)
        else []
    )
    topic_focus = (
        list(raw_topic_focus)
        if isinstance(raw_topic_focus, list)
        else [raw_topic_focus]
        if isinstance(raw_topic_focus, str)
        else []
    )

    if target_focus:
        if target_focus["time_bucket"] not in time_focus:
            time_focus = time_focus + [target_focus["time_bucket"]]
        if target_focus["topic_bucket"] not in topic_focus:
            topic_focus = topic_focus + [target_focus["topic_bucket"]]

    # Create question
    question = Question(
        thread_id=thread.id,
        index_in_thread=thread.questions_asked,
        type=q_data.get("type", "multiple_choice"),
        text=q_data["text"],
        options=q_data.get("options"),
        time_focus=time_focus,
        topic_focus=topic_focus,
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question
