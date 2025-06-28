"""
utils/hashing.py
Enterprise-grade hashing utility functions for Watchtower.
Supports SHA, BLAKE, and multihash for cross-protocol compatibility.
"""

import hashlib
from typing import Optional

class HashingUtils:
    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha512(data: bytes) -> str:
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def blake2b(data: bytes, digest_size: int = 32) -> str:
        return hashlib.blake2b(data, digest_size=digest_size).hexdigest()

    @staticmethod
    def multihash(data: bytes, algorithm: str = "sha2-256") -> str:
        if algorithm == "sha2-256":
            return "1220" + HashingUtils.sha256(data)
        elif algorithm == "sha2-512":
            return "1340" + HashingUtils.sha512(data)
        elif algorithm == "blake2b":
            return "b220" + HashingUtils.blake2b(data)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

if __name__ == "__main__":
    sample = b"watchtower"
    print("SHA256:", HashingUtils.sha256(sample))
    print("Blake2b:", HashingUtils.blake2b(sample))
    print("Multihash (sha2-256):", HashingUtils.multihash(sample, "sha2-256"))
