"""
websocket/__init__.py
WebSocket protocol package initializer for Watchtower.
Exposes server, dashboard, agent, audit, and protocol bridge modules.
"""

from .server import WebSocketServer
from .dashboard import DashboardSocketHandler
from .agent import AgentSocketHandler
from .audit import AuditSocketHandler
from .bridge import ProtocolBridgeHandler

__all__ = [
    "WebSocketServer",
    "DashboardSocketHandler",
    "AgentSocketHandler",
    "AuditSocketHandler",
    "ProtocolBridgeHandler"
]
