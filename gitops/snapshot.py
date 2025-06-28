"""
gitops/snapshot.py
Enterprise-grade snapshot manager for Watchtower GitOps.
Handles versioning, tagging, and artifact export for code and config state.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

class SnapshotManager:
    def __init__(self, repo_dir: str = ".", snapshot_dir: str = "snapshots"):
        self.repo_dir = Path(repo_dir)
        self.snapshot_dir = Path(snapshot_dir)
        if not self.snapshot_dir.exists():
            self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(self, tag: str = None) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        tag_part = f"_{tag}" if tag else ""
        snapshot_name = f"snapshot{tag_part}_{timestamp}"
        snapshot_path = self.snapshot_dir / snapshot_name
        shutil.make_archive(str(snapshot_path), 'zip', self.repo_dir)
        return snapshot_path.with_suffix('.zip')

    def list_snapshots(self) -> list:
        return sorted(self.snapshot_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)

    def export_snapshot(self, snapshot_path: Path, export_dir: Path) -> Path:
        export_dir.mkdir(parents=True, exist_ok=True)
        dest = export_dir / snapshot_path.name
        shutil.copy2(snapshot_path, dest)
        return dest

if __name__ == "__main__":
    sm = SnapshotManager()
    zipfile = sm.create_snapshot("demo")
    print(f"Created snapshot: {zipfile}")
