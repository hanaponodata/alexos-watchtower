"""
federation/peer.py
Enterprise-grade peer manager for Watchtower federated mesh.
Tracks and manages all known mesh peers, identities, and their protocol capabilities.
"""

from typing import Dict, Any, List

class PeerManager:
    def __init__(self):
        self.peers: Dict[str, Dict[str, Any]] = {}  # peer_id -> metadata

    def register_peer(self, peer_id: str, meta: Dict[str, Any]):
        self.peers[peer_id] = meta

    def unregister_peer(self, peer_id: str):
        if peer_id in self.peers:
            del self.peers[peer_id]

    def get_peer(self, peer_id: str) -> Dict[str, Any]:
        return self.peers.get(peer_id, {})

    def list_peers(self) -> List[str]:
        return list(self.peers.keys())

    def peer_summary(self) -> List[Dict[str, Any]]:
        return [{**{"peer_id": k}, **v} for k, v in self.peers.items()]

if __name__ == "__main__":
    pm = PeerManager()
    pm.register_peer("node1", {"host": "10.1.2.3", "status": "online"})
    print(pm.peer_summary())
