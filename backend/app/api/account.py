"""Account data controls: full export and account deletion.

Export returns everything the app stores for the authenticated user as JSON
(password hashes are never included). Deletion removes the user row; all
related rows (profile, threads, questions, answers, freeforms, life entries,
coverage grid) are removed by the database cascade rules.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import verify_password
from app.models.coverage import CoverageGrid
from app.models.life_entry import LifeEntry
from app.models.question import Answer, Question
from app.models.thread import Thread, ThreadFreeform
from app.models.user import User, UserProfile

router = APIRouter()


class AccountDeleteIn(BaseModel):
    # Password confirmation is required to delete an account.
    password: str


def _iso(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return value


def _row_to_dict(obj: Any, exclude: Optional[List[str]] = None) -> Dict[str, Any]:
    exclude = set(exclude or [])
    data: Dict[str, Any] = {}
    for column in obj.__table__.columns:
        if column.name in exclude:
            continue
        data[column.name] = _iso(getattr(obj, column.name))
    return data


@router.get("/export")
def export_account_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Export everything the app stores for the current user as JSON."""
    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    )

    threads: List[Dict[str, Any]] = []
    for thread in (
        db.query(Thread).filter(Thread.user_id == user.id).all()
    ):
        thread_dict = _row_to_dict(thread)
        thread_dict["freeforms"] = [
            _row_to_dict(f)
            for f in db.query(ThreadFreeform)
            .filter(ThreadFreeform.thread_id == thread.id)
            .order_by(ThreadFreeform.index_in_thread)
            .all()
        ]
        questions: List[Dict[str, Any]] = []
        for question in (
            db.query(Question)
            .filter(Question.thread_id == thread.id)
            .order_by(Question.index_in_thread)
            .all()
        ):
            question_dict = _row_to_dict(question)
            question_dict["answers"] = [
                _row_to_dict(a)
                for a in db.query(Answer)
                .filter(Answer.question_id == question.id)
                .all()
            ]
            questions.append(question_dict)
        thread_dict["questions"] = questions
        threads.append(thread_dict)

    life_entries = [
        _row_to_dict(e)
        for e in db.query(LifeEntry)
        .filter(LifeEntry.user_id == user.id)
        .order_by(LifeEntry.created_at)
        .all()
    ]

    coverage_grid = [
        _row_to_dict(c)
        for c in db.query(CoverageGrid)
        .filter(CoverageGrid.user_id == user.id)
        .all()
    ]

    return {
        "exported_at": datetime.utcnow().isoformat(),
        "user": _row_to_dict(user, exclude=["password_hash"]),
        "profile": _row_to_dict(profile) if profile else None,
        "threads": threads,
        "life_entries": life_entries,
        "coverage_grid": coverage_grid,
    }


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    payload: AccountDeleteIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete the current account and all of its data.

    Requires the account password as confirmation. Related rows are removed
    through the model's cascade rules; nothing is retained afterwards.
    """
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password confirmation failed",
        )

    db.delete(user)
    db.commit()
    return None
