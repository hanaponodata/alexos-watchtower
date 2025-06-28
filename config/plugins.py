"""
config/plugins.py
Plugin and extension configuration registry for Watchtower.
Handles dynamic discovery, enable/disable, and configuration of all core and third-party plugins.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import importlib.util
import json

class PluginConfig:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins = {}
        self.configs = {}
        self._discover_plugins()

    def _discover_plugins(self):
        """Discover available plugins in the plugin directory."""
        if not self.plugin_dir.exists():
            self.plugin_dir.mkdir(parents=True)
        for f in self.plugin_dir.glob("*/plugin.json"):
            try:
                with open(f, "r") as cfg:
                    meta = json.load(cfg)
                    plugin_name = meta.get("name") or f.parent.name
                    self.plugins[plugin_name] = f.parent
                    self.configs[plugin_name] = meta
            except Exception as e:
                print(f"[WARN] Failed to load plugin config {f}: {e}")

    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())

    def get_plugin_config(self, name: str) -> Optional[Dict[str, Any]]:
        return self.configs.get(name)

    def is_enabled(self, name: str) -> bool:
        cfg = self.get_plugin_config(name)
        if cfg:
            return cfg.get("enabled", True)
        return False

    def enable_plugin(self, name: str):
        if name in self.configs:
            self.configs[name]["enabled"] = True
            self._save_plugin_config(name)

    def disable_plugin(self, name: str):
        if name in self.configs:
            self.configs[name]["enabled"] = False
            self._save_plugin_config(name)

    def _save_plugin_config(self, name: str):
        """Persist plugin config changes."""
        cfg_path = self.plugins[name] / "plugin.json"
        try:
            with open(cfg_path, "w") as f:
                json.dump(self.configs[name], f, indent=2)
        except Exception as e:
            print(f"[ERROR] Could not save config for plugin {name}: {e}")

    def load_plugin(self, name: str):
        """Dynamically import a plugin if enabled."""
        if not self.is_enabled(name):
            print(f"[INFO] Plugin {name} is disabled.")
            return None
        main_py = self.plugins[name] / "main.py"
        if main_py.exists():
            spec = importlib.util.spec_from_file_location(f"plugin_{name}", main_py)
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
            return plugin
        else:
            print(f"[WARN] No main.py found for plugin {name}")
            return None

# Singleton plugin config for global usage
plugin_config = PluginConfig()

def list_enabled_plugins() -> List[str]:
    return [p for p in plugin_config.list_plugins() if plugin_config.is_enabled(p)]

if __name__ == "__main__":
    print("Plugins found:", plugin_config.list_plugins())
    print("Enabled plugins:", list_enabled_plugins())
