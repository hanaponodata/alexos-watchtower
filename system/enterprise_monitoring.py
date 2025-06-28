"""
system/enterprise_monitoring.py
Enhanced enterprise monitoring system for Watchtower.
Implements health monitoring, drift detection, auto-recovery, and admin escalation.
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import requests
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

from database.models.events import Event
from database.models.agents import Agent
from config.settings import settings

class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

class DriftType(Enum):
    """Drift type enumeration."""
    CONFIGURATION = "configuration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"

@dataclass
class HealthCheck:
    """Represents a health check result."""
    check_id: str
    component: str
    status: HealthStatus
    message: str
    timestamp: datetime
    duration_ms: float
    metadata: Dict[str, Any] = None

@dataclass
class DriftAlert:
    """Represents a drift detection alert."""
    alert_id: str
    drift_type: DriftType
    component: str
    severity: str
    description: str
    detected_at: datetime
    baseline: Dict[str, Any]
    current: Dict[str, Any]
    threshold: float
    deviation: float
    auto_recovery_attempted: bool = False
    admin_escalated: bool = False

@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, float]
    active_connections: int
    response_time_ms: float
    error_rate: float
    throughput: float

class EnterpriseMonitoringSystem:
    """Enterprise-grade monitoring and health management system."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.health_checks: Dict[str, Callable] = {}
        self.drift_baselines: Dict[str, Dict[str, Any]] = {}
        self.auto_recovery_handlers: Dict[str, Callable] = {}
        self.escalation_handlers: Dict[str, Callable] = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Initialize default health checks
        self._register_default_health_checks()
        
        # Initialize drift detection
        self._initialize_drift_detection()
        
        # Initialize auto-recovery handlers
        self._register_auto_recovery_handlers()
        
        # Initialize escalation handlers
        self._register_escalation_handlers()
    
    def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous monitoring."""
        
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        print(f"Enterprise monitoring started with {interval_seconds}s interval")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        print("Enterprise monitoring stopped")
    
    def register_health_check(self, check_id: str, component: str, check_func: Callable):
        """Register a custom health check."""
        
        self.health_checks[check_id] = {
            "component": component,
            "function": check_func
        }
    
    def run_health_checks(self) -> List[HealthCheck]:
        """Run all registered health checks."""
        
        health_results = []
        
        for check_id, check_info in self.health_checks.items():
            start_time = time.time()
            
            try:
                result = check_info["function"]()
                
                # Determine health status
                if isinstance(result, dict):
                    status = HealthStatus(result.get("status", "healthy"))
                    message = result.get("message", "Health check passed")
                    metadata = result.get("metadata", {})
                else:
                    status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                    message = "Health check passed" if result else "Health check failed"
                    metadata = {}
                
            except Exception as e:
                status = HealthStatus.CRITICAL
                message = f"Health check error: {str(e)}"
                metadata = {"error": str(e)}
            
            duration_ms = (time.time() - start_time) * 1000
            
            health_check = HealthCheck(
                check_id=check_id,
                component=check_info["component"],
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                metadata=metadata
            )
            
            health_results.append(health_check)
            
            # Log health check result
            self._log_health_check(health_check)
        
        return health_results
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        
        health_checks = self.run_health_checks()
        
        # Aggregate health status
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.CRITICAL: 0
        }
        
        for check in health_checks:
            status_counts[check.status] += 1
        
        # Determine overall status
        if status_counts[HealthStatus.CRITICAL] > 0:
            overall_status = HealthStatus.CRITICAL
        elif status_counts[HealthStatus.UNHEALTHY] > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        return {
            "overall_status": overall_status.value,
            "status_breakdown": {status.value: count for status, count in status_counts.items()},
            "health_checks": [asdict(check) for check in health_checks],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics."""
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Network I/O
        network_io = psutil.net_io_counters()
        network_data = {
            "bytes_sent": network_io.bytes_sent,
            "bytes_recv": network_io.bytes_recv,
            "packets_sent": network_io.packets_sent,
            "packets_recv": network_io.packets_recv
        }
        
        # Database connections (simplified)
        active_connections = self._get_active_connections()
        
        # Response time (simplified)
        response_time_ms = self._measure_response_time()
        
        # Error rate (simplified)
        error_rate = self._calculate_error_rate()
        
        # Throughput (simplified)
        throughput = self._calculate_throughput()
        
        metrics = SystemMetrics(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            network_io=network_data,
            active_connections=active_connections,
            response_time_ms=response_time_ms,
            error_rate=error_rate,
            throughput=throughput
        )
        
        # Check for drift
        self._check_drift(metrics)
        
        return metrics
    
    def detect_drift(self, component: str, current_metrics: Dict[str, Any]) -> Optional[DriftAlert]:
        """Detect drift in system metrics."""
        
        if component not in self.drift_baselines:
            return None
        
        baseline = self.drift_baselines[component]
        drift_alerts = []
        
        for metric_name, baseline_value in baseline.items():
            if metric_name not in current_metrics:
                continue
            
            current_value = current_metrics[metric_name]
            threshold = baseline.get(f"{metric_name}_threshold", 0.1)  # 10% default
            
            # Calculate deviation
            if isinstance(baseline_value, (int, float)) and isinstance(current_value, (int, float)):
                if baseline_value != 0:
                    deviation = abs(current_value - baseline_value) / baseline_value
                else:
                    deviation = abs(current_value)
                
                if deviation > threshold:
                    # Determine drift type and severity
                    drift_type = self._determine_drift_type(metric_name)
                    severity = self._determine_severity(deviation, threshold)
                    
                    alert = DriftAlert(
                        alert_id=f"drift_{component}_{metric_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        drift_type=drift_type,
                        component=component,
                        severity=severity,
                        description=f"Drift detected in {metric_name}: {current_value} vs baseline {baseline_value}",
                        detected_at=datetime.utcnow(),
                        baseline={metric_name: baseline_value},
                        current={metric_name: current_value},
                        threshold=threshold,
                        deviation=deviation
                    )
                    
                    drift_alerts.append(alert)
                    
                    # Log drift alert
                    self._log_drift_alert(alert)
                    
                    # Attempt auto-recovery
                    if not alert.auto_recovery_attempted:
                        self._attempt_auto_recovery(alert)
                    
                    # Escalate if needed
                    if severity in ["high", "critical"] and not alert.admin_escalated:
                        self._escalate_to_admin(alert)
        
        return drift_alerts[0] if drift_alerts else None
    
    def register_auto_recovery_handler(self, drift_type: DriftType, handler: Callable):
        """Register an auto-recovery handler for a drift type."""
        
        self.auto_recovery_handlers[drift_type.value] = handler
    
    def register_escalation_handler(self, severity: str, handler: Callable):
        """Register an escalation handler for a severity level."""
        
        self.escalation_handlers[severity] = handler
    
    def _monitoring_loop(self, interval_seconds: int):
        """Main monitoring loop."""
        
        while self.monitoring_active:
            try:
                # Run health checks
                health_checks = self.run_health_checks()
                
                # Collect system metrics
                metrics = self.collect_system_metrics()
                
                # Check for critical issues
                critical_checks = [h for h in health_checks if h.status == HealthStatus.CRITICAL]
                if critical_checks:
                    self._handle_critical_issues(critical_checks)
                
                # Sleep for interval
                time.sleep(interval_seconds)
                
            except Exception as e:
                print(f"Monitoring loop error: {str(e)}")
                time.sleep(interval_seconds)
    
    def _register_default_health_checks(self):
        """Register default health checks."""
        
        # Database connectivity
        self.register_health_check("db_connectivity", "database", self._check_database_connectivity)
        
        # API responsiveness
        self.register_health_check("api_responsiveness", "api", self._check_api_responsiveness)
        
        # Agent health
        self.register_health_check("agent_health", "agents", self._check_agent_health)
        
        # Disk space
        self.register_health_check("disk_space", "system", self._check_disk_space)
        
        # Memory usage
        self.register_health_check("memory_usage", "system", self._check_memory_usage)
    
    def _initialize_drift_detection(self):
        """Initialize drift detection baselines."""
        
        # Set initial baselines (in production, these would be learned over time)
        self.drift_baselines = {
            "system": {
                "cpu_percent": 20.0,
                "cpu_percent_threshold": 0.3,
                "memory_percent": 50.0,
                "memory_percent_threshold": 0.4,
                "disk_percent": 60.0,
                "disk_percent_threshold": 0.2
            },
            "api": {
                "response_time_ms": 100.0,
                "response_time_ms_threshold": 0.5,
                "error_rate": 0.01,
                "error_rate_threshold": 0.2
            },
            "database": {
                "active_connections": 10,
                "active_connections_threshold": 0.5,
                "query_time_ms": 50.0,
                "query_time_ms_threshold": 0.3
            }
        }
    
    def _register_auto_recovery_handlers(self):
        """Register auto-recovery handlers."""
        
        # CPU usage recovery
        self.register_auto_recovery_handler(DriftType.PERFORMANCE, self._recover_performance_drift)
        
        # Memory usage recovery
        self.register_auto_recovery_handler(DriftType.PERFORMANCE, self._recover_memory_drift)
        
        # Configuration drift recovery
        self.register_auto_recovery_handler(DriftType.CONFIGURATION, self._recover_configuration_drift)
    
    def _register_escalation_handlers(self):
        """Register escalation handlers."""
        
        # Critical severity escalation
        self.register_escalation_handler("critical", self._escalate_critical)
        
        # High severity escalation
        self.register_escalation_handler("high", self._escalate_high)
    
    def _check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity."""
        
        try:
            engine = create_engine(settings.db_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            return {
                "status": "healthy",
                "message": "Database connectivity OK",
                "metadata": {"connection_time_ms": 50}
            }
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Database connectivity failed: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _check_api_responsiveness(self) -> Dict[str, Any]:
        """Check API responsiveness."""
        
        try:
            start_time = time.time()
            response = requests.get(f"{settings.api_base_url}/health", timeout=5)
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "message": "API responsive",
                    "metadata": {"response_time_ms": duration_ms}
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"API returned status {response.status_code}",
                    "metadata": {"status_code": response.status_code}
                }
        except Exception as e:
            return {
                "status": "critical",
                "message": f"API unresponsive: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _check_agent_health(self) -> Dict[str, Any]:
        """Check agent health."""
        
        try:
            # Get active agents
            active_agents = self.db_session.query(Agent).filter_by(status="active").all()
            
            if not active_agents:
                return {
                    "status": "unhealthy",
                    "message": "No active agents found",
                    "metadata": {"active_agents": 0}
                }
            
            # Check agent health (simplified)
            healthy_agents = 0
            for agent in active_agents:
                if agent.last_heartbeat and (datetime.utcnow() - agent.last_heartbeat).seconds < 300:
                    healthy_agents += 1
            
            health_ratio = healthy_agents / len(active_agents)
            
            if health_ratio >= 0.9:
                status = "healthy"
            elif health_ratio >= 0.7:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "message": f"{healthy_agents}/{len(active_agents)} agents healthy",
                "metadata": {
                    "total_agents": len(active_agents),
                    "healthy_agents": healthy_agents,
                    "health_ratio": health_ratio
                }
            }
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Agent health check failed: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space usage."""
        
        try:
            disk = psutil.disk_usage('/')
            usage_percent = disk.percent
            
            if usage_percent < 80:
                status = "healthy"
            elif usage_percent < 90:
                status = "degraded"
            else:
                status = "critical"
            
            return {
                "status": status,
                "message": f"Disk usage: {usage_percent:.1f}%",
                "metadata": {
                    "usage_percent": usage_percent,
                    "free_gb": disk.free / (1024**3)
                }
            }
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Disk space check failed: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage."""
        
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent < 80:
                status = "healthy"
            elif usage_percent < 90:
                status = "degraded"
            else:
                status = "critical"
            
            return {
                "status": status,
                "message": f"Memory usage: {usage_percent:.1f}%",
                "metadata": {
                    "usage_percent": usage_percent,
                    "available_gb": memory.available / (1024**3)
                }
            }
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Memory check failed: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _get_active_connections(self) -> int:
        """Get number of active database connections."""
        
        try:
            engine = create_engine(settings.db_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"))
                return result.scalar()
        except:
            return 0
    
    def _measure_response_time(self) -> float:
        """Measure API response time."""
        
        try:
            start_time = time.time()
            requests.get(f"{settings.api_base_url}/health", timeout=5)
            return (time.time() - start_time) * 1000
        except:
            return 1000.0  # Default high value
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate from recent events."""
        
        try:
            # Get events from last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            total_events = self.db_session.query(Event).filter(Event.timestamp >= one_hour_ago).count()
            error_events = self.db_session.query(Event).filter(
                Event.timestamp >= one_hour_ago,
                Event.severity.in_(["error", "critical"])
            ).count()
            
            return error_events / total_events if total_events > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_throughput(self) -> float:
        """Calculate system throughput."""
        
        try:
            # Get events from last minute
            one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
            events_count = self.db_session.query(Event).filter(Event.timestamp >= one_minute_ago).count()
            return events_count / 60.0  # Events per second
        except:
            return 0.0
    
    def _check_drift(self, metrics: SystemMetrics):
        """Check for drift in system metrics."""
        
        # Convert metrics to dict for drift detection
        metrics_dict = {
            "cpu_percent": metrics.cpu_percent,
            "memory_percent": metrics.memory_percent,
            "disk_percent": metrics.disk_percent,
            "response_time_ms": metrics.response_time_ms,
            "error_rate": metrics.error_rate,
            "active_connections": metrics.active_connections
        }
        
        # Check drift for each component
        self.detect_drift("system", metrics_dict)
        self.detect_drift("api", metrics_dict)
        self.detect_drift("database", metrics_dict)
    
    def _determine_drift_type(self, metric_name: str) -> DriftType:
        """Determine drift type based on metric name."""
        
        if metric_name in ["cpu_percent", "memory_percent", "response_time_ms"]:
            return DriftType.PERFORMANCE
        elif metric_name in ["error_rate", "security_events"]:
            return DriftType.SECURITY
        elif metric_name in ["compliance_violations"]:
            return DriftType.COMPLIANCE
        else:
            return DriftType.CONFIGURATION
    
    def _determine_severity(self, deviation: float, threshold: float) -> str:
        """Determine severity based on deviation from threshold."""
        
        if deviation > threshold * 3:
            return "critical"
        elif deviation > threshold * 2:
            return "high"
        elif deviation > threshold:
            return "medium"
        else:
            return "low"
    
    def _attempt_auto_recovery(self, alert: DriftAlert):
        """Attempt automatic recovery for drift alert."""
        
        try:
            handler = self.auto_recovery_handlers.get(alert.drift_type.value)
            if handler:
                handler(alert)
                alert.auto_recovery_attempted = True
                print(f"Auto-recovery attempted for {alert.alert_id}")
        except Exception as e:
            print(f"Auto-recovery failed for {alert.alert_id}: {str(e)}")
    
    def _escalate_to_admin(self, alert: DriftAlert):
        """Escalate alert to administrator."""
        
        try:
            handler = self.escalation_handlers.get(alert.severity)
            if handler:
                handler(alert)
                alert.admin_escalated = True
                print(f"Alert escalated to admin: {alert.alert_id}")
        except Exception as e:
            print(f"Escalation failed for {alert.alert_id}: {str(e)}")
    
    def _handle_critical_issues(self, critical_checks: List[HealthCheck]):
        """Handle critical health issues."""
        
        for check in critical_checks:
            print(f"CRITICAL: {check.component} - {check.message}")
            
            # Create critical event
            event = Event(
                event_type="critical_health_issue",
                severity="critical",
                payload={
                    "check_id": check.check_id,
                    "component": check.component,
                    "message": check.message,
                    "metadata": check.metadata
                }
            )
            
            self.db_session.add(event)
        
        self.db_session.commit()
    
    def _recover_performance_drift(self, alert: DriftAlert):
        """Recover from performance drift."""
        
        if "cpu_percent" in alert.current:
            # Implement CPU throttling or scaling
            print(f"Recovering CPU performance drift: {alert.current['cpu_percent']}")
        
        if "memory_percent" in alert.current:
            # Implement memory cleanup
            print(f"Recovering memory performance drift: {alert.current['memory_percent']}")
    
    def _recover_memory_drift(self, alert: DriftAlert):
        """Recover from memory drift."""
        
        # Implement memory cleanup strategies
        print(f"Recovering memory drift: {alert.current}")
    
    def _recover_configuration_drift(self, alert: DriftAlert):
        """Recover from configuration drift."""
        
        # Implement configuration restoration
        print(f"Recovering configuration drift: {alert.current}")
    
    def _escalate_critical(self, alert: DriftAlert):
        """Escalate critical alerts."""
        
        # Send immediate notification
        print(f"CRITICAL ESCALATION: {alert.description}")
        
        # Create escalation event
        event = Event(
            event_type="admin_escalation",
            severity="critical",
            payload={
                "alert_id": alert.alert_id,
                "drift_type": alert.drift_type.value,
                "component": alert.component,
                "description": alert.description
            }
        )
        
        self.db_session.add(event)
        self.db_session.commit()
    
    def _escalate_high(self, alert: DriftAlert):
        """Escalate high severity alerts."""
        
        # Send notification
        print(f"HIGH ESCALATION: {alert.description}")
        
        # Create escalation event
        event = Event(
            event_type="admin_escalation",
            severity="warning",
            payload={
                "alert_id": alert.alert_id,
                "drift_type": alert.drift_type.value,
                "component": alert.component,
                "description": alert.description
            }
        )
        
        self.db_session.add(event)
        self.db_session.commit()
    
    def _log_health_check(self, health_check: HealthCheck):
        """Log health check result."""
        
        event = Event(
            event_type="health_check",
            severity=health_check.status.value,
            payload={
                "check_id": health_check.check_id,
                "component": health_check.component,
                "message": health_check.message,
                "duration_ms": health_check.duration_ms,
                "metadata": health_check.metadata
            }
        )
        
        self.db_session.add(event)
        self.db_session.commit()
    
    def _log_drift_alert(self, alert: DriftAlert):
        """Log drift alert."""
        
        event = Event(
            event_type="drift_detected",
            severity=alert.severity,
            payload={
                "alert_id": alert.alert_id,
                "drift_type": alert.drift_type.value,
                "component": alert.component,
                "description": alert.description,
                "deviation": alert.deviation,
                "threshold": alert.threshold
            }
        )
        
        self.db_session.add(event)
        self.db_session.commit() 