import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Thread(Base):
    __tablename__ = "threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    root_prompt = Column(Text, nullable=False)
    time_focus = Column(ARRAY(String), nullable=True, default=list)
    topic_focus = Column(ARRAY(String), nullable=True, default=list)

    questions_asked = Column(Integer, nullable=False, default=0)
    questions_since_last_freeform = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_activity_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="threads")
    freeforms = relationship("ThreadFreeform", back_populates="thread", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="thread", cascade="all, delete-orphan")
    life_entries = relationship("LifeEntry", back_populates="thread")


class ThreadFreeform(Base):
    __tablename__ = "thread_freeforms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("threads.id", ondelete="CASCADE"), nullable=False)
    index_in_thread = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    thread = relationship("Thread", back_populates="freeforms")
