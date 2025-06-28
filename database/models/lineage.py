"""
database/models/lineage.py
SQLAlchemy model for lineage nodes in Watchtower.
Tracks lineage metadata, parent/child relationships, and timestamps.
"""

from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import Base

class LineageNode(Base):
    __tablename__ = "lineage_nodes"
    uuid: Mapped[str] = mapped_column(String, primary_key=True, unique=True, index=True, nullable=False)
    parent_uuid: Mapped[Optional[str]] = mapped_column(String, ForeignKey("lineage_nodes.uuid"), nullable=True)
    lineage_metadata: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<LineageNode(uuid={self.uuid}, parent={self.parent_uuid})>"
