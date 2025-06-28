"""
selfaudit/__init__.py
Self-audit, lineage, and genetic programming package initializer for Watchtower.
Exposes core audit, analyzers, lineage, and reporting modules.
"""

from .core import SelfAuditEngine
from .analyzers import (
    LogAnalyzer, AgentAnalyzer, SystemAnalyzer,
    UpgradeAnalyzer, ConfigAnalyzer, ProtocolAnalyzer
)
from .lineage import LineageManager
from .report import AuditReportGenerator

__all__ = [
    "SelfAuditEngine",
    "LogAnalyzer",
    "AgentAnalyzer",
    "SystemAnalyzer",
    "UpgradeAnalyzer",
    "ConfigAnalyzer",
    "ProtocolAnalyzer",
    "LineageManager",
    "AuditReportGenerator"
]
