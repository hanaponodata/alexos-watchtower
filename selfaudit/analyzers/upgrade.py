"""
selfaudit/analyzers/upgrade.py
Enterprise-grade upgrade proposal analyzer for Watchtower self-audit engine.
Analyzes actual upgrade proposals, modularization arms, status, and outcomes in the database.
"""

from typing import Dict, Any
from database.models.upgrade import UpgradeProposal
from sqlalchemy.orm import Session
from sqlalchemy import func

class UpgradeAnalyzer:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> Dict[str, Any]:
        try:
            total_proposals = self.session.query(func.count(UpgradeProposal.id)).scalar() or 0
            pending = self.session.query(func.count(UpgradeProposal.id)).filter(UpgradeProposal.status == "pending").scalar() or 0
            approved = self.session.query(func.count(UpgradeProposal.id)).filter(UpgradeProposal.status == "approved").scalar() or 0
            implemented = self.session.query(func.count(UpgradeProposal.id)).filter(UpgradeProposal.status == "implemented").scalar() or 0
            rejected = self.session.query(func.count(UpgradeProposal.id)).filter(UpgradeProposal.status == "rejected").scalar() or 0
            spinoffs = self.session.query(func.count(UpgradeProposal.id)).filter(UpgradeProposal.proposal_type == "spinoff").scalar() or 0

            latest = (
                self.session.query(UpgradeProposal)
                .order_by(UpgradeProposal.created_at.desc())
                .first()
            )
            latest_title = latest.title if latest else None
            status = "healthy" if implemented > 0 or approved > 0 else "idle"
            if pending > approved + implemented:
                status = "action_needed"
        except Exception as e:
            return {
                "error": f"Upgrade analysis failed: {e}",
                "status": "critical"
            }
        return {
            "total_proposals": total_proposals,
            "pending": pending,
            "approved": approved,
            "implemented": implemented,
            "rejected": rejected,
            "spinoffs": spinoffs,
            "latest_title": latest_title,
            "status": status
        }

if __name__ == "__main__":
    print("Enterprise UpgradeAnalyzer requires an active SQLAlchemy session.")
