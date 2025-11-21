from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class ThreadCreate(BaseModel):
    title: str
    root_prompt: str
    persona: Optional[str] = None
    time_focus: Optional[List[str]] = None
    topic_focus: Optional[List[str]] = None


class ThreadOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    root_prompt: str
    persona: str
    time_focus: Optional[List[str]]
    topic_focus: Optional[List[str]]
    questions_asked: int
    questions_since_last_freeform: int
    created_at: datetime
    last_activity_at: datetime

    class Config:
        from_attributes = True


class ThreadFreeformOut(BaseModel):
    id: UUID
    thread_id: UUID
    index_in_thread: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True
