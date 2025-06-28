"""
selfaudit/analyzers/config.py
Enterprise-grade config analyzer for Watchtower self-audit engine.
Validates configuration integrity, environment consistency, and secrets status.
Checks for missing, deprecated, or conflicting config options and logs findings.
"""

from typing import Dict, Any
from config.settings import settings
from config.env import env_summary
from config.secrets import secret_manager
import os

class ConfigAnalyzer:
    def __init__(self):
        self.settings = settings
        self.env = env_summary()
        self.secret_manager = secret_manager

    def analyze(self) -> Dict[str, Any]:
        results = {
            "env": self.env,
            "config_status": "healthy",
            "missing": [],
            "deprecated": [],
            "conflicts": [],
            "secrets_unset": [],
            "warnings": []
        }
        # Required configs to check
        required_fields = [
            "DB_URL", "LOG_LEVEL", "NODE_ID", "API_KEYS"
        ]
        for field in required_fields:
            value = getattr(self.settings, field, None)
            if value in (None, "", [], {}):
                results["missing"].append(field)

        # Deprecated configs check (example)
        deprecated_envs = ["WATCHTOWER_OLD_API_KEY", "WATCHTOWER_LEGACY_MODE"]
        for env in deprecated_envs:
            if os.environ.get(env):
                results["deprecated"].append(env)

        # Conflicting configs (example)
        if getattr(self.settings, "debug", False) and self.settings.env == "production":
            results["conflicts"].append("DEBUG mode enabled in production environment.")

        # Secret checks
        critical_secrets = ["WATCHTOWER_ADMIN_KEY", "WATCHTOWER_DB_URL"]
        for secret in critical_secrets:
            if not self.secret_manager.get(secret):
                results["secrets_unset"].append(secret)

        if results["missing"] or results["conflicts"] or results["deprecated"] or results["secrets_unset"]:
            results["config_status"] = "review"
            if results["missing"]:
                results["warnings"].append(f"Missing configs: {results['missing']}")
            if results["deprecated"]:
                results["warnings"].append(f"Deprecated envs: {results['deprecated']}")
            if results["conflicts"]:
                results["warnings"].append(f"Conflicts: {results['conflicts']}")
            if results["secrets_unset"]:
                results["warnings"].append(f"Unset secrets: {results['secrets_unset']}")

        return results

if __name__ == "__main__":
    analyzer = ConfigAnalyzer()
    print(analyzer.analyze())
