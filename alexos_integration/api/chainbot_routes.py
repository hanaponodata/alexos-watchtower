"""
ChainBot API Routes for ALEX OS Integration
Provides REST API endpoints for ChainBot integration with Watchtower dashboard
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json

# Import ChainBot agent
from ..modules.chainbot_agent import ChainBotAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chainbot", tags=["chainbot"])

# Global ChainBot agent instance (will be set during initialization)
chainbot_agent: Optional[ChainBotAgent] = None


def get_chainbot_agent() -> ChainBotAgent:
    """Get the ChainBot agent instance"""
    if chainbot_agent is None:
        raise HTTPException(status_code=503, detail="ChainBot agent not initialized")
    return chainbot_agent


@router.get("/health")
async def chainbot_health():
    """Get ChainBot health status"""
    try:
        agent = get_chainbot_agent()
        status = await agent.get_status()
        return {
            "status": "healthy",
            "chainbot": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"ChainBot health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/status")
async def get_chainbot_status():
    """Get detailed ChainBot status"""
    try:
        agent = get_chainbot_agent()
        return await agent.get_status()
    except Exception as e:
        logger.error(f"Failed to get ChainBot status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/alex-framework")
async def get_alex_framework_agents():
    """Get ChainBot's ALEX OS framework agents"""
    try:
        agent = get_chainbot_agent()
        agents = await agent.get_alex_framework_agents()
        
        # Format for Watchtower dashboard
        formatted_agents = []
        for agent_data in agents:
            formatted_agents.append({
                "id": agent_data.get("id"),
                "name": agent_data.get("name"),
                "status": agent_data.get("status", "unknown"),
                "agent_type": "alex_os_framework_agent",
                "source": "chainbot",
                "capabilities": agent_data.get("capabilities", []),
                "created_at": agent_data.get("created_at"),
                "last_active": agent_data.get("last_active"),
                "metadata": agent_data.get("metadata", {})
            })
        
        return {
            "agents": formatted_agents,
            "count": len(formatted_agents),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get ALEX framework agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/ai")
async def get_ai_agents():
    """Get ChainBot's AI agents (ChatGPT, Custom GPTs, etc.)"""
    try:
        agent = get_chainbot_agent()
        agents = await agent.get_ai_agents()
        
        # Format for Watchtower dashboard
        formatted_agents = []
        for agent_data in agents:
            formatted_agents.append({
                "id": agent_data.get("id"),
                "name": agent_data.get("name"),
                "status": agent_data.get("status", "unknown"),
                "agent_type": agent_data.get("type", "ai_agent"),  # chatgpt, custom_gpt, gpt5, etc.
                "source": "chainbot",
                "capabilities": agent_data.get("capabilities", []),
                "provider": agent_data.get("provider"),  # openai, anthropic, etc.
                "model": agent_data.get("model"),
                "created_at": agent_data.get("created_at"),
                "last_active": agent_data.get("last_active"),
                "metadata": agent_data.get("metadata", {})
            })
        
        return {
            "agents": formatted_agents,
            "count": len(formatted_agents),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get AI agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/all")
async def get_all_chainbot_agents():
    """Get all ChainBot agents (both ALEX framework and AI agents)"""
    try:
        agent = get_chainbot_agent()
        
        # Get both types of agents
        alex_agents = await agent.get_alex_framework_agents()
        ai_agents = await agent.get_ai_agents()
        
        # Combine and format
        all_agents = []
        
        # Add ALEX framework agents
        for agent_data in alex_agents:
            all_agents.append({
                "id": agent_data.get("id"),
                "name": agent_data.get("name"),
                "status": agent_data.get("status", "unknown"),
                "agent_type": "alex_os_framework_agent",
                "source": "chainbot",
                "capabilities": agent_data.get("capabilities", []),
                "created_at": agent_data.get("created_at"),
                "last_active": agent_data.get("last_active"),
                "metadata": agent_data.get("metadata", {})
            })
        
        # Add AI agents
        for agent_data in ai_agents:
            all_agents.append({
                "id": agent_data.get("id"),
                "name": agent_data.get("name"),
                "status": agent_data.get("status", "unknown"),
                "agent_type": agent_data.get("type", "ai_agent"),
                "source": "chainbot",
                "capabilities": agent_data.get("capabilities", []),
                "provider": agent_data.get("provider"),
                "model": agent_data.get("model"),
                "created_at": agent_data.get("created_at"),
                "last_active": agent_data.get("last_active"),
                "metadata": agent_data.get("metadata", {})
            })
        
        return {
            "agents": all_agents,
            "count": len(all_agents),
            "alex_framework_count": len(alex_agents),
            "ai_agents_count": len(ai_agents),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get all ChainBot agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows")
async def get_workflows():
    """Get ChainBot workflows"""
    try:
        agent = get_chainbot_agent()
        workflows = await agent.get_workflows()
        
        # Format for Watchtower dashboard
        formatted_workflows = []
        for workflow in workflows:
            formatted_workflows.append({
                "id": workflow.get("id"),
                "name": workflow.get("name"),
                "description": workflow.get("description"),
                "status": workflow.get("status", "unknown"),
                "definition": workflow.get("definition"),
                "created_at": workflow.get("created_at"),
                "updated_at": workflow.get("updated_at"),
                "execution_count": workflow.get("execution_count", 0),
                "last_executed": workflow.get("last_executed"),
                "metadata": workflow.get("metadata", {})
            })
        
        return {
            "workflows": formatted_workflows,
            "count": len(formatted_workflows),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get specific ChainBot workflow"""
    try:
        agent = get_chainbot_agent()
        workflows = await agent.get_workflows()
        
        # Find the specific workflow
        workflow = None
        for wf in workflows:
            if wf.get("id") == workflow_id:
                workflow = wf
                break
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "id": workflow.get("id"),
            "name": workflow.get("name"),
            "description": workflow.get("description"),
            "status": workflow.get("status", "unknown"),
            "definition": workflow.get("definition"),
            "created_at": workflow.get("created_at"),
            "updated_at": workflow.get("updated_at"),
            "execution_count": workflow.get("execution_count", 0),
            "last_executed": workflow.get("last_executed"),
            "metadata": workflow.get("metadata", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, inputs: Optional[Dict[str, Any]] = None):
    """Execute a ChainBot workflow"""
    try:
        agent = get_chainbot_agent()
        result = await agent.execute_workflow(workflow_id, inputs)
        
        return {
            "workflow_id": workflow_id,
            "status": "executed",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to execute workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def get_sessions():
    """Get ChainBot sessions"""
    try:
        agent = get_chainbot_agent()
        status = await agent.get_status()
        
        # For now, return basic session info
        # This can be expanded when ChainBot provides session APIs
        return {
            "sessions": [],  # Will be populated when ChainBot provides session APIs
            "count": 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entanglements")
async def get_entanglements():
    """Get ChainBot entanglements"""
    try:
        agent = get_chainbot_agent()
        status = await agent.get_status()
        
        # For now, return basic entanglement info
        # This can be expanded when ChainBot provides entanglement APIs
        return {
            "entanglements": [],  # Will be populated when ChainBot provides entanglement APIs
            "count": 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get entanglements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def initialize_chainbot_routes(agent_instance: ChainBotAgent):
    """Initialize ChainBot routes with agent instance"""
    global chainbot_agent
    chainbot_agent = agent_instance
    logger.info("ChainBot API routes initialized") 