"""
auth/__init__.py
Authentication and authorization package initializer for Watchtower.
Imports core auth modules for unified access.
"""

from .keys import APIKeyManager
from .rbac import RoleManager
from .zkp import ZKPEngine
from .onchain import OnChainAuth
from .session import SessionManager

__all__ = [
    "APIKeyManager",
    "RoleManager",
    "ZKPEngine",
    "OnChainAuth",
    "SessionManager"
]
