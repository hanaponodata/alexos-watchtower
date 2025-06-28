"""
config/secrets.py
Centralized secret management and loader for Watchtower.
Handles local .env secrets, Vault/KMS/HSM integration, and secure file-based secrets.
"""

import os
from pathlib import Path
from typing import Optional, Dict

try:
    import hvac  # HashiCorp Vault API client (optional)
except ImportError:
    hvac = None

class SecretManager:
    def __init__(self, env_file: Optional[Path] = None, vault_addr: Optional[str] = None):
        self.env_file = env_file or Path(".env")
        self.vault_addr = vault_addr or os.environ.get("WATCHTOWER_VAULT_ADDR")
        self.vault_client = None
        self.secrets = {}

        # Load local .env secrets if present
        if self.env_file.exists():
            self._load_env_file(self.env_file)
        # Connect to Vault if configured
        if self.vault_addr and hvac:
            self._connect_vault(self.vault_addr)

    def _load_env_file(self, env_file: Path):
        """Load secrets from a .env file (key=value per line)."""
        with env_file.open("r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    self.secrets[k.strip()] = v.strip()

    def _connect_vault(self, addr: str):
        """Connect to HashiCorp Vault and authenticate using environment token."""
        try:
            self.vault_client = hvac.Client(url=addr)
            if not self.vault_client.is_authenticated():
                token = os.environ.get("VAULT_TOKEN")
                if token:
                    self.vault_client.token = token
            if not self.vault_client.is_authenticated():
                print("[WARN] Vault client not authenticated.")
        except Exception as e:
            print(f"[ERROR] Vault connection failed: {e}")
            self.vault_client = None

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret by key, prioritizing Vault > local .env > environment."""
        # Check Vault if connected
        if self.vault_client:
            try:
                # Example: secret at "secret/data/watchtower"
                secret_path = f"secret/data/watchtower"
                result = self.vault_client.secrets.kv.v2.read_secret_version(path="watchtower")
                if result and "data" in result["data"]["data"]:
                    return result["data"]["data"].get(key, default)
            except Exception:
                pass
        # Check loaded .env
        if key in self.secrets:
            return self.secrets[key]
        # Fall back to os.environ
        return os.environ.get(key, default)

# Singleton secret manager for global access
secret_manager = SecretManager()

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    return secret_manager.get(key, default)

if __name__ == "__main__":
    # Example usage
    print(get_secret("WATCHTOWER_DB_URL"))
