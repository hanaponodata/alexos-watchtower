"""
gitops/__init__.py
GitOps and CI/CD package initializer for Watchtower.
Exposes commit, snapshot, and CI automation modules.
"""

from .commit import GitCommitManager
from .snapshot import SnapshotManager
from .ci import CICDPipelineManager

__all__ = [
    "GitCommitManager",
    "SnapshotManager",
    "CICDPipelineManager"
]
