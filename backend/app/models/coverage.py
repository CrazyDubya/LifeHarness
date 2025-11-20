from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.db_types import UUIDType


class CoverageGrid(Base):
    __tablename__ = "coverage_grid"

    user_id = Column(UUIDType(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    time_bucket = Column(String, primary_key=True)
    topic_bucket = Column(String, primary_key=True)
    score = Column(Integer, nullable=False, default=0)

    # Relationships
    user = relationship("User", back_populates="coverage_grid")
