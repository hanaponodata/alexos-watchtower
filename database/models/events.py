"""
database/models/events.py
SQLAlchemy model for event logs in Watchtower.
Cryptographically linked with hashchain, signatures, and event metadata.
"""

from sqlalchemy import String, Integer, DateTime, Boolean, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import Base

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(String, index=True)
    agent_uuid: Mapped[Optional[str]] = mapped_column(String, ForeignKey("agents.uuid"), index=True, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), index=True)
    severity: Mapped[str] = mapped_column(String, index=True, default="info")
    payload: Mapped[dict] = mapped_column(JSON, default={})
    source: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Event source
    signature: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    hash_prev: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)  # Merkle/hashchain
    hash_self: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    chain_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    blockchain_tx: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # On-chain receipt/tx
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Event(id={self.id}, type={self.event_type}, agent={self.agent_uuid}, ts={self.timestamp})>"
