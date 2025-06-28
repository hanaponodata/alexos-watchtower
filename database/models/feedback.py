"""
database/models/feedback.py
SQLAlchemy model for feedback in Watchtower.
Tracks user/system feedback, ratings, and metadata.
"""

from sqlalchemy import String, Integer, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import Base

class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    feedback_type: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(String)
    rating: Mapped[Optional[int]] = mapped_column(Integer)
    feedback_metadata: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Feedback(id={self.id}, type={self.feedback_type}, user={self.user_id})>"
