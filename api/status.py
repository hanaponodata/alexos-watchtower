"""
api/status.py
System status and health check API endpoints for Watchtower.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database.engine import get_session
from database.models.agents import Agent
from database.models.events import Event
from config import settings
import psutil
import os
import time
from datetime import datetime, timedelta
from sqlalchemy import text

router = APIRouter(tags=["status"])

class SystemStatus(BaseModel):
    status: str
    version: str
    uptime: str
    environment: str
    node_id: str
    timestamp: datetime
    system_metrics: Dict[str, Any]
    database_status: str
    active_agents: int
    total_events: int
    recent_events: int

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    checks: Dict[str, str]

@router.get("/", response_model=SystemStatus)
def get_system_status(db: Session = Depends(get_session)):
    """Get comprehensive system status."""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get uptime
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_days = int(uptime_seconds // 86400)
        uptime_hours = int((uptime_seconds % 86400) // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        uptime_str = f"{uptime_days}d {uptime_hours}h {uptime_minutes}m"
        
        # Get database stats
        active_agents = db.query(Agent).filter(Agent.status == "online").count()
        total_events = db.query(Event).count()
        recent_events = db.query(Event).filter(
            Event.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        # Check database connection
        try:
            db.execute(text("SELECT 1"))
            db_status = "healthy"
        except Exception:
            db_status = "unhealthy"
        
        return SystemStatus(
            status="healthy",
            version="1.0.0",
            uptime=uptime_str,
            environment=settings.env,
            node_id=settings.node_id,
            timestamp=datetime.utcnow(),
            system_metrics={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
                "disk_total": disk.total
            },
            database_status=db_status,
            active_agents=active_agents,
            total_events=total_events,
            recent_events=recent_events
        )
    except Exception as e:
        return SystemStatus(
            status="degraded",
            version="1.0.0",
            uptime="unknown",
            environment=settings.env,
            node_id=settings.node_id,
            timestamp=datetime.utcnow(),
            system_metrics={},
            database_status="error",
            active_agents=0,
            total_events=0,
            recent_events=0
        )

@router.get("/health", response_model=HealthCheck)
def health_check():
    """Simple health check endpoint."""
    checks = {}
    
    # Check system resources
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        checks["cpu"] = "healthy" if cpu_percent < 90 else "warning"
        checks["memory"] = "healthy" if memory.percent < 90 else "warning"
    except Exception:
        checks["system"] = "error"
    
    # Check disk space
    try:
        disk = psutil.disk_usage('/')
        checks["disk"] = "healthy" if disk.percent < 90 else "warning"
    except Exception:
        checks["disk"] = "error"
    
    # Determine overall status
    if "error" in checks.values():
        status = "unhealthy"
    elif "warning" in checks.values():
        status = "degraded"
    else:
        status = "healthy"
    
    return HealthCheck(
        status=status,
        timestamp=datetime.utcnow(),
        checks=checks
    )

@router.get("/metrics")
def get_metrics():
    """Get system metrics for monitoring."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count(),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            },
            "network": {
                "connections": len(psutil.net_connections()),
                "interfaces": len(psutil.net_if_addrs())
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
