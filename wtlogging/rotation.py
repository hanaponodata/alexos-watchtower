"""
logging/rotation.py
Log rotation and archival manager for Watchtower.
Handles periodic, size-based, and retention-based rotation for all logs.
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

DEFAULT_LOG_DIR = Path(os.environ.get("WATCHTOWER_LOG_DIR", "logs"))
DEFAULT_RETENTION = int(os.environ.get("WATCHTOWER_LOG_BACKUP_COUNT", "7"))  # number of rotated logs to keep

class LogRotator:
    def __init__(self, log_dir: Path = DEFAULT_LOG_DIR, retention: int = DEFAULT_RETENTION):
        self.log_dir = log_dir
        self.retention = retention
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("watchtower.rotation")

    def rotate_log(self, log_name: str):
        """Rotate a log file and enforce retention policy."""
        log_path = self.log_dir / log_name
        if not log_path.exists():
            self.logger.warning(f"Log file {log_path} does not exist for rotation.")
            return False
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        rotated_name = f"{log_name}.{timestamp}"
        rotated_path = self.log_dir / rotated_name
        shutil.move(str(log_path), str(rotated_path))
        self.logger.info(f"Rotated log: {log_path} -> {rotated_path}")
        self._enforce_retention(log_name)
        return True

    def _enforce_retention(self, log_name: str):
        """Remove old rotated logs exceeding the retention count."""
        rotated_logs = sorted(self.log_dir.glob(f"{log_name}.*"), key=lambda f: f.stat().st_mtime, reverse=True)
        for old_log in rotated_logs[self.retention:]:
            try:
                old_log.unlink()
                self.logger.info(f"Deleted old rotated log: {old_log}")
            except Exception as e:
                self.logger.error(f"Failed to delete {old_log}: {e}")

if __name__ == "__main__":
    rotator = LogRotator()
    print("LogRotator ready (use rotate_log to rotate specific logs).")
