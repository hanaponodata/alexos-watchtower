"""
upgrade/__init__.py
Upgrade, roadmap, modularization, and auto-evolution package initializer for Watchtower.
Exposes core engine, genetic, spinoff, A/B test, and hook modules.
"""

from .engine import UpgradeEngine
from .genetic import GeneticProgramEngine
from .spinoff import SpinoffManager
from .abtest import ABTestManager
from .hooks import UpgradeHooks

__all__ = [
    "UpgradeEngine",
    "GeneticProgramEngine",
    "SpinoffManager",
    "ABTestManager",
    "UpgradeHooks"
]
