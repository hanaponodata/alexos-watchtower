"""
dashboard/websocket.py
Enhanced WebSocket handler for real-time dashboard updates.
Provides live data streaming for system metrics, events, and agent status.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import WebSocket, WebSocketDisconnect

from config import logger
from websocket.server import WebSocketServer

class DashboardWebSocket:
    def __init__(self, ws_server: WebSocketServer):
        self.ws_server = ws_server
        self.logger = logging.getLogger("watchtower.dashboard.ws")
        self.dashboard_clients: Dict[str, Dict[str, Any]] = {}
        self.metrics_task: Optional[asyncio.Task] = None
        
    async def handle_connection(self, client_id: str, websocket: WebSocket):
        """Handle a new dashboard WebSocket connection."""
        await self.ws_server.connect(client_id, websocket)
        self.dashboard_clients[client_id] = {
            "connected_at": datetime.utcnow(),
            "subscriptions": set(),
            "last_activity": datetime.utcnow()
        }
        
        self.logger.info(f"Dashboard client connected: {client_id}")
        
        # Start metrics broadcasting if this is the first client
        if len(self.dashboard_clients) == 1:
            await self._start_metrics_broadcast()
        
        try:
            while True:
                data = await websocket.receive_json()
                await self._handle_message(client_id, data)
        except WebSocketDisconnect:
            await self._handle_disconnect(client_id)
        except Exception as e:
            self.logger.error(f"Dashboard WS error ({client_id}): {e}")
            await self._handle_disconnect(client_id)
    
    async def _handle_message(self, client_id: str, data: Dict[str, Any]):
        """Handle incoming WebSocket messages from dashboard clients."""
        action = data.get("action")
        self.dashboard_clients[client_id]["last_activity"] = datetime.utcnow()
        
        if action == "subscribe":
            await self._handle_subscribe(client_id, data)
        elif action == "unsubscribe":
            await self._handle_unsubscribe(client_id, data)
        elif action == "ping":
            await self._send_pong(client_id)
        elif action == "get_metrics":
            await self._send_metrics(client_id)
        elif action == "get_events":
            await self._send_events(client_id, data.get("limit", 50))
        elif action == "get_agents":
            await self._send_agents(client_id, data.get("limit", 50))
        else:
            self.logger.warning(f"Unknown dashboard action: {action}")
    
    async def _handle_subscribe(self, client_id: str, data: Dict[str, Any]):
        """Handle subscription requests."""
        channels = data.get("channels", [])
        for channel in channels:
            self.dashboard_clients[client_id]["subscriptions"].add(channel)
        
        await self.ws_server.send_message(client_id, {
            "type": "subscription_confirmed",
            "channels": list(self.dashboard_clients[client_id]["subscriptions"]),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _handle_unsubscribe(self, client_id: str, data: Dict[str, Any]):
        """Handle unsubscription requests."""
        channels = data.get("channels", [])
        for channel in channels:
            self.dashboard_clients[client_id]["subscriptions"].discard(channel)
        
        await self.ws_server.send_message(client_id, {
            "type": "unsubscription_confirmed",
            "channels": list(self.dashboard_clients[client_id]["subscriptions"]),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _send_pong(self, client_id: str):
        """Send pong response."""
        await self.ws_server.send_message(client_id, {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _send_metrics(self, client_id: str):
        """Send current system metrics."""
        metrics = await self._get_system_metrics()
        await self.ws_server.send_message(client_id, {
            "type": "metrics",
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _send_events(self, client_id: str, limit: int):
        """Send recent events."""
        events = await self._get_recent_events(limit)
        await self.ws_server.send_message(client_id, {
            "type": "events",
            "data": events,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _send_agents(self, client_id: str, limit: int):
        """Send agent status."""
        agents = await self._get_agent_status(limit)
        await self.ws_server.send_message(client_id, {
            "type": "agents",
            "data": agents,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _handle_disconnect(self, client_id: str):
        """Handle client disconnection."""
        self.ws_server.disconnect(client_id)
        if client_id in self.dashboard_clients:
            del self.dashboard_clients[client_id]
        
        self.logger.info(f"Dashboard client disconnected: {client_id}")
        
        # Stop metrics broadcasting if no clients remain
        if not self.dashboard_clients and self.metrics_task:
            self.metrics_task.cancel()
            self.metrics_task = None
    
    async def _start_metrics_broadcast(self):
        """Start periodic metrics broadcasting to all dashboard clients."""
        if self.metrics_task and not self.metrics_task.done():
            return
        
        self.metrics_task = asyncio.create_task(self._metrics_broadcast_loop())
    
    async def _metrics_broadcast_loop(self):
        """Broadcast metrics to all dashboard clients every 5 seconds."""
        while self.dashboard_clients:
            try:
                # Get current metrics
                metrics = await self._get_system_metrics()
                
                # Broadcast to all dashboard clients
                message = {
                    "type": "metrics_update",
                    "data": metrics,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self.ws_server.broadcast(message)
                
                # Wait 5 seconds before next broadcast
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in metrics broadcast: {e}")
                await asyncio.sleep(5)
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            import psutil
            
            # CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network stats
            network = psutil.net_io_counters()
            
            return {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used": memory.used,
                    "memory_total": memory.total,
                    "disk_percent": disk.percent,
                    "disk_used": disk.used,
                    "disk_total": disk.total
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "watchtower": {
                    "uptime": await self._get_uptime(),
                    "active_agents": await self._get_active_agents_count(),
                    "total_events": await self._get_total_events_count(),
                    "peers_count": await self._get_peers_count(),
                    "system_health": "healthy"
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {
                "error": "Failed to get system metrics",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _get_recent_events(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent events."""
        # Mock data - replace with actual database queries
        events = []
        for i in range(limit):
            events.append({
                "id": f"event-{i}",
                "timestamp": datetime.utcnow().isoformat(),
                "type": "system",
                "severity": "info",
                "source": f"agent-{i % 5 + 1}",
                "message": f"Sample event {i}"
            })
        return events
    
    async def _get_agent_status(self, limit: int) -> List[Dict[str, Any]]:
        """Get agent status."""
        # Mock data - replace with actual database queries
        agents = []
        for i in range(limit):
            agents.append({
                "id": f"agent-{i}",
                "name": f"Agent {i}",
                "status": "active" if i % 3 != 0 else "idle",
                "last_seen": datetime.utcnow().isoformat(),
                "health_score": 0.95 - (i * 0.01)
            })
        return agents
    
    async def _get_uptime(self) -> str:
        """Get system uptime."""
        try:
            import psutil
            import time
            uptime_seconds = time.time() - psutil.boot_time()
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"
    
    async def _get_active_agents_count(self) -> int:
        """Get number of active agents."""
        return 12  # Mock data
    
    async def _get_total_events_count(self) -> int:
        """Get total number of events."""
        return 15420  # Mock data
    
    async def _get_peers_count(self) -> int:
        """Get number of connected peers."""
        return 3  # Mock data
    
    async def broadcast_event(self, event: Dict[str, Any]):
        """Broadcast a new event to all dashboard clients."""
        message = {
            "type": "new_event",
            "data": event,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.ws_server.broadcast(message)
    
    async def broadcast_alert(self, alert: Dict[str, Any]):
        """Broadcast an alert to all dashboard clients."""
        message = {
            "type": "alert",
            "data": alert,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.ws_server.broadcast(message) 