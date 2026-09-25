import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.db_types import UUIDType, ArrayType, JSONBType


class QuestionCandidate(Base):
    """A generated-but-not-yet-presented question.

    The LLM generates candidates in batches (spread across moves); Jev ranks
    the pooled candidates each step and the winner is materialized into a
    real Question. Losers stay pooled for future steps; the pool is condensed
    when it grows past CANDIDATE_POOL_CAP.
    """

    __tablename__ = "question_candidates"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUIDType(), ForeignKey("threads.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    type = Column(String, nullable=False, default="multiple_choice")

    options = Column(JSONBType(), nullable=True)
    time_focus = Column(ArrayType(String), nullable=True, default=list)
    topic_focus = Column(ArrayType(String), nullable=True, default=list)

    # Generation move: go_deeper | pivot_to_gap | bridge | freeform_reflection
    move = Column(String, nullable=False, default="pivot_to_gap")

    # Lifecycle: pooled -> presented | archived
    status = Column(String, nullable=False, default="pooled")

    # Last Jev probability assigned to this candidate (used for condense order)
    jev_probability = Column(Float, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    presented_at = Column(DateTime, nullable=True)

    # Relationships
    thread = relationship("Thread", back_populates="candidates")


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUIDType(), ForeignKey("threads.id", ondelete="CASCADE"), nullable=False)
    index_in_thread = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    text = Column(Text, nullable=False)

    options = Column(JSONBType(), nullable=True)
    time_focus = Column(ArrayType(String), nullable=True, default=list)
    topic_focus = Column(ArrayType(String), nullable=True, default=list)

    requires_children = Column(Boolean, default=False)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    thread = relationship("Thread", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUIDType(), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUIDType(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    choice_id = Column(String, nullable=True)
    free_text = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    linked_entry_id = Column(UUIDType(), ForeignKey("life_entries.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    question = relationship("Question", back_populates="answers")
    user = relationship("User", back_populates="answers")
    linked_entry = relationship("LifeEntry", foreign_keys=[linked_entry_id])
