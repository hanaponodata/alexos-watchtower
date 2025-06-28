"""
selfaudit/core.py
Central self-audit engine for Watchtower.
Schedules, orchestrates, and runs recursive audits using modular analyzers.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from .analyzers.log import LogAnalyzer
from .analyzers.agent import AgentAnalyzer
from .analyzers.system import SystemAnalyzer
from .analyzers.upgrade import UpgradeAnalyzer
from .analyzers.config import ConfigAnalyzer
from .analyzers.protocol import ProtocolAnalyzer
from .lineage import LineageManager
from .report import AuditReportGenerator

class SelfAuditEngine:
    def __init__(self, interval_minutes: int = 60):
        self.logger = logging.getLogger("watchtower.selfaudit")
        self.interval = timedelta(minutes=interval_minutes)
        self.last_run: Optional[datetime] = None
        # Instantiate analyzers and managers
        self.log_analyzer = LogAnalyzer()
        self.agent_analyzer = AgentAnalyzer()
        self.system_analyzer = SystemAnalyzer()
        self.upgrade_analyzer = UpgradeAnalyzer()
        self.config_analyzer = ConfigAnalyzer()
        self.protocol_analyzer = ProtocolAnalyzer()
        self.lineage_manager = LineageManager()
        self.report_generator = AuditReportGenerator()

    def run_audit(self) -> Dict[str, Any]:
        """Run a full self-audit cycle and return results."""
        self.logger.info("Starting self-audit cycle...")
        results = {
            "log": self.log_analyzer.analyze(),
            "agent": self.agent_analyzer.analyze(),
            "system": self.system_analyzer.analyze(),
            "upgrade": self.upgrade_analyzer.analyze(),
            "config": self.config_analyzer.analyze(),
            "protocol": self.protocol_analyzer.analyze(),
            "lineage": self.lineage_manager.analyze(),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.last_run = datetime.utcnow()
        # Generate and persist report
        self.report_generator.generate_report(results)
        self.logger.info("Self-audit complete.")
        return results

    def schedule(self):
        """
        Optionally, integrate with APScheduler or a similar task scheduler
        to run self-audit at defined intervals.
        """
        # TODO: Add integration with scheduler if needed
        pass

if __name__ == "__main__":
    engine = SelfAuditEngine()
    results = engine.run_audit()
    print("Audit Results:", results)
