import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import VisibilityLevel, SealType


class LifeEntry(Base):
    __tablename__ = "life_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    thread_id = Column(UUID(as_uuid=True), ForeignKey("threads.id", ondelete="SET NULL"), nullable=True)
    source_question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)

    time_bucket = Column(String, nullable=False)
    approx_year_start = Column(Integer, nullable=True)
    approx_year_end = Column(Integer, nullable=True)
    timeframe_label = Column(String, nullable=False)

    headline = Column(Text, nullable=False)
    raw_text = Column(Text, nullable=False)
    distilled = Column(Text, nullable=False)

    tags = Column(ARRAY(String), nullable=True, default=list)
    topic_buckets = Column(ARRAY(String), nullable=True, default=list)

    visibility = Column(String, nullable=False, default=VisibilityLevel.SELF.value)

    seal_type = Column(String, nullable=False, default=SealType.NONE.value)
    seal_release_at = Column(DateTime, nullable=True)
    seal_event_key = Column(String, nullable=True)
    seal_audiences_blocked = Column(ARRAY(String), nullable=True, default=list)

    emotional_tone = Column(String, nullable=True)
    people = Column(ARRAY(String), nullable=True, default=list)
    locations = Column(ARRAY(String), nullable=True, default=list)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="life_entries")
    thread = relationship("Thread", back_populates="life_entries")
    source_question = relationship("Question", foreign_keys=[source_question_id])
