"""
Watchtower API Routes for ALEX OS Integration
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/watchtower", tags=["watchtower"])

# Global reference to the Watchtower agent
_watchtower_agent = None

def set_watchtower_agent(agent):
    """Set the global Watchtower agent reference"""
    global _watchtower_agent
    _watchtower_agent = agent

def get_watchtower_agent():
    """Get the Watchtower agent instance"""
    if not _watchtower_agent:
        raise HTTPException(status_code=404, detail="Watchtower agent not found")
    return _watchtower_agent


@router.get("/status")
async def get_watchtower_status():
    """Get Watchtower status"""
    agent = get_watchtower_agent()
    return await agent.get_status()


@router.get("/containers")
async def get_watchtower_containers():
    """Get monitored containers"""
    agent = get_watchtower_agent()
    return await agent.get_containers()


@router.get("/updates")
async def get_update_history(
    limit: int = Query(50, ge=1, le=1000)
):
    """Get update history"""
    agent = get_watchtower_agent()
    return await agent.get_update_history(limit)


@router.post("/check-updates")
async def force_update_check():
    """Force an update check"""
    agent = get_watchtower_agent()
    await agent.force_update_check()
    return {"message": "Update check initiated"}


@router.post("/containers/{container_id}/update")
async def update_container(container_id: str):
    """Update a specific container"""
    agent = get_watchtower_agent()
    await agent.update_container(container_id)
    return {"message": f"Update initiated for container {container_id}"}


@router.post("/webhook/{agent_id}")
async def watchtower_webhook(
    agent_id: str,
    request: Request
):
    """Handle Watchtower webhook notifications"""
    try:
        payload = await request.json()
    except:
        payload = {}
    
    agent = get_watchtower_agent()
    if agent.agent_id != agent_id:
        raise HTTPException(status_code=404, detail="Watchtower agent not found")
    
    # Process webhook payload
    await agent._emit_event("watchtower_webhook", payload)
    
    return {"message": "Webhook processed"}


@router.get("/config")
async def get_watchtower_config():
    """Get Watchtower configuration"""
    agent = get_watchtower_agent()
    return agent.watchtower_config


@router.put("/config")
async def update_watchtower_config(config: Dict[str, Any]):
    """Update Watchtower configuration"""
    agent = get_watchtower_agent()
    
    # Update configuration
    agent.watchtower_config.update(config)
    
    # Restart agent to apply changes
    await agent.stop()
    await agent.start()
    
    return {"message": "Configuration updated"}


@router.get("/containers/{container_id}")
async def get_container_details(container_id: str):
    """Get detailed information about a specific container"""
    agent = get_watchtower_agent()
    containers = await agent.get_containers()
    
    for container in containers:
        if container['id'] == container_id:
            return container
    
    raise HTTPException(status_code=404, detail="Container not found")


@router.post("/containers/{container_id}/restart")
async def restart_container(container_id: str):
    """Restart a specific container"""
    agent = get_watchtower_agent()
    
    if not agent.docker_client:
        raise HTTPException(status_code=500, detail="Docker client not available")
    
    try:
        container = agent.docker_client.containers.get(container_id)
        container.restart()
        return {"message": f"Container {container_id} restarted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart container: {str(e)}")


@router.post("/containers/{container_id}/stop")
async def stop_container(container_id: str):
    """Stop a specific container"""
    agent = get_watchtower_agent()
    
    if not agent.docker_client:
        raise HTTPException(status_code=500, detail="Docker client not available")
    
    try:
        container = agent.docker_client.containers.get(container_id)
        container.stop()
        return {"message": f"Container {container_id} stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop container: {str(e)}")


@router.post("/containers/{container_id}/start")
async def start_container(container_id: str):
    """Start a specific container"""
    agent = get_watchtower_agent()
    
    if not agent.docker_client:
        raise HTTPException(status_code=500, detail="Docker client not available")
    
    try:
        container = agent.docker_client.containers.get(container_id)
        container.start()
        return {"message": f"Container {container_id} started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start container: {str(e)}")


@router.delete("/containers/{container_id}")
async def remove_container(container_id: str, force: bool = Query(False)):
    """Remove a specific container"""
    agent = get_watchtower_agent()
    
    if not agent.docker_client:
        raise HTTPException(status_code=500, detail="Docker client not available")
    
    try:
        container = agent.docker_client.containers.get(container_id)
        container.remove(force=force)
        return {"message": f"Container {container_id} removed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove container: {str(e)}")


@router.get("/images")
async def get_docker_images():
    """Get all Docker images"""
    agent = get_watchtower_agent()
    
    if not agent.docker_client:
        raise HTTPException(status_code=500, detail="Docker client not available")
    
    try:
        images = agent.docker_client.images.list()
        return [
            {
                'id': img.id,
                'tags': img.tags,
                'created': img.attrs['Created'],
                'size': img.attrs['Size']
            }
            for img in images
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get images: {str(e)}")


@router.post("/images/{image_name}/pull")
async def pull_image(image_name: str):
    """Pull a Docker image"""
    agent = get_watchtower_agent()
    
    if not agent.docker_client:
        raise HTTPException(status_code=500, detail="Docker client not available")
    
    try:
        image = agent.docker_client.images.pull(image_name)
        return {
            "message": f"Image {image_name} pulled successfully",
            "image_id": image.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pull image: {str(e)}")


@router.get("/stats")
async def get_watchtower_stats():
    """Get Watchtower statistics"""
    agent = get_watchtower_agent()
    
    containers = await agent.get_containers()
    updates = await agent.get_update_history()
    
    # Calculate statistics
    running_containers = len([c for c in containers if c['status'] == 'running'])
    stopped_containers = len([c for c in containers if c['status'] == 'exited'])
    
    recent_updates = [u for u in updates if u.get('status') == 'applied']
    
    return {
        'total_containers': len(containers),
        'running_containers': running_containers,
        'stopped_containers': stopped_containers,
        'total_updates': len(updates),
        'recent_updates': len(recent_updates),
        'last_check': agent.last_check.isoformat() if agent.last_check else None,
        'agent_status': agent.status
    }


# Add routes to main API server
def register_watchtower_routes(app):
    """Register Watchtower routes with FastAPI app"""
    app.include_router(router) 