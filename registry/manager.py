"""
registry/manager.py
Agent registry manager for Watchtower.
Handles agent registration, updates, status, and metadata.
"""

from typing import Optional, List, Dict
from database.models.agents import Agent
from sqlalchemy.orm import Session

class AgentRegistry:
    def __init__(self, session: Session):
        self.session = session

    def register_agent(self, uuid: str, name: str, agent_type: str, owner: str, metadata: Optional[Dict] = None) -> Agent:
        agent = Agent(
            uuid=uuid,
            name=name,
            agent_type=agent_type,
            owner=owner,
            metadata=metadata or {},
            status="offline"
        )
        self.session.add(agent)
        self.session.commit()
        return agent

    def update_agent(self, uuid: str, **kwargs) -> Optional[Agent]:
        agent = self.session.query(Agent).filter_by(uuid=uuid).first()
        if agent:
            for k, v in kwargs.items():
                if hasattr(agent, k):
                    setattr(agent, k, v)
            self.session.commit()
            return agent
        return None

    def set_status(self, uuid: str, status: str) -> bool:
        agent = self.session.query(Agent).filter_by(uuid=uuid).first()
        if agent:
            agent.status = status
            self.session.commit()
            return True
        return False

    def get_agent(self, uuid: str) -> Optional[Agent]:
        return self.session.query(Agent).filter_by(uuid=uuid).first()

    def list_agents(self, status: Optional[str] = None) -> List[Agent]:
        query = self.session.query(Agent)
        if status:
            query = query.filter_by(status=status)
        return query.all()

    def remove_agent(self, uuid: str) -> bool:
        agent = self.session.query(Agent).filter_by(uuid=uuid).first()
        if agent:
            self.session.delete(agent)
            self.session.commit()
            return True
        return False

if __name__ == "__main__":
    print("AgentRegistry module ready (requires DB session).")
