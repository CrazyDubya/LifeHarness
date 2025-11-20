import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("threads.id", ondelete="CASCADE"), nullable=False)
    index_in_thread = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    text = Column(Text, nullable=False)

    options = Column(JSONB, nullable=True)
    time_focus = Column(ARRAY(String), nullable=True, default=list)
    topic_focus = Column(ARRAY(String), nullable=True, default=list)

    requires_children = Column(Boolean, default=False)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    thread = relationship("Thread", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    choice_id = Column(String, nullable=True)
    free_text = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    linked_entry_id = Column(UUID(as_uuid=True), ForeignKey("life_entries.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    question = relationship("Question", back_populates="answers")
    user = relationship("User", back_populates="answers")
    linked_entry = relationship("LifeEntry", foreign_keys=[linked_entry_id])
