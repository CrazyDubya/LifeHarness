import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.thread import Thread, ThreadFreeform
from app.models.question import Question, Answer
from app.models.user import UserProfile
from app.services.llm_orchestrator import llm_orchestrator
from app.services.coverage_service import get_coverage_slice
from app.services.agent_personalities import get_persona, DEFAULT_PERSONA_KEY


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

    # Get coverage
    coverage_slice = get_coverage_slice(db, profile.user_id, allowed_time, allowed_topics)

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

    # Call LLM
    result = await llm_orchestrator.generate_question(
        thread_root=f"{thread.title}: {thread.root_prompt}",
        profile_summary=profile_summary,
        thread_freeforms=thread_freeforms,
        recent_qa=recent_qa,
        coverage_slice=coverage_slice,
        allowed_time_buckets=allowed_time,
        allowed_topic_buckets=allowed_topics,
        persona=persona,
    )

    if not result or "question" not in result:
        return None

    q_data = result["question"]

    # Create question
    question = Question(
        thread_id=thread.id,
        index_in_thread=thread.questions_asked,
        type=q_data.get("type", "multiple_choice"),
        text=q_data["text"],
        options=q_data.get("options"),
        time_focus=q_data.get("time_focus", []),
        topic_focus=q_data.get("topic_focus", []),
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question
