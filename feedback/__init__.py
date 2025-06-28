"""
feedback/__init__.py
Feedback system package initializer for Watchtower.
Exposes ingest, analysis, and routing modules.
"""

from .ingest import FeedbackIngestor
from .analyze import FeedbackAnalyzer
from .routing import FeedbackRouter

__all__ = [
    "FeedbackIngestor",
    "FeedbackAnalyzer",
    "FeedbackRouter"
]
