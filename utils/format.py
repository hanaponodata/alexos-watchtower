"""
utils/format.py
Enterprise-grade formatting utilities for Watchtower.
Supports time, size, log, and output formatting for reports, dashboards, and logs.
"""

from datetime import datetime
from typing import Union

class FormatUtils:
    @staticmethod
    def format_time(ts: Union[datetime, str], fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        if isinstance(ts, datetime):
            return ts.strftime(fmt)
        try:
            return datetime.fromisoformat(ts).strftime(fmt)
        except Exception:
            return str(ts)

    @staticmethod
    def format_size(num_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if num_bytes < 1024.0:
                return f"{num_bytes:3.1f} {unit}"
            num_bytes /= 1024.0
        return f"{num_bytes:.1f} PB"

    @staticmethod
    def format_log(level: str, message: str, ts: Union[datetime, str] = None) -> str:
        ts_str = FormatUtils.format_time(ts or datetime.utcnow())
        return f"[{ts_str}][{level.upper()}] {message}"

if __name__ == "__main__":
    print(FormatUtils.format_time(datetime.utcnow()))
    print(FormatUtils.format_size(123456789))
    print(FormatUtils.format_log("info", "Watchtower log message"))
