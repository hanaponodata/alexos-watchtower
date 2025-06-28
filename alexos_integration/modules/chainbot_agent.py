"""
ALEX OS ChainBot Integration Module
Provides integration between ChainBot's AI orchestration platform and ALEX OS
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
import sys
import requests
from pathlib import Path

# Add ALEX OS core imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

logger = logging.getLogger(__name__)


class ChainBotAgent:
    """
    ALEX OS ChainBot Agent
    
    Integrates ChainBot's AI orchestration platform as a native ALEX OS agent.
    ChainBot manages two types of agents:
    1. ALEX OS Framework Agents (internal agents via AgentSpawner)
    2. AI Agents (external AI services via AIAgentManager)
    
    This agent provides the bridge between ChainBot and ALEX OS dashboard.
    """
    
    def __init__(self, agent_id: str, name: str, event_bus=None, 
                 ledger=None, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.name = name
        self.event_bus = event_bus
        self.ledger = ledger
        self.config = config or {}
        
        self.chainbot_config = config.get('chainbot', {}) if config else {}
        self.chainbot_api_url = self.chainbot_config.get('api_url', 'http://localhost:3000')
        self.chainbot_api_key = self.chainbot_config.get('api_key')
        
        # ChainBot-specific state
        self.alex_framework_agents = {}  # Internal ALEX OS agents
        self.ai_agents = {}              # External AI agents (ChatGPT, Custom GPTs, etc.)
        self.workflows = {}
        self.active_sessions = {}
        self.status = "initializing"
        self.last_sync = None
        
        # Health monitoring
        self.health_check_interval = 30  # seconds
        self.health_monitor = None
        
    async def start(self):
        """Start the ChainBot agent"""
        try:
            # Initialize ChainBot integration
            await self._init_chainbot()
            
            # Start health monitoring
            await self._start_health_monitoring()
            
            # Sync initial agent data
            await self._sync_agents()
            
            self.status = "running"
            await self._emit_event("chainbot_started", {
                "agent_id": self.agent_id,
                "status": self.status,
                "alex_framework_agents_count": len(self.alex_framework_agents),
                "ai_agents_count": len(self.ai_agents),
                "workflows_count": len(self.workflows)
            })
            
            logger.info(f"ChainBot agent {self.name} started successfully")
            
        except Exception as e:
            self.status = "error"
            logger.error(f"Failed to start ChainBot agent: {e}")
            await self._emit_event("chainbot_error", {"error": str(e)})
            raise
    
    async def stop(self):
        """Stop the ChainBot agent"""
        try:
            self.status = "stopped"
            
            # Stop health monitoring
            if self.health_monitor:
                self.health_monitor.cancel()
            
            await self._emit_event("chainbot_stopped", {
                "agent_id": self.agent_id,
                "status": self.status
            })
            
            logger.info(f"ChainBot agent {self.name} stopped")
            
        except Exception as e:
            logger.error(f"Error stopping ChainBot agent: {e}")
    
    async def _init_chainbot(self):
        """Initialize ChainBot integration"""
        try:
            # Test ChainBot API connectivity
            response = await self._make_chainbot_request("GET", "/api/health")
            if response and response.get("status") == "healthy":
                logger.info("ChainBot API connection established")
            else:
                logger.warning("ChainBot API may not be fully available")
            
            logger.info("ChainBot integration initialized")
            
        except Exception as e:
            logger.error(f"ChainBot initialization failed: {e}")
            raise Exception(f"ChainBot integration failed: {e}")
    
    async def _start_health_monitoring(self):
        """Start monitoring ChainBot health"""
        self.health_monitor = asyncio.create_task(self._monitor_health())
        logger.info("Started ChainBot health monitoring")
    
    async def _monitor_health(self):
        """Monitor ChainBot health and sync agent data"""
        while self.status == "running":
            try:
                # Check ChainBot health
                health = await self._check_chainbot_health()
                
                # Sync agent data periodically
                await self._sync_agents()
                
                # Emit health event
                await self._emit_event("chainbot_health_check", {
                    "agent_id": self.agent_id,
                    "health": health,
                    "alex_framework_agents_count": len(self.alex_framework_agents),
                    "ai_agents_count": len(self.ai_agents),
                    "workflows_count": len(self.workflows)
                })
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _sync_agents(self):
        """Sync agent data from ChainBot"""
        try:
            # Get ALEX OS framework agents
            alex_agents = await self._get_alex_framework_agents()
            self.alex_framework_agents = {agent["id"]: agent for agent in alex_agents}
            
            # Get AI agents
            ai_agents = await self._get_ai_agents()
            self.ai_agents = {agent["id"]: agent for agent in ai_agents}
            
            # Get workflows
            workflows = await self._get_workflows()
            self.workflows = {workflow["id"]: workflow for workflow in workflows}
            
            self.last_sync = datetime.now()
            
        except Exception as e:
            logger.error(f"Error syncing agents: {e}")
    
    async def _check_chainbot_health(self) -> Dict[str, Any]:
        """Check ChainBot health status"""
        try:
            response = await self._make_chainbot_request("GET", "/api/health")
            return response or {"status": "unknown"}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _get_alex_framework_agents(self) -> List[Dict[str, Any]]:
        """Get ChainBot's ALEX OS framework agents"""
        try:
            response = await self._make_chainbot_request("GET", "/api/chainbot/alex-agents")
            if isinstance(response, list):
                return response
            return []
        except Exception as e:
            logger.error(f"Failed to get ALEX framework agents: {e}")
            return []
    
    async def _get_ai_agents(self) -> List[Dict[str, Any]]:
        """Get ChainBot's AI agents (ChatGPT, Custom GPTs, etc.)"""
        try:
            response = await self._make_chainbot_request("GET", "/api/chainbot/ai-agents")
            if isinstance(response, list):
                return response
            return []
        except Exception as e:
            logger.error(f"Failed to get AI agents: {e}")
            return []
    
    async def _get_workflows(self) -> List[Dict[str, Any]]:
        """Get ChainBot workflows"""
        try:
            response = await self._make_chainbot_request("GET", "/api/chainbot/workflows")
            if isinstance(response, list):
                return response
            return []
        except Exception as e:
            logger.error(f"Failed to get workflows: {e}")
            return []
    
    async def _make_chainbot_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make request to ChainBot API"""
        try:
            url = f"{self.chainbot_api_url}{endpoint}"
            headers = {}
            
            if self.chainbot_api_key:
                headers["Authorization"] = f"Bearer {self.chainbot_api_key}"
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"ChainBot API request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"ChainBot API request error: {e}")
            return None
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event to ALEX OS event bus"""
        if self.event_bus:
            try:
                await self.event_bus.emit(f"chainbot.{event_type}", data)
            except Exception as e:
                logger.error(f"Failed to emit event {event_type}: {e}")
        else:
            logger.info(f"Event {event_type}: {data}")
    
    # Public API methods for Watchtower integration
    
    async def get_status(self) -> Dict[str, Any]:
        """Get ChainBot agent status"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.status,
            'alex_framework_agents_count': len(self.alex_framework_agents),
            'ai_agents_count': len(self.ai_agents),
            'workflows_count': len(self.workflows),
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'chainbot_config': self.chainbot_config
        }
    
    async def get_alex_framework_agents(self) -> List[Dict[str, Any]]:
        """Get ChainBot's ALEX OS framework agents"""
        return list(self.alex_framework_agents.values())
    
    async def get_ai_agents(self) -> List[Dict[str, Any]]:
        """Get ChainBot's AI agents"""
        return list(self.ai_agents.values())
    
    async def get_workflows(self) -> List[Dict[str, Any]]:
        """Get ChainBot workflows"""
        return list(self.workflows.values())
    
    async def execute_workflow(self, workflow_id: str, inputs: Optional[Dict[str, Any]] = None):
        """Execute a ChainBot workflow"""
        try:
            data = {"inputs": inputs or {}}
            response = await self._make_chainbot_request("POST", f"/api/chainbot/workflows/{workflow_id}/execute", data)
            
            await self._emit_event("workflow_executed", {
                "workflow_id": workflow_id,
                "inputs": inputs,
                "response": response
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            await self._emit_event("workflow_execution_failed", {
                "workflow_id": workflow_id,
                "error": str(e)
            })
            raise


def create_chainbot_agent(agent_id: str, name: str, event_bus=None, 
                         ledger=None, config: Optional[Dict[str, Any]] = None) -> ChainBotAgent:
    """Create a ChainBot agent instance"""
    return ChainBotAgent(agent_id, name, event_bus, ledger, config) 