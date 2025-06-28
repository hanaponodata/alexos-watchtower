"""
database/models/artifact.py
SQLAlchemy model for artifacts in Watchtower.
Supports NFT tokenization, ownership, provenance, and metadata.
"""

from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import Base

class Artifact(Base):
    __tablename__ = "artifacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    artifact_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    owner: Mapped[Optional[str]] = mapped_column(String, index=True)
    description: Mapped[Optional[str]] = mapped_column(String)
    artifact_metadata: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Artifact(uuid={self.uuid}, name={self.name}, type={self.artifact_type})>"
