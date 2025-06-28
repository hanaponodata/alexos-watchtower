"""
registry/scoring.py
Agent scoring, health, and selection algorithms for Watchtower.
Supports agent trust, reliability, workload, and performance-based routing.
"""

from typing import Optional
from database.models.agents import Agent
from sqlalchemy.orm import Session

class AgentScoring:
    def __init__(self, session: Session):
        self.session = session

    def score_agent(self, uuid: str, delta: int):
        agent = self.session.query(Agent).filter_by(uuid=uuid).first()
        if agent:
            agent.score = max(0, agent.score + delta)
            self.session.commit()

    def get_score(self, uuid: str) -> Optional[int]:
        agent = self.session.query(Agent).filter_by(uuid=uuid).first()
        return agent.score if agent else None

    def top_agents(self, limit: int = 10):
        return self.session.query(Agent).order_by(Agent.score.desc()).limit(limit).all()

    def low_score_agents(self, limit: int = 10):
        return self.session.query(Agent).order_by(Agent.score.asc()).limit(limit).all()

    def agent_health_summary(self):
        agents = self.session.query(Agent).all()
        return [
            {
                "uuid": a.uuid,
                "name": a.name,
                "status": a.status,
                "score": a.score,
                "last_seen": a.last_seen
            }
            for a in agents
        ]

if __name__ == "__main__":
    print("AgentScoring module ready (requires DB session).")
