"""
secret/__init__.py
Secret, vault, HSM, and escrow management package initializer for Watchtower.
Exposes vault, HSM, escrow, rotation, and hook modules.
"""

from .vault import VaultManager
from .hsm import HSMManager
from .escrow import EscrowManager
from .rotation import SecretRotationManager
from .hooks import SecretHooks

__all__ = [
    "VaultManager",
    "HSMManager",
    "EscrowManager",
    "SecretRotationManager",
    "SecretHooks"
]
