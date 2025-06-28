"""
selfaudit/analyzers/agent.py
Enterprise-grade agent analyzer for Watchtower self-audit engine.
Assesses agent registry health, liveness, error and behavioral anomaly stats from real DB.
"""

from typing import Dict, Any
from database.models.agents import Agent
from sqlalchemy.orm import Session
from sqlalchemy import func

class AgentAnalyzer:
    def __init__(self, session: Session):
        self.session = session

    def analyze(self) -> Dict[str, Any]:
        try:
            total_agents = self.session.query(func.count(Agent.id)).scalar() or 0
            online_agents = self.session.query(func.count(Agent.id)).filter(Agent.status == "online").scalar() or 0
            offline_agents = self.session.query(func.count(Agent.id)).filter(Agent.status == "offline").scalar() or 0
            degraded_agents = self.session.query(func.count(Agent.id)).filter(Agent.status == "degraded").scalar() or 0
            agents_with_errors = self.session.query(func.count(Agent.id)).filter(Agent.agent_metadata["error"].astext == "true").scalar() if total_agents > 0 else 0
            suspicious_activity_detected = self.session.query(Agent).filter(Agent.agent_metadata["suspicious"].astext == "true").count() > 0 if total_agents > 0 else False

            status = "healthy"
            if degraded_agents > 0 or agents_with_errors > 0:
                status = "degraded"
            if offline_agents == total_agents and total_agents > 0:
                status = "critical"
        except Exception as e:
            return {
                "error": f"Agent analysis failed: {e}",
                "status": "critical"
            }
        return {
            "total_agents": total_agents,
            "online_agents": online_agents,
            "offline_agents": offline_agents,
            "degraded_agents": degraded_agents,
            "agents_with_errors": agents_with_errors,
            "suspicious_activity_detected": suspicious_activity_detected,
            "status": status
        }

if __name__ == "__main__":
    print("Enterprise AgentAnalyzer requires an active SQLAlchemy session.")
