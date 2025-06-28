"""
selfaudit/analyzers/system.py
Enterprise-level system analyzer for Watchtower self-audit engine.
Performs real-time checks on CPU, memory, disk, and (basic) network health.
Handles empty or partial data robustly.
"""

import psutil
import socket
import time
from typing import Dict, Any, Optional

class SystemAnalyzer:
    def __init__(self, test_ping_host: Optional[str] = "8.8.8.8"):
        self.test_ping_host = test_ping_host

    def _get_network_latency(self) -> Optional[float]:
        # Basic network "ping" using socket connect (works on most systems)
        try:
            t0 = time.time()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((self.test_ping_host, 53))
            s.close()
            t1 = time.time()
            return round((t1 - t0) * 1000, 2)
        except Exception:
            return None

    def analyze(self) -> Dict[str, Any]:
        # Real system data
        try:
            cpu = psutil.cpu_percent(interval=0.3)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
            net_latency = self._get_network_latency()
        except Exception as e:
            return {
                "error": f"System metrics collection failed: {e}",
                "status": "critical"
            }
        resource_anomalies = cpu > 90 or mem > 90 or disk > 90 or (net_latency is not None and net_latency > 200)
        status = "critical" if resource_anomalies else "healthy"
        result = {
            "cpu_usage": cpu,
            "memory_usage": mem,
            "disk_usage": disk,
            "network_latency_ms": net_latency,
            "resource_anomalies": resource_anomalies,
            "status": status
        }
        return result

if __name__ == "__main__":
    analyzer = SystemAnalyzer()
    print(analyzer.analyze())
