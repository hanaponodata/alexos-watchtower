"""
secret/vault.py
Enterprise-grade vault secret manager for Watchtower.
Integrates with HashiCorp Vault and similar KMS systems for secure secret storage and retrieval.
"""

from typing import Optional, Dict, Any
import os
try:
    import hvac  # HashiCorp Vault API client
except ImportError:
    hvac = None

class VaultManager:
    def __init__(self, vault_addr: Optional[str] = None):
        self.vault_addr = vault_addr or os.environ.get("WATCHTOWER_VAULT_ADDR")
        self.client = None
        if hvac and self.vault_addr:
            self._connect()

    def _connect(self):
        try:
            self.client = hvac.Client(url=self.vault_addr)
            if not self.client.is_authenticated():
                token = os.environ.get("VAULT_TOKEN")
                if token:
                    self.client.token = token
            if not self.client.is_authenticated():
                print("[VaultManager] Warning: Vault client not authenticated.")
        except Exception as e:
            print(f"[VaultManager] Vault connection failed: {e}")
            self.client = None

    def get_secret(self, path: str, key: str) -> Optional[str]:
        if not self.client:
            return None
        try:
            result = self.client.secrets.kv.v2.read_secret_version(path=path)
            return result["data"]["data"].get(key)
        except Exception as e:
            print(f"[VaultManager] Error reading secret: {e}")
            return None

    def set_secret(self, path: str, key: str, value: str) -> bool:
        if not self.client:
            return False
        try:
            self.client.secrets.kv.v2.create_or_update_secret(path=path, secret={key: value})
            return True
        except Exception as e:
            print(f"[VaultManager] Error writing secret: {e}")
            return False

if __name__ == "__main__":
    vm = VaultManager()
    print("VaultManager ready.")
