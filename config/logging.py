"""
config/logging.py
Centralized logging configuration for Watchtower.
Supports file/console logging, rotation, JSON logs, audit trails, and plugin/extensibility.
"""

import logging
import logging.config
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

DEFAULT_LOG_DIR = Path(os.environ.get("WATCHTOWER_LOG_DIR", "logs"))
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "watchtower.log"
DEFAULT_LOG_LEVEL = os.environ.get("WATCHTOWER_LOG_LEVEL", "INFO")
DEFAULT_LOG_ROTATION = int(os.environ.get("WATCHTOWER_LOG_ROTATION_MB", "10")) * 1024 * 1024  # MB to bytes
DEFAULT_LOG_BACKUP_COUNT = int(os.environ.get("WATCHTOWER_LOG_BACKUP_COUNT", "7"))

def ensure_log_dir(log_dir: Path = DEFAULT_LOG_DIR):
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)

def get_logging_config(
    log_dir: Path = DEFAULT_LOG_DIR,
    log_file: Path = DEFAULT_LOG_FILE,
    level: str = DEFAULT_LOG_LEVEL,
    rotation: int = DEFAULT_LOG_ROTATION,
    backup_count: int = DEFAULT_LOG_BACKUP_COUNT
):
    ensure_log_dir(log_dir)
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": str(log_file),
                "maxBytes": rotation,
                "backupCount": backup_count,
                "level": level
            },
            # Optional: JSON file handler for audit logs
            "audit_json": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": str(log_dir / "audit.json.log"),
                "maxBytes": rotation,
                "backupCount": backup_count,
                "level": "INFO"
            }
        },
        "root": {
            "handlers": ["console", "file"],
            "level": level
        },
        "loggers": {
            "audit": {
                "handlers": ["audit_json"],
                "level": "INFO",
                "propagate": False
            }
        }
    }

def setup_logging():
    """Apply logging config globally."""
    import sys
    try:
        import pythonjsonlogger  # For JSON audit logs
    except ImportError:
        print("[WARN] python-json-logger not installed, JSON audit logs will be unavailable.")
    logging_config = get_logging_config()
    logging.config.dictConfig(logging_config)
    logging.info("Logging initialized.")
    return logging.getLogger("watchtower")

# Exported logger for global use
logger = setup_logging()

if __name__ == "__main__":
    logger.info("Watchtower logging test (INFO).")
    logger.error("Watchtower logging test (ERROR).")
    logging.getLogger("audit").info("This is an audit event (JSON logger).")
