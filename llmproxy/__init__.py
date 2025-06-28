"""
llmproxy/__init__.py
LLM/AI agent orchestration and shadow copilot package initializer for Watchtower.
Exposes manager, agent, scoring, hooks, and shadow copilot modules.
"""

from .manager import LLMProxyManager
from .agent import LLMProxyAgent
from .scoring import LLMProxyScoring
from .hooks import LLMProxyHooks
from .shadow import ShadowCopilot

__all__ = [
    "LLMProxyManager",
    "LLMProxyAgent",
    "LLMProxyScoring",
    "LLMProxyHooks",
    "ShadowCopilot"
]
