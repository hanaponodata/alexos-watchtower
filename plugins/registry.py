"""
plugins/registry.py
Enterprise-grade plugin registry for Watchtower.
Maintains a manifest of all registered plugins, their metadata, dependencies, and compliance status.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

class PluginRegistry:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.manifest: Dict[str, Dict[str, Any]] = {}
        self._scan_plugins()

    def _scan_plugins(self):
        self.manifest.clear()
        for d in self.plugin_dir.iterdir():
            if d.is_dir():
                cfg = d / "plugin.json"
                meta = {}
                if cfg.exists():
                    with open(cfg, "r") as f:
                        meta = json.load(f)
                self.manifest[d.name] = meta

    def get_plugin_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        return self.manifest.get(name)

    def list_registered_plugins(self) -> List[str]:
        return list(self.manifest.keys())

    def check_compliance(self, name: str) -> Dict[str, Any]:
        meta = self.get_plugin_metadata(name) or {}
        missing = [field for field in ["name", "author", "version"] if field not in meta]
        return {
            "plugin": name,
            "missing_fields": missing,
            "compliant": not missing
        }

    def registry_summary(self) -> List[Dict[str, Any]]:
        return [self.check_compliance(name) for name in self.manifest]

if __name__ == "__main__":
    reg = PluginRegistry()
    print("Registry summary:", reg.registry_summary())
