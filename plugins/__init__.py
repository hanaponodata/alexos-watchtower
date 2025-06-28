"""
plugins/__init__.py
Plugin and extension package initializer for Watchtower.
Exposes core plugin manager, registry, sandboxing, and hooks.
"""

from .manager import PluginManager
from .registry import PluginRegistry
from .sandbox import PluginSandbox
from .hooks import PluginHooks

__all__ = [
    "PluginManager",
    "PluginRegistry",
    "PluginSandbox",
    "PluginHooks"
]
