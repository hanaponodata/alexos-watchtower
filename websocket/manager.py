"""
websocket/manager.py
Comprehensive WebSocket manager for Watchtower with authentication, audit logging, and connection management.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set, Callable
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from database.engine import get_session
from database.models.audit import AuditLog
from auth.session import SessionManager
from config import settings, logger
import hashlib
import hmac

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_subscriptions: Dict[str, Set[str]] = {}
        self.client_metadata: Dict[str, Dict[str, Any]] = {}
        self.connection_counters: Dict[str, int] = {}
        self.logger = logging.getLogger("watchtower.websocket")
        self.session_manager = SessionManager()
        
    def _generate_client_id(self, websocket: WebSocket) -> str:
        """Generate a unique client ID based on connection details."""
        client_host = websocket.client.host if websocket.client else "unknown"
        client_port = websocket.client.port if websocket.client else 0
        timestamp = datetime.utcnow().isoformat()
        unique_id = str(uuid.uuid4())
        
        # Create a deterministic client ID
        client_string = f"{client_host}:{client_port}:{timestamp}:{unique_id}"
        return hashlib.sha256(client_string.encode()).hexdigest()[:16]
    
    def _validate_auth_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate authentication token and return user info."""
        try:
            # For now, implement basic token validation
            # In production, this should use proper JWT or session validation
            if not token:
                return None
                
            # Simple token format: "user_id:timestamp:signature"
            parts = token.split(":")
            if len(parts) != 3:
                return None
                
            user_id, timestamp, signature = parts
            
            # Check if token is expired (24 hours)
            token_time = datetime.fromisoformat(timestamp)
            if datetime.utcnow() - token_time > timedelta(hours=24):
                return None
                
            # Validate signature (in production, use proper crypto)
            expected_signature = hmac.new(
                settings.admin_key.encode() if settings.admin_key else b"default",
                f"{user_id}:{timestamp}".encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature):
                return {"user_id": user_id, "authenticated": True}
            
            return None
        except Exception as e:
            self.logger.error(f"Token validation error: {e}")
            return None
    
    async def _log_audit_event(self, client_id: str, action: str, details: Dict[str, Any], severity: str = "info"):
        """Log audit event to database."""
        try:
            db = next(get_session())
            audit_log = AuditLog(
                category="websocket",
                actor=client_id,
                action=action,
                target="websocket_connection",
                details=details,
                severity=severity,
                timestamp=datetime.utcnow()
            )
            db.add(audit_log)
            db.commit()
            db.close()
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
    
    async def connect(self, websocket: WebSocket, auth_token: Optional[str] = None) -> Optional[str]:
        """Accept WebSocket connection with authentication and audit logging."""
        await websocket.accept()
        
        client_id = self._generate_client_id(websocket)
        client_host = websocket.client.host if websocket.client else "unknown"
        
        # Validate authentication if token provided
        user_info = None
        if auth_token:
            user_info = self._validate_auth_token(auth_token)
            if not user_info:
                await websocket.close(code=4001, reason="Invalid authentication token")
                return None
        
        # Store connection
        self.active_connections[client_id] = websocket
        self.client_subscriptions[client_id] = set()
        self.client_metadata[client_id] = {
            "host": client_host,
            "connected_at": datetime.utcnow(),
            "authenticated": user_info is not None,
            "user_id": user_info.get("user_id") if user_info else None,
            "last_activity": datetime.utcnow()
        }
        
        # Log connection
        self.logger.info(f"WebSocket connected: {client_id} from {client_host}")
        await self._log_audit_event(
            client_id, 
            "websocket_connect", 
            {"host": client_host, "authenticated": user_info is not None},
            "info"
        )
        
        return client_id
    
    def disconnect(self, client_id: str, reason: str = "normal"):
        """Disconnect WebSocket client and cleanup."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
        if client_id in self.client_subscriptions:
            del self.client_subscriptions[client_id]
            
        if client_id in self.client_metadata:
            metadata = self.client_metadata[client_id]
            del self.client_metadata[client_id]
            
            # Log disconnection
            self.logger.info(f"WebSocket disconnected: {client_id} - {reason}")
            asyncio.create_task(self._log_audit_event(
                client_id,
                "websocket_disconnect",
                {"reason": reason, "duration": (datetime.utcnow() - metadata["connected_at"]).total_seconds()},
                "info"
            ))
    
    async def send_message(self, client_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific client."""
        if client_id not in self.active_connections:
            return False
            
        try:
            websocket = self.active_connections[client_id]
            await websocket.send_text(json.dumps(message))
            
            # Update last activity
            if client_id in self.client_metadata:
                self.client_metadata[client_id]["last_activity"] = datetime.utcnow()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message to {client_id}: {e}")
            self.disconnect(client_id, "send_error")
            return False
    
    async def broadcast(self, message: Dict[str, Any], channels: Optional[Set[str]] = None) -> int:
        """Broadcast message to all subscribed clients."""
        sent_count = 0
        disconnected_clients = []
        
        for client_id, websocket in list(self.active_connections.items()):
            try:
                # Check if client is subscribed to any of the channels
                if channels:
                    client_channels = self.client_subscriptions.get(client_id, set())
                    if not channels.intersection(client_channels):
                        continue
                
                await websocket.send_text(json.dumps(message))
                sent_count += 1
                
                # Update last activity
                if client_id in self.client_metadata:
                    self.client_metadata[client_id]["last_activity"] = datetime.utcnow()
                    
            except Exception as e:
                self.logger.error(f"Failed to broadcast to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Cleanup disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id, "broadcast_error")
        
        return sent_count
    
    async def handle_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming WebSocket message with validation and audit logging."""
        try:
            # Update last activity
            if client_id in self.client_metadata:
                self.client_metadata[client_id]["last_activity"] = datetime.utcnow()
            
            action = message.get('action')
            if not action:
                return {"type": "error", "message": "Missing action"}
            
            # Log message for audit
            await self._log_audit_event(
                client_id,
                f"websocket_{action}",
                {"message": message},
                "info"
            )
            
            if action == 'subscribe':
                return await self._handle_subscribe(client_id, message)
            elif action == 'unsubscribe':
                return await self._handle_unsubscribe(client_id, message)
            elif action == 'ping':
                return {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
            elif action == 'get_status':
                return await self._handle_get_status(client_id, message)
            else:
                return {"type": "error", "message": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Error handling message from {client_id}: {e}")
            await self._log_audit_event(
                client_id,
                "websocket_error",
                {"error": str(e), "message": message},
                "error"
            )
            return {"type": "error", "message": "Internal server error"}
    
    async def _handle_subscribe(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription to channels."""
        channels = message.get('channels', [])
        if not isinstance(channels, list):
            return {"type": "error", "message": "Channels must be a list"}
        
        # Validate channels
        valid_channels = {'metrics', 'events', 'agents', 'alerts', 'system'}
        invalid_channels = set(channels) - valid_channels
        if invalid_channels:
            return {"type": "error", "message": f"Invalid channels: {invalid_channels}"}
        
        # Add subscriptions
        if client_id not in self.client_subscriptions:
            self.client_subscriptions[client_id] = set()
        
        self.client_subscriptions[client_id].update(channels)
        
        await self._log_audit_event(
            client_id,
            "websocket_subscribe",
            {"channels": list(channels)},
            "info"
        )
        
        return {
            "type": "subscription_confirmed",
            "channels": list(channels),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_unsubscribe(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unsubscription from channels."""
        channels = message.get('channels', [])
        if not isinstance(channels, list):
            return {"type": "error", "message": "Channels must be a list"}
        
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].difference_update(channels)
        
        await self._log_audit_event(
            client_id,
            "websocket_unsubscribe",
            {"channels": list(channels)},
            "info"
        )
        
        return {
            "type": "unsubscription_confirmed",
            "channels": list(channels),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_get_status(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status request."""
        return {
            "type": "status",
            "client_id": client_id,
            "connected_at": self.client_metadata.get(client_id, {}).get("connected_at"),
            "subscriptions": list(self.client_subscriptions.get(client_id, set())),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics."""
        now = datetime.utcnow()
        active_connections = len(self.active_connections)
        
        # Calculate connection durations
        durations = []
        for metadata in self.client_metadata.values():
            duration = (now - metadata["connected_at"]).total_seconds()
            durations.append(duration)
        
        return {
            "active_connections": active_connections,
            "total_subscriptions": sum(len(subs) for subs in self.client_subscriptions.values()),
            "average_connection_duration": sum(durations) / len(durations) if durations else 0,
            "authenticated_connections": sum(1 for m in self.client_metadata.values() if m.get("authenticated")),
            "timestamp": now.isoformat()
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager() 