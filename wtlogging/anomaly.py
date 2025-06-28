"""
logging/anomaly.py
Anomaly detection for Watchtower logs and events.
Flags outliers, high-severity, and suspicious agent/system behaviors.
"""

import logging
from typing import List, Dict, Any, Optional
from database.models.events import Event
from sqlalchemy.orm import Session

class AnomalyDetector:
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger("watchtower.anomaly")

    def detect_outliers(self, events: List[Event], key: str = "severity", threshold: str = "critical") -> List[Event]:
        """
        Simple rule-based outlier detection for critical or high-severity events.
        """
        outliers = [e for e in events if getattr(e, key, None) == threshold]
        self.logger.info(f"Detected {len(outliers)} critical events")
        return outliers

    def flag_suspicious_activity(self, agent_uuid: str, window: int = 100) -> Optional[List[Event]]:
        """
        Detects bursts or repeated suspicious events from a single agent.
        """
        events = (
            self.session.query(Event)
            .filter_by(agent_uuid=agent_uuid)
            .order_by(Event.timestamp.desc())
            .limit(window)
            .all()
        )
        # Example: flag if more than 5 criticals in window
        criticals = [e for e in events if e.severity == "critical"]
        if len(criticals) > 5:
            self.logger.warning(f"Agent {agent_uuid} flagged for excessive critical events.")
            return criticals
        return None

    def detect_pattern(self, pattern: str, limit: int = 100) -> List[Event]:
        """
        Search for a text pattern or keyword in recent event payloads.
        """
        events = (
            self.session.query(Event)
            .order_by(Event.timestamp.desc())
            .limit(limit)
            .all()
        )
        flagged = []
        for e in events:
            payload_str = str(e.payload)
            if pattern.lower() in payload_str.lower():
                flagged.append(e)
        self.logger.info(f"Pattern '{pattern}' detected in {len(flagged)} events.")
        return flagged

if __name__ == "__main__":
    print("AnomalyDetector module ready (requires DB session).")
