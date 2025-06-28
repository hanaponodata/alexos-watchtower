"""
artifact/__init__.py
Artifact, knowledge pack, and marketplace package initializer for Watchtower.
Exposes manager, NFT, swap, and hook modules.
"""

from .manager import ArtifactManager
from .nft import ArtifactNFTManager
from .swap import ArtifactSwapManager
from .hooks import ArtifactHooks

__all__ = [
    "ArtifactManager",
    "ArtifactNFTManager",
    "ArtifactSwapManager",
    "ArtifactHooks"
]
