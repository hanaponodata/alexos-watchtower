"""
logging/receipts.py
Digital signature and cryptographic receipt management for Watchtower logs/events.
Generates, verifies, and stores cryptographic proofs for tamper-evident logging.
"""

import hashlib
import hmac
from typing import Optional, Dict, Any

class ReceiptManager:
    def __init__(self, secret_key: Optional[bytes] = None):
        self.secret_key = secret_key or b"watchtower-default-secret"

    def generate_receipt(self, payload: Dict[str, Any]) -> str:
        """
        Generates a HMAC-SHA256 signature for a log/event payload.
        """
        payload_str = str(payload)
        signature = hmac.new(self.secret_key, payload_str.encode(), hashlib.sha256).hexdigest()
        return signature

    def verify_receipt(self, payload: Dict[str, Any], signature: str) -> bool:
        """
        Verifies a signature against the given payload.
        """
        expected = self.generate_receipt(payload)
        return hmac.compare_digest(expected, signature)

    def set_secret_key(self, secret_key: bytes):
        self.secret_key = secret_key

if __name__ == "__main__":
    rm = ReceiptManager()
    payload = {"event": "test", "level": "info"}
    sig = rm.generate_receipt(payload)
    print("Generated signature:", sig)
    print("Verify:", rm.verify_receipt(payload, sig))
