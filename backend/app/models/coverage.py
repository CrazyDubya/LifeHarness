from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class CoverageGrid(Base):
    __tablename__ = "coverage_grid"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    time_bucket = Column(String, primary_key=True)
    topic_bucket = Column(String, primary_key=True)
    score = Column(Integer, nullable=False, default=0)

    # Relationships
    user = relationship("User", back_populates="coverage_grid")
