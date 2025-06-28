"""
blockchain/__init__.py
On-chain protocol, signature, and NFT/token management package initializer for Watchtower.
Exposes EVM, Solana, Polkadot, proof, token, and hook modules.
"""

from .evm import EVMChain
from .solana import SolanaChain
from .polkadot import PolkadotChain
from .proof import BlockchainProofManager
from .token import TokenManager
from .hooks import BlockchainHooks

__all__ = [
    "EVMChain",
    "SolanaChain",
    "PolkadotChain",
    "BlockchainProofManager",
    "TokenManager",
    "BlockchainHooks"
]
