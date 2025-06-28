"""
logging/event.py
Central event logger for Watchtower.
Handles ingestion, formatting, routing, and storage of system and agent events.
"""

import logging
from typing import Any, Dict, Optional
# Remove problematic import - will import when needed
# from database.models.events import Event
from sqlalchemy.orm import Session

class EventLogger:
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger("watchtower.event")

    def log_event(
        self,
        event_type: str,
        agent_uuid: Optional[str] = None,
        severity: str = "info",
        payload: Optional[Dict[str, Any]] = None,
        signature: Optional[str] = None,
        hash_prev: Optional[str] = None,
        chain_id: Optional[str] = None,
        blockchain_tx: Optional[str] = None,
    ):
        # Lazy import to avoid circular dependency
        from database.models.events import Event
        
        event = Event(
            event_type=event_type,
            agent_uuid=agent_uuid,
            severity=severity,
            payload=payload or {},
            signature=signature,
            hash_prev=hash_prev,
            chain_id=chain_id,
            blockchain_tx=blockchain_tx,
        )
        self.session.add(event)
        self.session.commit()
        self.logger.info(
            f"Event logged: type={event_type} agent={agent_uuid} severity={severity} id={event.id}"
        )
        return event

    def get_event(self, event_id: int):
        # Lazy import to avoid circular dependency
        from database.models.events import Event
        return self.session.query(Event).filter_by(id=event_id).first()

    def query_events(self, **filters):
        # Lazy import to avoid circular dependency
        from database.models.events import Event
        query = self.session.query(Event)
        for key, value in filters.items():
            if hasattr(Event, key):
                query = query.filter(getattr(Event, key) == value)
        return query.order_by(Event.timestamp.desc()).all()

    def archive_event(self, event_id: int) -> bool:
        # Lazy import to avoid circular dependency
        from database.models.events import Event
        event = self.get_event(event_id)
        if event:
            event.archived = True
            self.session.commit()
            self.logger.info(f"Event archived: id={event_id}")
            return True
        return False

if __name__ == "__main__":
    print("EventLogger module ready (requires DB session).")
