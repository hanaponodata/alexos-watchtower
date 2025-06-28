"""
dashboard/api.py
FastAPI routes for the Watchtower dashboard.
Serves the dashboard UI and provides REST APIs for dashboard data.
"""

import os
import json
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import settings, logger
# from auth.rbac import get_current_user, User  # Temporarily disabled
from database.engine import get_session, SessionLocal
from database.models.agents import Agent
from database.models.events import Event
from websocket.dashboard import DashboardSocketHandler

# Pydantic models for API responses
class SystemStatus(BaseModel):
    uptime: str
    version: str
    environment: str
    node_id: str
    peers_count: int
    active_agents: int
    total_events: int
    system_health: str

class AgentSummary(BaseModel):
    id: str
    name: str
    status: str
    last_seen: datetime
    events_count: int
    health_score: float

    class Config:
        from_attributes = True

class EventSummary(BaseModel):
    id: str
    timestamp: datetime
    type: str
    severity: str
    source: str
    message: str

    class Config:
        from_attributes = True

class DashboardMetrics(BaseModel):
    system_status: SystemStatus
    recent_events: List[EventSummary]
    active_agents: List[AgentSummary]
    compliance_status: Dict[str, Any]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DashboardAPI:
    def __init__(self):
        self.router = APIRouter(prefix="/dashboard", tags=["dashboard"])
        self.setup_routes()
        self.dashboard_path = Path(__file__).parent / "frontend" / "build"
        
    def setup_routes(self):
        """Setup all dashboard routes."""
        
        @self.router.get("/", response_class=HTMLResponse)
        async def serve_dashboard():
            """Serve the main dashboard HTML."""
            index_path = self.dashboard_path / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            else:
                # Fallback to a simple HTML if React build doesn't exist
                return self._get_fallback_html()
        
        @self.router.get("/api/status")
        async def get_system_status(
            db: Session = Depends(get_db)
        ) -> SystemStatus:
            """Get system status and health metrics."""
            try:
                # Get real data from database
                uptime = await self._get_system_uptime()
                peers_count = await self._get_peers_count()
                active_agents = db.query(Agent).filter(Agent.status == "online").count()
                total_events = db.query(Event).count()
                
                return SystemStatus(
                    uptime=uptime,
                    version="1.0.0",
                    environment=settings.env,
                    node_id=settings.node_id,
                    peers_count=peers_count,
                    active_agents=active_agents,
                    total_events=total_events,
                    system_health="healthy"
                )
            except Exception as e:
                logger.error(f"Error getting system status: {e}")
                raise HTTPException(status_code=500, detail="Failed to get system status")
        
        @self.router.get("/api/agents")
        async def get_agents(
            db: Session = Depends(get_db),
            limit: int = Query(50, ge=1, le=100)
        ) -> List[AgentSummary]:
            """Get list of active agents."""
            try:
                # Get real agents from database
                agents = db.query(Agent).limit(limit).all()
                return [
                    AgentSummary(
                        id=str(agent.id),
                        name=agent.name,
                        status=agent.status,
                        last_seen=datetime.fromisoformat(str(agent.last_seen)) if agent.last_seen else datetime.utcnow(),
                        events_count=db.query(Event).filter(Event.agent_uuid == agent.uuid).count(),
                        health_score=agent.score / 100.0 if agent.score else 0.0
                    )
                    for agent in agents
                ]
            except Exception as e:
                logger.error(f"Error getting agents: {e}")
                raise HTTPException(status_code=500, detail="Failed to get agents")
        
        @self.router.get("/api/events")
        async def get_events(
            db: Session = Depends(get_db),
            limit: int = Query(100, ge=1, le=1000),
            severity: Optional[str] = Query(None),
            event_type: Optional[str] = Query(None)
        ) -> List[EventSummary]:
            """Get recent events with optional filtering."""
            try:
                query = db.query(Event)
                
                if severity:
                    query = query.filter(Event.severity == severity)
                if event_type:
                    query = query.filter(Event.event_type == event_type)
                
                events = query.order_by(Event.timestamp.desc()).limit(limit).all()
                
                return [
                    EventSummary(
                        id=str(event.id),
                        timestamp=datetime.fromisoformat(str(event.timestamp)),
                        type=event.event_type,
                        severity=event.severity,
                        source=event.source or "system",
                        message=str(event.payload.get("message", f"{event.event_type} event"))
                    )
                    for event in events
                ]
            except Exception as e:
                logger.error(f"Error getting events: {e}")
                raise HTTPException(status_code=500, detail="Failed to get events")
        
        @self.router.get("/api/metrics")
        async def get_dashboard_metrics(
            db: Session = Depends(get_db)
        ) -> DashboardMetrics:
            """Get comprehensive dashboard metrics."""
            try:
                system_status = await get_system_status(db)
                recent_events = await get_events(db, limit=20)
                active_agents = await get_agents(db, limit=10)
                compliance_status = await self._get_compliance_status()
                
                return DashboardMetrics(
                    system_status=system_status,
                    recent_events=recent_events,
                    active_agents=active_agents,
                    compliance_status=compliance_status
                )
            except Exception as e:
                logger.error(f"Error getting dashboard metrics: {e}")
                raise HTTPException(status_code=500, detail="Failed to get metrics")
        
        @self.router.get("/api/health")
        async def health_check() -> Dict[str, Any]:
            """Health check endpoint for the dashboard."""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        @self.router.get("/watchtower", response_class=HTMLResponse)
        async def serve_watchtower_dashboard():
            """Serve the Watchtower dashboard HTML."""
            watchtower_path = Path(__file__).parent / "templates" / "watchtower.html"
            if watchtower_path.exists():
                return FileResponse(watchtower_path)
            else:
                # Fallback to a simple HTML if template doesn't exist
                return HTMLResponse(content=self._get_watchtower_fallback_html())
        
        @self.router.get("/chainbot", response_class=HTMLResponse)
        async def serve_chainbot_dashboard():
            """Serve the ChainBot dashboard HTML."""
            chainbot_path = Path(__file__).parent / "templates" / "chainbot.html"
            if chainbot_path.exists():
                return FileResponse(chainbot_path)
            else:
                # Fallback to a simple HTML if template doesn't exist
                return HTMLResponse(content=self._get_chainbot_fallback_html())
    
    def _get_fallback_html(self) -> str:
        """Return a simple HTML dashboard if React build doesn't exist."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Watchtower Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .status { padding: 8px 16px; border-radius: 4px; color: white; display: inline-block; }
                .status.healthy { background: #28a745; }
                .status.warning { background: #ffc107; }
                .status.error { background: #dc3545; }
                h1 { color: #333; margin: 0 0 10px 0; }
                h2 { color: #666; margin: 0 0 15px 0; }
                .metric { font-size: 24px; font-weight: bold; color: #333; }
                .label { color: #666; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Watchtower Dashboard</h1>
                    <p>Enterprise-grade agentic, sovereign, extensible OS and protocol</p>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h2>System Status</h2>
                        <div class="status healthy">Healthy</div>
                        <div style="margin-top: 15px;">
                            <div class="metric" id="uptime">Loading...</div>
                            <div class="label">Uptime</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2>Active Agents</h2>
                        <div class="metric" id="agents">Loading...</div>
                        <div class="label">Connected Agents</div>
                    </div>
                    
                    <div class="card">
                        <h2>Events</h2>
                        <div class="metric" id="events">Loading...</div>
                        <div class="label">Total Events</div>
                    </div>
                    
                    <div class="card">
                        <h2>Peers</h2>
                        <div class="metric" id="peers">Loading...</div>
                        <div class="label">Connected Peers</div>
                    </div>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <h2>Recent Events</h2>
                    <div id="recent-events">Loading events...</div>
                </div>
            </div>
            
            <script>
                // Simple dashboard with real-time updates
                async function loadDashboard() {
                    try {
                        const response = await fetch('/dashboard/api/metrics');
                        const data = await response.json();
                        
                        document.getElementById('uptime').textContent = data.system_status.uptime;
                        document.getElementById('agents').textContent = data.system_status.active_agents;
                        document.getElementById('events').textContent = data.system_status.total_events;
                        document.getElementById('peers').textContent = data.system_status.peers_count;
                        
                        const eventsHtml = data.recent_events.map(event => 
                            `<div style="padding: 10px; border-bottom: 1px solid #eee;">
                                <strong>${event.type}</strong> - ${event.message}
                                <br><small>${new Date(event.timestamp).toLocaleString()}</small>
                            </div>`
                        ).join('');
                        document.getElementById('recent-events').innerHTML = eventsHtml;
                    } catch (error) {
                        console.error('Error loading dashboard:', error);
                    }
                }
                
                // Load initial data
                loadDashboard();
                
                // Refresh every 30 seconds
                setInterval(loadDashboard, 30000);
            </script>
        </body>
        </html>
        """
    
    async def _get_system_uptime(self) -> str:
        """Get system uptime."""
        try:
            import psutil
            uptime_seconds = time.time() - psutil.boot_time()
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"
    
    async def _get_peers_count(self) -> int:
        """Get number of connected peers."""
        # Mock data - replace with actual federation peer count
        return 3
    
    async def _get_active_agents_count(self) -> int:
        """Get number of active agents."""
        # Mock data - replace with actual agent count
        return 12
    
    async def _get_total_events_count(self) -> int:
        """Get total number of events."""
        # Mock data - replace with actual event count
        return 15420
    
    async def _get_agents_data(self, limit: int) -> List[AgentSummary]:
        """Get agents data."""
        # Mock data - replace with actual database queries
        return [
            AgentSummary(
                id=f"agent-{i}",
                name=f"Agent {i}",
                status="active" if i % 3 != 0 else "idle",
                last_seen=datetime.utcnow() - timedelta(minutes=i * 5),
                events_count=i * 10,
                health_score=0.95 - (i * 0.01)
            )
            for i in range(1, min(limit + 1, 11))
        ]
    
    async def _get_events_data(self, limit: int, severity: Optional[str], event_type: Optional[str]) -> List[EventSummary]:
        """Get events data."""
        # Mock data - replace with actual database queries
        event_types = ["system", "agent", "security", "compliance", "network"]
        severities = ["info", "warning", "error", "critical"]
        
        events = []
        for i in range(limit):
            event_type_val = event_types[i % len(event_types)]
            severity_val = severities[i % len(severities)]
            
            if severity and severity != severity_val:
                continue
            if event_type and event_type != event_type_val:
                continue
                
            events.append(EventSummary(
                id=f"event-{i}",
                timestamp=datetime.utcnow() - timedelta(minutes=i * 2),
                type=event_type_val,
                severity=severity_val,
                source=f"agent-{i % 5 + 1}",
                message=f"Sample {event_type_val} event {i}"
            ))
        
        return events[:limit]
    
    async def _get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status."""
        return {
            "overall_score": 95.5,
            "last_audit": datetime.utcnow().isoformat(),
            "violations": 2,
            "pending_reviews": 5,
            "certifications": ["SOC2", "GDPR", "ISO27001"]
        }

    def _get_watchtower_fallback_html(self) -> str:
        """Return a simple HTML fallback for the Watchtower dashboard."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Watchtower Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .status { padding: 8px 16px; border-radius: 4px; color: white; display: inline-block; }
                .status.healthy { background: #28a745; }
                .status.warning { background: #ffc107; }
                .status.error { background: #dc3545; }
                h1 { color: #333; margin: 0 0 10px 0; }
                h2 { color: #666; margin: 0 0 15px 0; }
                .metric { font-size: 24px; font-weight: bold; color: #333; }
                .label { color: #666; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Watchtower Dashboard</h1>
                    <p>Enterprise-grade agentic, sovereign, extensible OS and protocol</p>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h2>System Status</h2>
                        <div class="status healthy">Healthy</div>
                        <div style="margin-top: 15px;">
                            <div class="metric" id="uptime">Loading...</div>
                            <div class="label">Uptime</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2>Active Agents</h2>
                        <div class="metric" id="agents">Loading...</div>
                        <div class="label">Connected Agents</div>
                    </div>
                    
                    <div class="card">
                        <h2>Events</h2>
                        <div class="metric" id="events">Loading...</div>
                        <div class="label">Total Events</div>
                    </div>
                    
                    <div class="card">
                        <h2>Peers</h2>
                        <div class="metric" id="peers">Loading...</div>
                        <div class="label">Connected Peers</div>
                    </div>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <h2>Recent Events</h2>
                    <div id="recent-events">Loading events...</div>
                </div>
            </div>
            
            <script>
                // Simple dashboard with real-time updates
                async function loadDashboard() {
                    try {
                        const response = await fetch('/dashboard/api/metrics');
                        const data = await response.json();
                        
                        document.getElementById('uptime').textContent = data.system_status.uptime;
                        document.getElementById('agents').textContent = data.system_status.active_agents;
                        document.getElementById('events').textContent = data.system_status.total_events;
                        document.getElementById('peers').textContent = data.system_status.peers_count;
                        
                        const eventsHtml = data.recent_events.map(event => 
                            `<div style="padding: 10px; border-bottom: 1px solid #eee;">
                                <strong>${event.type}</strong> - ${event.message}
                                <br><small>${new Date(event.timestamp).toLocaleString()}</small>
                            </div>`
                        ).join('');
                        document.getElementById('recent-events').innerHTML = eventsHtml;
                    } catch (error) {
                        console.error('Error loading dashboard:', error);
                    }
                }
                
                // Load initial data
                loadDashboard();
                
                // Refresh every 30 seconds
                setInterval(loadDashboard, 30000);
            </script>
        </body>
        </html>
        """

    def _get_chainbot_fallback_html(self) -> str:
        """Return a simple HTML fallback for the ChainBot dashboard."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ChainBot Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .status { padding: 8px 16px; border-radius: 4px; color: white; display: inline-block; }
                .status.healthy { background: #28a745; }
                .status.warning { background: #ffc107; }
                .status.error { background: #dc3545; }
                h1 { color: #333; margin: 0 0 10px 0; }
                h2 { color: #666; margin: 0 0 15px 0; }
                .metric { font-size: 24px; font-weight: bold; color: #333; }
                .label { color: #666; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 ChainBot Dashboard</h1>
                    <p>Enterprise-grade agentic, sovereign, extensible OS and protocol</p>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h2>System Status</h2>
                        <div class="status healthy">Healthy</div>
                        <div style="margin-top: 15px;">
                            <div class="metric" id="uptime">Loading...</div>
                            <div class="label">Uptime</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2>Active Agents</h2>
                        <div class="metric" id="agents">Loading...</div>
                        <div class="label">Connected Agents</div>
                    </div>
                    
                    <div class="card">
                        <h2>Events</h2>
                        <div class="metric" id="events">Loading...</div>
                        <div class="label">Total Events</div>
                    </div>
                    
                    <div class="card">
                        <h2>Peers</h2>
                        <div class="metric" id="peers">Loading...</div>
                        <div class="label">Connected Peers</div>
                    </div>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <h2>Recent Events</h2>
                    <div id="recent-events">Loading events...</div>
                </div>
            </div>
            
            <script>
                // Simple dashboard with real-time updates
                async function loadDashboard() {
                    try {
                        const response = await fetch('/dashboard/api/metrics');
                        const data = await response.json();
                        
                        document.getElementById('uptime').textContent = data.system_status.uptime;
                        document.getElementById('agents').textContent = data.system_status.active_agents;
                        document.getElementById('events').textContent = data.system_status.total_events;
                        document.getElementById('peers').textContent = data.system_status.peers_count;
                        
                        const eventsHtml = data.recent_events.map(event => 
                            `<div style="padding: 10px; border-bottom: 1px solid #eee;">
                                <strong>${event.type}</strong> - ${event.message}
                                <br><small>${new Date(event.timestamp).toLocaleString()}</small>
                            </div>`
                        ).join('');
                        document.getElementById('recent-events').innerHTML = eventsHtml;
                    } catch (error) {
                        console.error('Error loading dashboard:', error);
                    }
                }
                
                // Load initial data
                loadDashboard();
                
                // Refresh every 30 seconds
                setInterval(loadDashboard, 30000);
            </script>
        </body>
        </html>
        """

# Create router instance
dashboard_api = DashboardAPI()
router = dashboard_api.router 