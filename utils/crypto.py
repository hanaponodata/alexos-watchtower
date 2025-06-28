"""
utils/crypto.py
Enterprise-grade cryptography utility functions for Watchtower.
Supports key generation, signing, encryption, and verification.
"""

import os
import hashlib
import hmac
import secrets
from typing import Optional

class CryptoUtils:
    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def hmac_sha256(key: bytes, data: bytes) -> str:
        return hmac.new(key, data, hashlib.sha256).hexdigest()

    @staticmethod
    def random_bytes(length: int = 32) -> bytes:
        return secrets.token_bytes(length)

    @staticmethod
    def random_hex(length: int = 32) -> str:
        return secrets.token_hex(length)

    @staticmethod
    def derive_key(passphrase: str, salt: Optional[bytes] = None) -> bytes:
        salt = salt or secrets.token_bytes(16)
        key = hashlib.pbkdf2_hmac('sha256', passphrase.encode(), salt, 100_000)
        return key

if __name__ == "__main__":
    print("Random hex:", CryptoUtils.random_hex())
    key = CryptoUtils.derive_key("hunter2")
    print("Derived key:", key.hex())
