"""
ALEX OS Watchtower Integration Module
Provides seamless integration between Watchtower and ALEX OS
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
import sys
import subprocess
import docker
from pathlib import Path

# Add ALEX OS core imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

logger = logging.getLogger(__name__)


class WatchtowerAgent:
    """
    ALEX OS Watchtower Agent
    
    Integrates Watchtower functionality as a native ALEX OS agent,
    providing container monitoring, updates, and management through
    the ALEX OS web dashboard and API.
    """
    
    def __init__(self, agent_id: str, name: str, event_bus=None, 
                 ledger=None, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.name = name
        self.event_bus = event_bus
        self.ledger = ledger
        self.config = config or {}
        
        self.watchtower_config = config.get('watchtower', {}) if config else {}
        self.container_monitor = None
        self.update_scheduler = None
        self.webhook_endpoint = None
        self.running = False
        
        # Watchtower-specific state
        self.monitored_containers = {}
        self.update_history = []
        self.last_check = None
        self.status = "initializing"
        
        # Docker client
        self.docker_client = None
        
    async def start(self):
        """Start the Watchtower agent"""
        try:
            # Initialize Watchtower integration
            await self._init_watchtower()
            
            # Start monitoring containers
            await self._start_container_monitoring()
            
            # Start update scheduler
            await self._start_update_scheduler()
            
            # Register webhook endpoint
            await self._register_webhook()
            
            self.running = True
            self.status = "running"
            await self._emit_event("watchtower_started", {
                "agent_id": self.agent_id,
                "status": self.status,
                "monitored_containers": len(self.monitored_containers)
            })
            
            logger.info(f"Watchtower agent {self.name} started successfully")
            
        except Exception as e:
            self.status = "error"
            logger.error(f"Failed to start Watchtower agent: {e}")
            await self._emit_event("watchtower_error", {"error": str(e)})
            raise
    
    async def stop(self):
        """Stop the Watchtower agent"""
        try:
            self.running = False
            
            # Stop monitoring
            if self.container_monitor:
                self.container_monitor.cancel()
            
            # Stop scheduler
            if self.update_scheduler:
                self.update_scheduler.cancel()
            
            self.status = "stopped"
            await self._emit_event("watchtower_stopped", {
                "agent_id": self.agent_id,
                "status": self.status
            })
            
            logger.info(f"Watchtower agent {self.name} stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Watchtower agent: {e}")
    
    async def _init_watchtower(self):
        """Initialize Watchtower integration"""
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            
            # Check if Watchtower is available
            try:
                # Try to find Watchtower container
                watchtower_containers = self.docker_client.containers.list(
                    filters={"ancestor": "containrrr/watchtower"}
                )
                if watchtower_containers:
                    logger.info(f"Found {len(watchtower_containers)} Watchtower containers")
                else:
                    logger.info("No Watchtower containers found - will use direct Docker API")
                    
            except Exception as e:
                logger.warning(f"Could not connect to Docker: {e}")
            
            logger.info("Watchtower integration initialized")
            
        except Exception as e:
            logger.error(f"Watchtower initialization failed: {e}")
            raise Exception(f"Watchtower integration failed: {e}")
    
    async def _start_container_monitoring(self):
        """Start monitoring Docker containers"""
        try:
            if not self.docker_client:
                logger.warning("Docker client not available - skipping container monitoring")
                return
            
            # Get initial container list
            containers = self.docker_client.containers.list()
            
            for container in containers:
                await self._register_container(container)
            
            # Start monitoring loop
            self.container_monitor = asyncio.create_task(self._monitor_containers())
            
            logger.info(f"Started monitoring {len(containers)} containers")
            
        except Exception as e:
            logger.error(f"Failed to start container monitoring: {e}")
            raise
    
    async def _monitor_containers(self):
        """Monitor containers for changes"""
        while self.running:
            try:
                if not self.docker_client:
                    await asyncio.sleep(60)
                    continue
                    
                containers = self.docker_client.containers.list()
                current_container_ids = {c.id for c in containers}
                
                # Check for new containers
                for container in containers:
                    if container.id not in self.monitored_containers:
                        await self._register_container(container)
                
                # Check for removed containers
                removed_containers = set(self.monitored_containers.keys()) - current_container_ids
                for container_id in removed_containers:
                    await self._unregister_container(container_id)
                
                # Update container status
                for container in containers:
                    await self._update_container_status(container)
                
                self.last_check = datetime.now()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in container monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _register_container(self, container):
        """Register a container for monitoring"""
        try:
            container_info = {
                'id': container.id,
                'name': container.name,
                'image': container.image.tags[0] if container.image.tags else container.image.id,
                'status': container.status,
                'created': container.attrs['Created'],
                'ports': container.attrs['NetworkSettings']['Ports'],
                'labels': container.labels,
                'environment': container.attrs['Config']['Env']
            }
            
            self.monitored_containers[container.id] = container_info
            
            await self._emit_event("container_registered", {
                "container_id": container.id,
                "container_name": container.name,
                "image": container_info['image']
            })
            
            logger.info(f"Registered container: {container.name}")
            
        except Exception as e:
            logger.error(f"Failed to register container {container.id}: {e}")
    
    async def _unregister_container(self, container_id):
        """Unregister a container"""
        if container_id in self.monitored_containers:
            container_name = self.monitored_containers[container_id]['name']
            del self.monitored_containers[container_id]
            
            await self._emit_event("container_unregistered", {
                "container_id": container_id,
                "container_name": container_name
            })
            
            logger.info(f"Unregistered container: {container_name}")
    
    async def _update_container_status(self, container):
        """Update container status"""
        if container.id in self.monitored_containers:
            old_status = self.monitored_containers[container.id]['status']
            new_status = container.status
            
            if old_status != new_status:
                self.monitored_containers[container.id]['status'] = new_status
                
                await self._emit_event("container_status_changed", {
                    "container_id": container.id,
                    "container_name": container.name,
                    "old_status": old_status,
                    "new_status": new_status
                })
    
    async def _start_update_scheduler(self):
        """Start the update scheduler"""
        update_interval = self.watchtower_config.get('update_interval', 300)
        
        self.update_scheduler = asyncio.create_task(self._schedule_updates(update_interval))
        logger.info(f"Started update scheduler with {update_interval}s interval")
    
    async def _schedule_updates(self, interval):
        """Schedule container updates"""
        while self.running:
            try:
                await asyncio.sleep(interval)
                
                if self.running:
                    await self._check_for_updates()
                    
            except Exception as e:
                logger.error(f"Error in update scheduler: {e}")
                await asyncio.sleep(60)
    
    async def _check_for_updates(self):
        """Check for container updates"""
        try:
            if not self.docker_client:
                return
                
            # Check for updates by comparing image digests
            updates = []
            
            for container in self.docker_client.containers.list():
                try:
                    # Get current image
                    current_image = container.image
                    
                    # Check if there's a newer version available
                    # This is a simplified check - in practice, you'd check registries
                    image_name = current_image.tags[0] if current_image.tags else current_image.id
                    
                    # For now, we'll simulate update detection
                    # In a real implementation, you'd check Docker Hub or other registries
                    
                except Exception as e:
                    logger.error(f"Error checking container {container.name}: {e}")
                    continue
            
            if updates:
                await self._emit_event("updates_available", {
                    "count": len(updates),
                    "containers": [u['container_name'] for u in updates]
                })
            
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
    
    async def _process_update(self, update):
        """Process a container update"""
        try:
            update_record = {
                'container_id': update['container_id'],
                'container_name': update['container_name'],
                'old_image': update['old_image'],
                'new_image': update['new_image'],
                'timestamp': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            self.update_history.append(update_record)
            
            await self._emit_event("update_detected", update_record)
            
            # Auto-update if configured
            if self.watchtower_config.get('auto_update', False):
                await self._apply_update(update)
            
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    async def _apply_update(self, update):
        """Apply a container update"""
        try:
            if not self.docker_client:
                return
                
            container = self.docker_client.containers.get(update['container_id'])
            
            # Pull new image
            new_image = update['new_image']
            self.docker_client.images.pull(new_image)
            
            # Stop and remove old container
            container.stop()
            container.remove()
            
            # Create new container with same configuration
            # This is a simplified version - in practice, you'd preserve all settings
            
            update_record = {
                'container_id': update['container_id'],
                'container_name': update['container_name'],
                'old_image': update['old_image'],
                'new_image': update['new_image'],
                'timestamp': datetime.now().isoformat(),
                'status': 'applied'
            }
            
            self.update_history.append(update_record)
            
            await self._emit_event("update_applied", update_record)
            
            logger.info(f"Applied update for container: {update['container_name']}")
            
        except Exception as e:
            logger.error(f"Error applying update: {e}")
            await self._emit_event("update_failed", {
                "container_id": update['container_id'],
                "error": str(e)
            })
    
    async def _register_webhook(self):
        """Register webhook endpoint for Watchtower notifications"""
        # This will be handled by the ALEX OS API server
        self.webhook_endpoint = f"/api/watchtower/webhook/{self.agent_id}"
        
        logger.info(f"Registered webhook endpoint: {self.webhook_endpoint}")
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event to ALEX OS event bus"""
        if self.event_bus:
            try:
                await self.event_bus.emit(f"watchtower.{event_type}", data)
            except Exception as e:
                logger.error(f"Failed to emit event {event_type}: {e}")
        else:
            logger.info(f"Event {event_type}: {data}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Watchtower agent status"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.status,
            'monitored_containers': len(self.monitored_containers),
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'update_history_count': len(self.update_history),
            'watchtower_config': self.watchtower_config
        }
    
    async def get_containers(self) -> List[Dict[str, Any]]:
        """Get monitored containers"""
        return list(self.monitored_containers.values())
    
    async def get_update_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get update history"""
        return self.update_history[-limit:] if self.update_history else []
    
    async def force_update_check(self):
        """Force an update check"""
        await self._check_for_updates()
    
    async def update_container(self, container_id: str):
        """Manually update a specific container"""
        if container_id in self.monitored_containers:
            container_info = self.monitored_containers[container_id]
            
            # Create update object and apply it
            update = {
                'container_id': container_id,
                'container_name': container_info['name'],
                'old_image': container_info['image'],
                'new_image': container_info['image']  # In practice, you'd get the new version
            }
            
            await self._process_update(update)


# Factory function for creating Watchtower agents
def create_watchtower_agent(agent_id: str, name: str, event_bus=None, 
                           ledger=None, config: Optional[Dict[str, Any]] = None) -> WatchtowerAgent:
    """Create a Watchtower agent instance"""
    return WatchtowerAgent(agent_id, name, event_bus, ledger, config) 