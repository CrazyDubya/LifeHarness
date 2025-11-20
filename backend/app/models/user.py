import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import RelationshipStatus, MainRole, IntensityLevel


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    threads = relationship("Thread", back_populates="user", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="user", cascade="all, delete-orphan")
    life_entries = relationship("LifeEntry", back_populates="user", cascade="all, delete-orphan")
    coverage_grid = relationship("CoverageGrid", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    year_of_birth = Column(Integer, nullable=True)
    country = Column(String, nullable=True)
    primary_language = Column(String, nullable=True)

    relationship_status = Column(String, nullable=True)
    has_children = Column(Boolean, nullable=True)
    children_count = Column(Integer, nullable=True)
    children_age_brackets = Column(ARRAY(String), nullable=True, default=list)

    main_role = Column(String, nullable=True)
    field_or_industry = Column(String, nullable=True)

    avoid_topics = Column(ARRAY(String), nullable=True, default=list)
    intensity = Column(String, nullable=True, default=IntensityLevel.BALANCED.value)

    life_snapshot = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")
