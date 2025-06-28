"""
registry/crypto_id.py
Cryptographic ID and sigil/NFT management for agents in Watchtower.
Handles assignment, validation, and on-chain verification of unique agent identities.
"""

import hashlib
from typing import Optional
from database.models.agents import Agent
from sqlalchemy.orm import Session

class CryptoIDManager:
    def __init__(self, session: Session):
        self.session = session

    def assign_crypto_id(self, uuid: str, nft_token: Optional[str] = None) -> Optional[str]:
        agent = self.session.query(Agent).filter_by(uuid=uuid).first()
        if not agent:
            return None
        # Assign a cryptographic ID (hash of uuid + optional NFT token)
        base = uuid + (nft_token or "")
        crypto_id = hashlib.sha256(base.encode()).hexdigest()
        agent.crypto_id = crypto_id
        self.session.commit()
        return crypto_id

    def verify_crypto_id(self, uuid: str, crypto_id: str) -> bool:
        agent = self.session.query(Agent).filter_by(uuid=uuid).first()
        if not agent or not agent.crypto_id:
            return False
        return agent.crypto_id == crypto_id

    def get_crypto_id(self, uuid: str) -> Optional[str]:
        agent = self.session.query(Agent).filter_by(uuid=uuid).first()
        if agent:
            return agent.crypto_id
        return None

if __name__ == "__main__":
    print("CryptoIDManager module ready (requires DB session).")
