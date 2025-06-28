"""
dashboard/__init__.py
Enterprise-grade dashboard module for Watchtower.
Provides real-time monitoring, visualization, and management interface.
"""

from .api import DashboardAPI
from .websocket import DashboardWebSocket

__all__ = ["DashboardAPI", "DashboardWebSocket"] 