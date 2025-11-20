from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, UserProfile
from app.models.thread import Thread
from app.models.question import Question, Answer
from app.schemas.thread import ThreadCreate, ThreadOut
from app.schemas.question import StepIn, StepOut, QuestionPayload, AnswerOut
from app.services.question_engine import (
    should_inject_freeform,
    create_freeform_question,
    generate_next_question
)
from app.services.life_entry_service import create_life_entry_from_freeform

router = APIRouter()


@router.post("", response_model=ThreadOut)
def create_thread(
    thread_data: ThreadCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new thread"""
    thread = Thread(
        user_id=user.id,
        title=thread_data.title,
        root_prompt=thread_data.root_prompt,
        time_focus=thread_data.time_focus or [],
        topic_focus=thread_data.topic_focus or [],
    )

    db.add(thread)
    db.commit()
    db.refresh(thread)

    return thread


@router.get("", response_model=List[ThreadOut])
def list_threads(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all user threads"""
    threads = db.query(Thread).filter(
        Thread.user_id == user.id
    ).order_by(Thread.last_activity_at.desc()).all()

    return threads


@router.get("/{thread_id}", response_model=ThreadOut)
def get_thread(
    thread_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get a specific thread"""
    thread = db.query(Thread).filter(
        Thread.id == thread_id,
        Thread.user_id == user.id
    ).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    return thread


@router.post("/{thread_id}/step", response_model=StepOut)
async def thread_step(
    thread_id: UUID,
    step_data: StepIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Execute one step in the thread's infinite question loop"""

    # Get thread
    thread = db.query(Thread).filter(
        Thread.id == thread_id,
        Thread.user_id == user.id
    ).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Get profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Handle stop
    if step_data.control == "stop":
        return StepOut(done=True, question=None)

    # Process last answer if provided
    if step_data.last_answer:
        answer_data = step_data.last_answer

        # Get question
        question = db.query(Question).filter(Question.id == answer_data.question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        # Create answer
        answer = Answer(
            question_id=answer_data.question_id,
            user_id=user.id,
            choice_id=answer_data.choice_id,
            free_text=answer_data.free_text
        )

        # If meaningful text (freeform or elaboration), create life entry
        entry_id = None
        if answer_data.free_text and len(answer_data.free_text.strip()) > 20:
            entry = await create_life_entry_from_freeform(
                db=db,
                user_id=user.id,
                raw_text=answer_data.free_text,
                thread_id=thread.id,
                question_id=question.id
            )
            if entry:
                entry_id = entry.id

        answer.linked_entry_id = entry_id
        db.add(answer)

        # Update thread counters
        thread.questions_asked += 1
        thread.questions_since_last_freeform += 1
        thread.last_activity_at = datetime.utcnow()

        db.commit()

    # Decide next question type
    if should_inject_freeform(thread):
        # Inject freeform
        question = create_freeform_question(db, thread, thread.questions_asked)
        thread.questions_since_last_freeform = 0
        db.commit()
    else:
        # Generate regular question
        question = await generate_next_question(db, thread, profile)

        if not question:
            # Fallback if LLM fails
            question = create_freeform_question(db, thread, thread.questions_asked)
            thread.questions_since_last_freeform = 0
            db.commit()

    # Return next question
    return StepOut(
        done=False,
        question=QuestionPayload(
            id=question.id,
            type=question.type,
            text=question.text,
            options=question.options
        )
    )


@router.get("/{thread_id}/history", response_model=List[AnswerOut])
def get_thread_history(
    thread_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all answers in a thread"""
    thread = db.query(Thread).filter(
        Thread.id == thread_id,
        Thread.user_id == user.id
    ).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    questions = db.query(Question).filter(Question.thread_id == thread_id).all()
    question_ids = [q.id for q in questions]

    answers = db.query(Answer).filter(
        Answer.question_id.in_(question_ids)
    ).order_by(Answer.created_at).all()

    return answers
