"""
upgrade/genetic.py
Enterprise-grade genetic programming engine for Watchtower.
Evolves, mutates, and tests new protocol/feature variants for autonomous system improvement.
Tracks all genetic forks, mutations, and selection outcomes.
"""

from typing import Dict, Any, List, Optional
from database.models.upgrade import UpgradeProposal
from sqlalchemy.orm import Session
from datetime import datetime
import random

class GeneticProgramEngine:
    def __init__(self, session: Session):
        self.session = session

    def create_variant(self, base_proposal_id: str, mutation_desc: str, proposer: str, metadata: Optional[Dict] = None) -> UpgradeProposal:
        base = self.session.query(UpgradeProposal).filter_by(proposal_id=base_proposal_id).first()
        if not base:
            raise ValueError(f"Base proposal {base_proposal_id} not found")
        variant = UpgradeProposal(
            proposal_id=f"{base_proposal_id}-variant-{random.randint(1000,9999)}",
            title=f"{base.title} [VARIANT]",
            description=f"{base.description}\n\nMUTATION: {mutation_desc}",
            proposer=proposer,
            proposal_type="upgrade",
            metadata=metadata or {},
            roadmap=base.roadmap,
            status="pending",
            created_at=datetime.utcnow()
        )
        self.session.add(variant)
        self.session.commit()
        return variant

    def evaluate_variants(self, base_proposal_id: str) -> List[UpgradeProposal]:
        # Return all variants of a base proposal (useful for A/B or bandit testing)
        return self.session.query(UpgradeProposal).filter(
            UpgradeProposal.proposal_id.like(f"{base_proposal_id}-variant-%")
        ).all()

    def select_best_variant(self, base_proposal_id: str, criteria_func) -> Optional[UpgradeProposal]:
        # Select the best variant based on external criteria_func
        variants = self.evaluate_variants(base_proposal_id)
        if not variants:
            return None
        scored = [(v, criteria_func(v)) for v in variants]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0] if scored else None

if __name__ == "__main__":
    print("GeneticProgramEngine requires an active SQLAlchemy session.")
