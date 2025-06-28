"""
system/recovery.py
Enterprise-grade self-healing and recovery manager for Watchtower.
Monitors failures, restarts services, and triggers system recovery actions.
"""

import subprocess
import logging
from typing import List

class SelfHealingManager:
    def __init__(self, critical_services: List[str] = None):
        self.critical_services = critical_services or []
        self.logger = logging.getLogger("watchtower.recovery")

    def restart_service(self, service: str) -> bool:
        try:
            subprocess.run(
                ["systemctl", "restart", service],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            self.logger.info(f"Restarted service: {service}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restart {service}: {e}")
            return False

    def auto_recover(self):
        # Check services and restart any that are not running
        for svc in self.critical_services:
            status = subprocess.run(
                ["systemctl", "is-active", svc],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            if status.stdout.decode().strip() not in ("active", "running"):
                self.logger.warning(f"Service {svc} not running, attempting restart.")
                self.restart_service(svc)

if __name__ == "__main__":
    mgr = SelfHealingManager(critical_services=["postgresql", "docker"])
    mgr.auto_recover()
    print("Self-healing routine complete.")
