from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class QuestionPayload(BaseModel):
    id: UUID
    type: Literal["multiple_choice", "short_answer"]
    text: str
    options: Optional[List[Dict[str, str]]] = None


class QuestionOut(BaseModel):
    id: UUID
    thread_id: UUID
    index_in_thread: int
    type: str
    text: str
    options: Optional[List[Dict[str, Any]]]
    time_focus: Optional[List[str]]
    topic_focus: Optional[List[str]]
    requires_children: bool
    min_age: Optional[int]
    max_age: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class AnswerIn(BaseModel):
    question_id: UUID
    choice_id: Optional[str] = None
    free_text: Optional[str] = None


class AnswerOut(BaseModel):
    id: UUID
    question_id: UUID
    user_id: UUID
    choice_id: Optional[str]
    free_text: Optional[str]
    created_at: datetime
    linked_entry_id: Optional[UUID]

    class Config:
        from_attributes = True


class StepIn(BaseModel):
    last_answer: Optional[AnswerIn] = None
    control: Literal["continue", "stop"] = "continue"


class StepOut(BaseModel):
    done: bool
    question: Optional[QuestionPayload] = None
