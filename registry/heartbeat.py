"""
registry/heartbeat.py
Agent heartbeat and liveness manager for Watchtower.
Tracks agent health, updates last seen, and triggers offline/degraded detection.
"""

from datetime import datetime, timedelta
from typing import Optional
from database.models.agents import Agent
from sqlalchemy.orm import Session

HEARTBEAT_TIMEOUT = timedelta(minutes=5)  # Agent is offline after this period

class HeartbeatManager:
    def __init__(self, session: Session):
        self.session = session

    def update_heartbeat(self, uuid: str) -> bool:
        agent = self.session.query(Agent).filter_by(uuid=uuid).first()
        if agent:
            agent.last_seen = datetime.utcnow()
            agent.status = "online"
            self.session.commit()
            return True
        return False

    def check_liveness(self, uuid: str) -> str:
        agent = self.session.query(Agent).filter_by(uuid=uuid).first()
        if agent:
            now = datetime.utcnow()
            if agent.last_seen and (now - agent.last_seen) > HEARTBEAT_TIMEOUT:
                agent.status = "offline"
                self.session.commit()
                return "offline"
            return agent.status
        return "not_found"

    def sweep_all_agents(self):
        now = datetime.utcnow()
        agents = self.session.query(Agent).all()
        for agent in agents:
            if agent.last_seen and (now - agent.last_seen) > HEARTBEAT_TIMEOUT:
                if agent.status != "offline":
                    agent.status = "offline"
        self.session.commit()

if __name__ == "__main__":
    print("HeartbeatManager module ready (requires DB session).")
