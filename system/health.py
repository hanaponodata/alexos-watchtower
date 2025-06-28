"""
system/health.py
Enterprise-grade system health monitor for Watchtower.
Performs live checks on system resources, process status, service uptime, and critical infrastructure.
"""

import psutil
import subprocess
from typing import Dict, Any, List

class SystemHealthMonitor:
    def __init__(self, critical_services: List[str] = None):
        self.critical_services = critical_services or []

    def resource_status(self) -> Dict[str, float]:
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        return {"cpu": cpu, "memory": mem, "disk": disk}

    def check_services(self) -> Dict[str, str]:
        status = {}
        for service in self.critical_services:
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", service],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                status[service] = result.stdout.decode().strip()
            except Exception:
                status[service] = "unknown"
        return status

    def full_health_check(self) -> Dict[str, Any]:
        resources = self.resource_status()
        services = self.check_services()
        issues = []
        for k, v in resources.items():
            if v > 90:
                issues.append(f"High {k}: {v}%")
        for svc, state in services.items():
            if state not in ("active", "running"):
                issues.append(f"Service {svc} not active: {state}")
        return {
            "resources": resources,
            "services": services,
            "issues": issues,
            "status": "critical" if issues else "healthy"
        }

if __name__ == "__main__":
    monitor = SystemHealthMonitor(critical_services=["postgresql", "docker"])
    print(monitor.full_health_check())
