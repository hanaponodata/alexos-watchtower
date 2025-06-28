"""
selfaudit/analyzers/log.py
Enterprise-grade log analyzer for Watchtower self-audit engine.
Queries real event log data for error, critical, and anomaly metrics.
Handles empty DB, and works with any compliant SQLAlchemy session.
"""

from typing import Dict, Any
from database.models.events import Event
from sqlalchemy.orm import Session
from sqlalchemy import func

class LogAnalyzer:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> Dict[str, Any]:
        try:
            total_logs = self.session.query(func.count(Event.id)).scalar() or 0
            error_count = self.session.query(func.count(Event.id)).filter(Event.severity == "error").scalar() or 0
            critical_count = self.session.query(func.count(Event.id)).filter(Event.severity == "critical").scalar() or 0
            anomalies_found = self.session.query(func.count(Event.id)).filter(Event.payload.contains("anomaly")).scalar() or 0
            last_error_event = (
                self.session.query(Event)
                .filter(Event.severity.in_(["error", "critical"]))
                .order_by(Event.timestamp.desc())
                .first()
            )
            last_error = last_error_event.timestamp.isoformat() if last_error_event else None
            status = "healthy"
            if critical_count > 0:
                status = "critical"
            elif error_count > 0:
                status = "degraded"
        except Exception as e:
            return {
                "error": f"Log analysis failed: {e}",
                "status": "critical"
            }
        return {
            "total_logs": total_logs,
            "error_count": error_count,
            "critical_count": critical_count,
            "anomalies_found": anomalies_found,
            "last_error": last_error,
            "status": status
        }

if __name__ == "__main__":
    print("Enterprise LogAnalyzer requires an active SQLAlchemy session.")
