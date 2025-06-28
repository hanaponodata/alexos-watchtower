"""
system/resource.py
Enterprise-grade resource monitor for Watchtower.
Tracks real-time and historical usage of CPU, memory, disk, and network I/O for adaptive scaling.
"""

import psutil
from typing import Dict, Any

class ResourceMonitor:
    def __init__(self):
        pass

    def collect_resource_stats(self) -> Dict[str, Any]:
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()
        return {
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "memory_used_mb": round(mem.used / (1024 * 1024), 2),
            "memory_total_mb": round(mem.total / (1024 * 1024), 2),
            "disk_percent": disk.percent,
            "disk_used_gb": round(disk.used / (1024 ** 3), 2),
            "disk_total_gb": round(disk.total / (1024 ** 3), 2),
            "net_bytes_sent_mb": round(net.bytes_sent / (1024 * 1024), 2),
            "net_bytes_recv_mb": round(net.bytes_recv / (1024 * 1024), 2)
        }

    def resource_history(self):
        # Placeholder: In production, persist to DB for long-term analytics
        # For now, this could log or export to a timeseries backend
        pass

if __name__ == "__main__":
    monitor = ResourceMonitor()
    print(monitor.collect_resource_stats())
