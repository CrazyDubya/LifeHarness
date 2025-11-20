from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from app.models.enums import VisibilityLevel, SealType


class LifeEntryOut(BaseModel):
    id: UUID
    user_id: UUID
    thread_id: Optional[UUID]
    source_question_id: Optional[UUID]
    time_bucket: str
    approx_year_start: Optional[int]
    approx_year_end: Optional[int]
    timeframe_label: str
    headline: str
    raw_text: str
    distilled: str
    tags: Optional[List[str]]
    topic_buckets: Optional[List[str]]
    visibility: str
    seal_type: str
    seal_release_at: Optional[datetime]
    seal_event_key: Optional[str]
    seal_audiences_blocked: Optional[List[str]]
    emotional_tone: Optional[str]
    people: Optional[List[str]]
    locations: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SealUpdateIn(BaseModel):
    visibility: Optional[VisibilityLevel] = None
    seal_type: Optional[SealType] = None
    seal_release_at: Optional[datetime] = None
    seal_event_key: Optional[str] = None
    seal_audiences_blocked: Optional[List[str]] = None


class CoverageGridOut(BaseModel):
    user_id: UUID
    time_bucket: str
    topic_bucket: str
    score: int

    class Config:
        from_attributes = True
