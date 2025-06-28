"""
api/events.py
Event logging and querying API endpoints for Watchtower.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from database.engine import get_session
from database.models.events import Event
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/events", tags=["events"])

class EventCreate(BaseModel):
    event_type: str = Field(..., description="Type of event")
    agent_uuid: Optional[str] = Field(None, description="Associated agent UUID")
    severity: str = Field("info", description="Event severity: info, warning, error, critical")
    payload: dict = Field(default_factory=dict, description="Event payload data")
    source: Optional[str] = Field(None, description="Event source")

class EventOut(BaseModel):
    id: int
    event_type: str
    agent_uuid: Optional[str]
    timestamp: datetime
    severity: str
    payload: dict
    source: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=EventOut)
def create_event(event: EventCreate, db: Session = Depends(get_session)):
    """Create a new event."""
    db_event = Event(
        event_type=event.event_type,
        agent_uuid=event.agent_uuid,
        severity=event.severity,
        payload=event.payload,
        source=event.source
    )
    db.add(db_event)
    try:
        db.commit()
        db.refresh(db_event)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Event creation failed: {e}")
    return db_event

@router.get("/", response_model=List[EventOut])
def list_events(
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    agent_uuid: Optional[str] = Query(None),
    db: Session = Depends(get_session)
):
    """List events with optional filtering."""
    query = db.query(Event)
    
    if severity:
        query = query.filter(Event.severity == severity)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if agent_uuid:
        query = query.filter(Event.agent_uuid == agent_uuid)
    
    events = query.order_by(Event.timestamp.desc()).limit(limit).all()
    return events

@router.get("/recent", response_model=List[EventOut])
def get_recent_events(
    hours: int = Query(24, ge=1, le=168),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_session)
):
    """Get recent events from the last N hours."""
    since = datetime.utcnow() - timedelta(hours=hours)
    query = db.query(Event).filter(Event.timestamp >= since)
    
    if severity:
        query = query.filter(Event.severity == severity)
    
    events = query.order_by(Event.timestamp.desc()).all()
    return events

@router.get("/stats")
def get_event_stats(db: Session = Depends(get_session)):
    """Get event statistics."""
    total_events = db.query(Event).count()
    critical_events = db.query(Event).filter(Event.severity == "critical").count()
    error_events = db.query(Event).filter(Event.severity == "error").count()
    warning_events = db.query(Event).filter(Event.severity == "warning").count()
    info_events = db.query(Event).filter(Event.severity == "info").count()
    
    return {
        "total": total_events,
        "critical": critical_events,
        "error": error_events,
        "warning": warning_events,
        "info": info_events
    }
