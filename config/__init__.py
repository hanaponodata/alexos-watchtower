"""
config/__init__.py
Config package initializer for Watchtower.
Provides unified import access for all configuration submodules.
"""

from .settings import settings, get_settings
from .env import get_env, running_env, env_summary
from .secrets import get_secret, secret_manager
from .plugins import plugin_config, list_enabled_plugins
from .logging import logger, setup_logging

__all__ = [
    "settings", "get_settings",
    "get_env", "running_env", "env_summary",
    "get_secret", "secret_manager",
    "plugin_config", "list_enabled_plugins",
    "logger", "setup_logging"
]
