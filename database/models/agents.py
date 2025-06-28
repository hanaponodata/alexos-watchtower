"""
database/models/agents.py
SQLAlchemy model for agent registry in Watchtower.
Tracks agent metadata, cryptographic ID, NFT/sigil, status, and scoring.
"""

from sqlalchemy import String, Integer, Boolean, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from .base import Base

class Agent(Base):
    __tablename__ = "agents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    agent_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    owner: Mapped[Optional[str]] = mapped_column(String, index=True)
    description: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="offline")  # "online", "offline", "degraded"
    score: Mapped[int] = mapped_column(Integer, default=0)
    last_seen: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), index=True)
    agent_metadata: Mapped[dict] = mapped_column(JSON, default={})
    crypto_id: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)  # NFT/sigil
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships (optional, e.g., to events, tokens, etc.)
    # events = relationship("Event", back_populates="agent")

    def __repr__(self):
        return f"<Agent(uuid={self.uuid}, name={self.name}, type={self.agent_type}, status={self.status})>"
