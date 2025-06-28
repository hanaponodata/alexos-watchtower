"""
utils/logger.py
Enterprise-grade logger utility for Watchtower.
Provides unified logging setup, formatting, and context-aware logging across modules.
"""

import logging
import sys

class LoggerUtils:
    @staticmethod
    def setup_logger(
        name: str,
        level: str = "INFO",
        fmt: str = "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
        stream = sys.stdout
    ) -> logging.Logger:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler(stream)
            formatter = logging.Formatter(fmt)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(level)
        return logger

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)

if __name__ == "__main__":
    logger = LoggerUtils.setup_logger("watchtower.test", level="DEBUG")
    logger.info("LoggerUtils ready.")
