"""
database/models/token.py
SQLAlchemy model for tokens in Watchtower.
Tracks token metadata, ownership, and status.
"""

from sqlalchemy import String, Integer, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import Base

class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    token_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    owner: Mapped[Optional[str]] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, default="active")
    token_metadata: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Token(uuid={self.uuid}, type={self.token_type}, owner={self.owner})>"
