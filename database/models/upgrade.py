"""
database/models/upgrade.py
SQLAlchemy model for upgrade proposals in Watchtower.
Tracks roadmap, proposal metadata, A/B test arms, outcomes, and lineage.
"""

from sqlalchemy import String, Integer, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import Base

class UpgradeProposal(Base):
    __tablename__ = "upgrade_proposals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending")
    upgrade_metadata: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UpgradeProposal(uuid={self.uuid}, title={self.title}, status={self.status})>"
