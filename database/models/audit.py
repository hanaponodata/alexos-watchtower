"""
database/models/audit.py
SQLAlchemy model for audit logs in Watchtower.
Tracks system, agent, protocol, and upgrade audit events with cryptographic lineage.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, ForeignKey, func
from .base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)  # e.g., "system", "agent", "protocol", "upgrade"
    actor = Column(String, index=True)     # User/agent performing the action
    action = Column(String, index=True)
    target = Column(String, index=True, nullable=True)
    details = Column(JSON, default={})
    severity = Column(String, default="info")
    timestamp = Column(DateTime, default=func.now(), index=True)
    hash_prev = Column(String, nullable=True, index=True)
    hash_self = Column(String, nullable=True, index=True)
    chain_id = Column(String, nullable=True, index=True)
    signature = Column(String, nullable=True)
    blockchain_tx = Column(String, nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, actor={self.actor}, ts={self.timestamp})>"
