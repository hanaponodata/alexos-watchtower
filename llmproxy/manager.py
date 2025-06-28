"""
llmproxy/manager.py
Enterprise-grade LLM/AI proxy manager for Watchtower.
Handles registry, load balancing, and routing for local and remote LLM agents.
"""

from typing import Dict, Any, List, Optional
from .agent import LLMProxyAgent

class LLMProxyManager:
    def __init__(self):
        self.agents: Dict[str, LLMProxyAgent] = {}

    def register_agent(self, agent_id: str, agent: LLMProxyAgent):
        self.agents[agent_id] = agent

    def unregister_agent(self, agent_id: str):
        if agent_id in self.agents:
            del self.agents[agent_id]

    def get_agent(self, agent_id: str) -> Optional[LLMProxyAgent]:
        return self.agents.get(agent_id)

    def list_agents(self) -> List[str]:
        return list(self.agents.keys())

    def route_request(self, agent_id: str, prompt: str, **kwargs) -> Any:
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        return agent.generate(prompt, **kwargs)

if __name__ == "__main__":
    print("LLMProxyManager ready to manage LLM agents.")
