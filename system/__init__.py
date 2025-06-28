"""
system/__init__.py
System health, recovery, and resource management package initializer for Watchtower.
Exposes health checks, self-healing, failover, and adaptive resource modules.
"""

from .health import SystemHealthMonitor
from .recovery import SelfHealingManager
from .failover import FailoverManager
from .resource import ResourceMonitor

__all__ = [
    "SystemHealthMonitor",
    "SelfHealingManager",
    "FailoverManager",
    "ResourceMonitor"
]
