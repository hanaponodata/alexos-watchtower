"""
feedback/ingest.py
Enterprise-grade feedback ingestion for Watchtower.
Accepts, validates, and stores user/agent/system feedback from API, UI, or protocol.
"""

from typing import Dict, Any
from database.models.feedback import Feedback
from sqlalchemy.orm import Session
from datetime import datetime

class FeedbackIngestor:
    def __init__(self, session: Session):
        self.session = session

    def ingest(self, feedback_type: str, source: str, message: str, metadata: Dict[str, Any] = None) -> Feedback:
        fb = Feedback(
            feedback_type=feedback_type,
            source=source,
            message=message,
            sentiment="neutral",
            analysis={},
            routed_to=None,
            status="new",
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        self.session.add(fb)
        self.session.commit()
        return fb

if __name__ == "__main__":
    print("FeedbackIngestor requires an active SQLAlchemy session.")
1~"""
feedback/ingest.py
Enterprise-grade feedback ingestion for Watchtower.
Accepts, validates, and stores user/agent/system feedback from API, UI, or protocol.
"""

from typing import Dict, Any
from database.models.feedback import Feedback
from sqlalchemy.orm import Session
from datetime import datetime

class FeedbackIngestor:
    def __init__(self, session: Session):
        self.session = session

    def ingest(self, feedback_type: str, source: str, message: str, metadata: Dict[str, Any] = None) -> Feedback:
        fb = Feedback(
            feedback_type=feedback_type,
            source=source,
            message=message,
            sentiment="neutral",
            analysis={},
            routed_to=None,
            status="new",
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        self.session.add(fb)
        self.session.commit()
        return fb

if __name__ == "__main__":
    print("FeedbackIngestor requires an active SQLAlchemy session.")

