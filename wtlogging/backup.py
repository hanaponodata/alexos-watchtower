"""
logging/backup.py
Log backup and export manager for Watchtower.
Handles scheduled/local/network backup, snapshotting, and export to remote storage.
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

DEFAULT_LOG_DIR = Path(os.environ.get("WATCHTOWER_LOG_DIR", "logs"))
DEFAULT_BACKUP_DIR = Path(os.environ.get("WATCHTOWER_LOG_BACKUP_DIR", "log_backups"))

class LogBackupManager:
    def __init__(self, log_dir: Path = DEFAULT_LOG_DIR, backup_dir: Path = DEFAULT_BACKUP_DIR):
        self.log_dir = log_dir
        self.backup_dir = backup_dir
        self.logger = logging.getLogger("watchtower.logbackup")
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True, exist_ok=True)

    def backup_logs(self):
        """Copy all log files to backup directory with timestamp."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        for log_file in self.log_dir.glob("*.log"):
            dest = self.backup_dir / f"{log_file.stem}.{timestamp}.log"
            shutil.copy2(log_file, dest)
            self.logger.info(f"Backed up log: {log_file} -> {dest}")

    def export_logs(self, export_path: Path):
        """Export all log files to a given external path."""
        export_path.mkdir(parents=True, exist_ok=True)
        for log_file in self.log_dir.glob("*.log"):
            dest = export_path / log_file.name
            shutil.copy2(log_file, dest)
            self.logger.info(f"Exported log: {log_file} -> {dest}")

if __name__ == "__main__":
    mgr = LogBackupManager()
    mgr.backup_logs()
    print("Log backup complete.")
