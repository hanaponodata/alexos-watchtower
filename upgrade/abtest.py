"""
upgrade/abtest.py
Enterprise-grade A/B test manager for Watchtower upgrades and protocol trials.
Runs, tracks, and evaluates multi-arm bandit experiments for modular variants.
"""

from typing import List, Dict, Any, Callable, Optional
from database.models.upgrade import UpgradeProposal
from sqlalchemy.orm import Session

class ABTestManager:
    def __init__(self, session: Session):
        self.session = session

    def register_abtest(self, proposal_id: str, arms: List[str], metadata: Optional[Dict] = None) -> UpgradeProposal:
        # Store arms for this upgrade proposal
        proposal = self.session.query(UpgradeProposal).filter_by(proposal_id=proposal_id).first()
        if not proposal:
            raise ValueError(f"Upgrade proposal {proposal_id} not found")
        proposal.abtest_arms = arms
        if metadata:
            proposal.metadata.update(metadata)
        self.session.commit()
        return proposal

    def record_outcome(self, proposal_id: str, best_arm: str) -> UpgradeProposal:
        proposal = self.session.query(UpgradeProposal).filter_by(proposal_id=proposal_id).first()
        if not proposal:
            raise ValueError(f"Upgrade proposal {proposal_id} not found")
        proposal.outcome = best_arm
        self.session.commit()
        return proposal

    def evaluate_arms(self, proposal_id: str, scorer: Callable[[str], float]) -> Optional[str]:
        proposal = self.session.query(UpgradeProposal).filter_by(proposal_id=proposal_id).first()
        if not proposal or not proposal.abtest_arms:
            return None
        scores = {arm: scorer(arm) for arm in proposal.abtest_arms}
        best = max(scores, key=scores.get)
        self.record_outcome(proposal_id, best)
        return best

if __name__ == "__main__":
    print("ABTestManager requires an active SQLAlchemy session.")
