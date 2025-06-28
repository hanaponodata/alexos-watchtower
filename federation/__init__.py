"""
federation/__init__.py
Federated mesh, protocol, and cluster package initializer for Watchtower.
Exposes peer, discovery, sync, consensus, bridge, and hook modules.
"""

from .peer import PeerManager
from .discovery import DiscoveryEngine
from .sync import FederationSyncManager
from .consensus import ConsensusManager
from .bridge import FederationBridge
from .hooks import FederationHooks

__all__ = [
    "PeerManager",
    "DiscoveryEngine",
    "FederationSyncManager",
    "ConsensusManager",
    "FederationBridge",
    "FederationHooks"
]
