"""
config/settings.py
Centralized configuration loader and validator for Watchtower.
Enterprise-grade, modular, and extensible for any deployment.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

class WatchtowerSettings(BaseModel):
    # Core server
    env: str = Field("production", alias="WATCHTOWER_ENV")
    debug: bool = Field(False, alias="WATCHTOWER_DEBUG")
    host: str = Field("0.0.0.0", alias="WATCHTOWER_HOST")
    port: int = Field(5000, alias="WATCHTOWER_PORT")
    
    # Database
    db_url: str = Field("sqlite:///./watchtower.db", alias="WATCHTOWER_DB_URL")
    db_pool_size: int = Field(20, alias="WATCHTOWER_DB_POOL_SIZE")
    db_timeout: int = Field(30, alias="WATCHTOWER_DB_TIMEOUT")
    db_echo: bool = Field(False, alias="WATCHTOWER_DB_ECHO")

    # Logging
    log_level: str = Field("INFO", alias="WATCHTOWER_LOG_LEVEL")
    log_dir: str = Field("logs", alias="WATCHTOWER_LOG_DIR")
    log_rotation: str = Field("10 MB", alias="WATCHTOWER_LOG_ROTATION")
    log_backup_count: int = Field(7, alias="WATCHTOWER_LOG_BACKUP_COUNT")
    audit_log: bool = Field(True, alias="WATCHTOWER_AUDIT_LOG")

    # Secrets
    secret_file: Optional[Path] = Field(None, alias="WATCHTOWER_SECRET_FILE")
    vault_addr: Optional[str] = Field(None, alias="WATCHTOWER_VAULT_ADDR")

    # API Auth
    api_keys: List[str] = Field([], alias="WATCHTOWER_API_KEYS")
    admin_key: Optional[str] = Field(None, alias="WATCHTOWER_ADMIN_KEY")

    # Federation/Cluster
    node_id: str = Field("watchtower-01", alias="WATCHTOWER_NODE_ID")
    peers: List[str] = Field([], alias="WATCHTOWER_PEERS")
    consensus_engine: str = Field("raft", alias="WATCHTOWER_CONSENSUS_ENGINE")
    enable_federation: bool = Field(True, alias="WATCHTOWER_ENABLE_FEDERATION")

    # Messaging/Bus
    message_bus: str = Field("nats", alias="WATCHTOWER_MESSAGE_BUS")
    message_bus_url: str = Field("nats://localhost:4222", alias="WATCHTOWER_MESSAGE_BUS_URL")

    # LLM/AI Agents
    llm_proxy_url: Optional[str] = Field(None, alias="WATCHTOWER_LLM_PROXY_URL")
    llm_api_key: Optional[str] = Field(None, alias="WATCHTOWER_LLM_API_KEY")
    shadow_copilot_enabled: bool = Field(True, alias="WATCHTOWER_SHADOW_COPILOT_ENABLED")

    # Blockchain/Tokenization
    enable_blockchain: bool = Field(False, alias="WATCHTOWER_ENABLE_BLOCKCHAIN")
    blockchain_network: Optional[str] = Field(None, alias="WATCHTOWER_BLOCKCHAIN_NETWORK")
    blockchain_rpc: Optional[str] = Field(None, alias="WATCHTOWER_BLOCKCHAIN_RPC")

    # Entropy/Quantum
    use_hardware_entropy: bool = Field(True, alias="WATCHTOWER_USE_HARDWARE_ENTROPY")
    entropy_device: Optional[str] = Field("/dev/hwrng", alias="WATCHTOWER_ENTROPY_DEVICE")

    # Misc/Extensibility
    enable_plugins: bool = Field(True, alias="WATCHTOWER_ENABLE_PLUGINS")
    plugin_dir: str = Field("plugins", alias="WATCHTOWER_PLUGIN_DIR")

    # Compliance
    enable_compliance: bool = Field(True, alias="WATCHTOWER_ENABLE_COMPLIANCE")
    compliance_export_dir: str = Field("compliance", alias="WATCHTOWER_COMPLIANCE_EXPORT_DIR")

    # Backup settings
    backup_dir: str = Field("/var/backups/watchtower", alias="WATCHTOWER_BACKUP_DIR")

    # Compliance/SIEM settings
    siem_endpoints: list[str] = Field(default_factory=list, alias="WATCHTOWER_SIEM_ENDPOINTS")

    # API base URL
    api_base_url: str = Field("http://localhost:5000", alias="WATCHTOWER_API_BASE_URL")

    @field_validator("api_keys", "peers", mode="before")
    @classmethod
    def split_str(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

# Create settings from environment variables
def create_settings() -> WatchtowerSettings:
    """Create settings instance from environment variables."""
    env_vars = {}
    
    # Map environment variables to field names
    env_mapping = {
        "WATCHTOWER_ENV": "env",
        "WATCHTOWER_DEBUG": "debug", 
        "WATCHTOWER_HOST": "host",
        "WATCHTOWER_PORT": "port",
        "WATCHTOWER_DB_URL": "db_url",
        "WATCHTOWER_DB_POOL_SIZE": "db_pool_size",
        "WATCHTOWER_DB_TIMEOUT": "db_timeout",
        "WATCHTOWER_DB_ECHO": "db_echo",
        "WATCHTOWER_LOG_LEVEL": "log_level",
        "WATCHTOWER_LOG_DIR": "log_dir",
        "WATCHTOWER_LOG_ROTATION": "log_rotation",
        "WATCHTOWER_LOG_BACKUP_COUNT": "log_backup_count",
        "WATCHTOWER_AUDIT_LOG": "audit_log",
        "WATCHTOWER_SECRET_FILE": "secret_file",
        "WATCHTOWER_VAULT_ADDR": "vault_addr",
        "WATCHTOWER_API_KEYS": "api_keys",
        "WATCHTOWER_ADMIN_KEY": "admin_key",
        "WATCHTOWER_NODE_ID": "node_id",
        "WATCHTOWER_PEERS": "peers",
        "WATCHTOWER_CONSENSUS_ENGINE": "consensus_engine",
        "WATCHTOWER_ENABLE_FEDERATION": "enable_federation",
        "WATCHTOWER_MESSAGE_BUS": "message_bus",
        "WATCHTOWER_MESSAGE_BUS_URL": "message_bus_url",
        "WATCHTOWER_LLM_PROXY_URL": "llm_proxy_url",
        "WATCHTOWER_LLM_API_KEY": "llm_api_key",
        "WATCHTOWER_SHADOW_COPILOT_ENABLED": "shadow_copilot_enabled",
        "WATCHTOWER_ENABLE_BLOCKCHAIN": "enable_blockchain",
        "WATCHTOWER_BLOCKCHAIN_NETWORK": "blockchain_network",
        "WATCHTOWER_BLOCKCHAIN_RPC": "blockchain_rpc",
        "WATCHTOWER_USE_HARDWARE_ENTROPY": "use_hardware_entropy",
        "WATCHTOWER_ENTROPY_DEVICE": "entropy_device",
        "WATCHTOWER_ENABLE_PLUGINS": "enable_plugins",
        "WATCHTOWER_PLUGIN_DIR": "plugin_dir",
        "WATCHTOWER_ENABLE_COMPLIANCE": "enable_compliance",
        "WATCHTOWER_COMPLIANCE_EXPORT_DIR": "compliance_export_dir",
        "WATCHTOWER_BACKUP_DIR": "backup_dir",
        "WATCHTOWER_SIEM_ENDPOINTS": "siem_endpoints",
        "WATCHTOWER_API_BASE_URL": "api_base_url",
    }
    
    for env_var, field_name in env_mapping.items():
        if env_var in os.environ:
            env_vars[field_name] = os.environ[env_var]
    
    return WatchtowerSettings(**env_vars)

# Singleton settings object for import
settings = create_settings()

def get_settings() -> WatchtowerSettings:
    return settings

def reload_settings() -> WatchtowerSettings:
    """Reload settings from environment variables."""
    global settings
    settings = create_settings()
    return settings

