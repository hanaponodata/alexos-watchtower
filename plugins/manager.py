"""
plugins/manager.py
Enterprise-grade plugin manager for Watchtower.
Handles discovery, loading, enabling, disabling, and dynamic lifecycle management of all plugins/extensions.
"""

import os
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any

class PluginManager:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, Any] = {}
        self.enabled: Dict[str, bool] = {}
        self._discover_plugins()

    def _discover_plugins(self):
        if not self.plugin_dir.exists():
            self.plugin_dir.mkdir(parents=True)
        for d in self.plugin_dir.iterdir():
            if d.is_dir() and (d / "main.py").exists():
                self.plugins[d.name] = None
                self.enabled[d.name] = self._is_plugin_enabled(d.name)

    def _is_plugin_enabled(self, name: str) -> bool:
        cfg = self.plugin_dir / name / "plugin.json"
        if cfg.exists():
            import json
            with open(cfg, "r") as f:
                meta = json.load(f)
            return meta.get("enabled", True)
        return True

    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())

    def load_plugin(self, name: str):
        if not self.enabled.get(name, True):
            return None
        main_py = self.plugin_dir / name / "main.py"
        if main_py.exists():
            spec = importlib.util.spec_from_file_location(f"plugin_{name}", main_py)
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
            self.plugins[name] = plugin
            return plugin
        return None

    def enable_plugin(self, name: str):
        self.enabled[name] = True

    def disable_plugin(self, name: str):
        self.enabled[name] = False

    def reload_plugins(self):
        for name in self.plugins:
            self.load_plugin(name)

if __name__ == "__main__":
    mgr = PluginManager()
    print("Plugins discovered:", mgr.list_plugins())
