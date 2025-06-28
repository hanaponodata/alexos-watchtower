"""
auth/keys.py
API key, sigil, and token management for Watchtower.
Handles creation, validation, revocation, and hashing of all system and agent keys.
"""

import os
import hashlib
import secrets
from typing import Optional, Dict, List
from database.models.token import Token
from sqlalchemy.orm import Session
from config.settings import settings

class APIKeyManager:
    def __init__(self, session: Session):
        self.session = session

    def generate_key(self, owner: str, token_type: str = "api_key", length: int = 64) -> str:
        raw = secrets.token_urlsafe(length)
        hashed = self.hash_key(raw)
        token = Token(
            token_type=token_type,
            value=hashed,
            owner=owner
        )
        self.session.add(token)
        self.session.commit()
        return raw  # Only show plain on creation

    def hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()

    def validate_key(self, key: str, token_type: str = "api_key") -> Optional[Token]:
        hashed = self.hash_key(key)
        token = self.session.query(Token).filter_by(value=hashed, token_type=token_type, revoked=False).first()
        return token

    def revoke_key(self, key: str) -> bool:
        hashed = self.hash_key(key)
        token = self.session.query(Token).filter_by(value=hashed, revoked=False).first()
        if token:
            token.revoked = True
            self.session.commit()
            return True
        return False

    def list_keys(self, owner: Optional[str] = None) -> List[Token]:
        query = self.session.query(Token).filter_by(token_type="api_key", revoked=False)
        if owner:
            query = query.filter_by(owner=owner)
        return query.all()

if __name__ == "__main__":
    print("APIKeyManager module ready (requires DB session).")
