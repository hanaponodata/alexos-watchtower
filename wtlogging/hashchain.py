"""
logging/hashchain.py
Merkle hash chain manager for Watchtower event and audit logs.
Ensures cryptographic integrity, tamper-proof lineage, and chain validation.
"""

import hashlib
from typing import Optional, List, Dict

class HashChainLogger:
    def __init__(self, session):
        self.session = session

    @staticmethod
    def compute_hash(payload: Dict, prev_hash: Optional[str] = None) -> str:
        """
        Computes SHA-256 hash of the event payload and previous hash (if any).
        """
        payload_str = str(payload)
        hasher = hashlib.sha256()
        if prev_hash:
            hasher.update(prev_hash.encode())
        hasher.update(payload_str.encode())
        return hasher.hexdigest()

    def append_event(self, event, prev_hash: Optional[str] = None) -> str:
        """
        Appends an event to the hash chain, updates the event with hash_prev and hash_self.
        """
        hash_self = self.compute_hash(event.payload, prev_hash)
        event.hash_prev = prev_hash
        event.hash_self = hash_self
        self.session.commit()
        return hash_self

    def verify_chain(self, events: List) -> bool:
        """
        Verifies the Merkle/hash chain across a sequence of events.
        Returns True if all links are valid.
        """
        prev_hash = None
        for event in events:
            expected = self.compute_hash(event.payload, prev_hash)
            if event.hash_self != expected or event.hash_prev != prev_hash:
                return False
            prev_hash = event.hash_self
        return True

    def get_chain(self, limit: int = 100) -> List:
        """
        Returns the most recent N events in chain order for verification.
        """
        # Lazy import to avoid circular dependency
        from database.models.events import Event
        
        return (
            self.session.query(Event)
            .order_by(Event.id.desc())
            .limit(limit)
            .all()[::-1]
        )  # reverse to get chronological order

if __name__ == "__main__":
    print("HashChainLogger module ready (requires DB session).")
