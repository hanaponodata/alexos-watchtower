"""
selfaudit/lineage.py
Enterprise-grade lineage manager for Watchtower.
Tracks immutable genetic lineage nodes for upgrades, forks, merges, and system history.
"""

from typing import Dict, Any, List, Optional
from database.models.lineage import LineageNode
from sqlalchemy.orm import Session
from sqlalchemy import func

class LineageManager:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> Dict[str, Any]:
        try:
            total_nodes = self.session.query(func.count(LineageNode.id)).scalar() or 0
            forks = self.session.query(func.count(LineageNode.id)).filter(LineageNode.branch_type == "fork").scalar() or 0
            merges = self.session.query(func.count(LineageNode.id)).filter(LineageNode.branch_type == "merge").scalar() or 0
            rollbacks = self.session.query(func.count(LineageNode.id)).filter(LineageNode.branch_type == "rollback").scalar() or 0
            upgrades = self.session.query(func.count(LineageNode.id)).filter(LineageNode.branch_type == "upgrade").scalar() or 0
            spinoffs = self.session.query(func.count(LineageNode.id)).filter(LineageNode.branch_type == "spinoff").scalar() or 0
            latest = (
                self.session.query(LineageNode)
                .order_by(LineageNode.timestamp.desc())
                .first()
            )
            latest_id = latest.node_id if latest else None
            status = "healthy"
            if total_nodes == 0:
                status = "empty"
        except Exception as e:
            return {
                "error": f"Lineage analysis failed: {e}",
                "status": "critical"
            }
        return {
            "total_nodes": total_nodes,
            "forks": forks,
            "merges": merges,
            "rollbacks": rollbacks,
            "upgrades": upgrades,
            "spinoffs": spinoffs,
            "latest_node_id": latest_id,
            "status": status
        }

if __name__ == "__main__":
    print("Enterprise LineageManager requires an active SQLAlchemy session.")
