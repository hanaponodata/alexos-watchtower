"""
database/models/ledger.py
SQLAlchemy model for immutable ledger entries in Watchtower.
Tracks all transactions, upgrades, protocol state, and cross-node sync for full auditability.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LedgerEntry(Base):
    __tablename__ = "ledger"
    id = Column(Integer, primary_key=True, index=True)
    entry_type = Column(String, index=True)  # e.g. "transaction", "upgrade", "state_change"
    reference_id = Column(String, index=True, nullable=True)  # Link to related entity/event
    data = Column(JSON, default={})
    timestamp = Column(DateTime, default=func.now(), index=True)
    node_id = Column(String, index=True)
    signature = Column(String, nullable=True)
    hash_prev = Column(String, nullable=True, index=True)
    hash_self = Column(String, nullable=True, index=True)
    chain_id = Column(String, nullable=True, index=True)
    blockchain_tx = Column(String, nullable=True)
    archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<LedgerEntry(id={self.id}, type={self.entry_type}, node={self.node_id}, ts={self.timestamp})>"
