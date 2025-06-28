"""
api/audit.py
Audit API for Watchtower providing access to audit logs with forensic capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from database.engine import get_session
from database.models.audit import AuditLog
from api.auth import get_current_user
from config import settings, logger
from datetime import datetime, timedelta
import json
import csv
from io import StringIO

router = APIRouter(tags=["audit"])

class AuditLogResponse(BaseModel):
    id: int
    category: str
    actor: str
    action: str
    target: Optional[str]
    details: Dict[str, Any]
    severity: str
    timestamp: datetime
    hash_prev: Optional[str]
    hash_self: Optional[str]
    chain_id: Optional[str]
    signature: Optional[str]
    blockchain_tx: Optional[str]
    resolved: bool

class AuditLogFilter(BaseModel):
    category: Optional[str] = None
    actor: Optional[str] = None
    action: Optional[str] = None
    severity: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    resolved: Optional[bool] = None
    search: Optional[str] = None

class AuditStats(BaseModel):
    total_logs: int
    logs_by_category: Dict[str, int]
    logs_by_severity: Dict[str, int]
    logs_by_actor: Dict[str, int]
    recent_activity: List[Dict[str, Any]]

@router.get("/", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    actor: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    resolved: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get audit logs with filtering and pagination."""
    try:
        # Build query
        query = db.query(AuditLog)
        
        # Apply filters
        filters = []
        
        if category:
            filters.append(AuditLog.category == category)
        
        if actor:
            filters.append(AuditLog.actor == actor)
        
        if action:
            filters.append(AuditLog.action == action)
        
        if severity:
            filters.append(AuditLog.severity == severity)
        
        if start_date:
            filters.append(AuditLog.timestamp >= start_date)
        
        if end_date:
            filters.append(AuditLog.timestamp <= end_date)
        
        if resolved is not None:
            filters.append(AuditLog.resolved == resolved)
        
        if search:
            search_filter = or_(
                AuditLog.actor.contains(search),
                AuditLog.action.contains(search),
                AuditLog.target.contains(search)
            )
            filters.append(search_filter)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Order by timestamp (newest first)
        query = query.order_by(desc(AuditLog.timestamp))
        
        # Apply pagination
        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        
        # Log the audit query
        await _log_audit_query(
            db,
            current_user["username"],
            {
                "skip": skip,
                "limit": limit,
                "filters": {
                    "category": category,
                    "actor": actor,
                    "action": action,
                    "severity": severity,
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                    "resolved": resolved,
                    "search": search
                },
                "total_results": total
            }
        )
        
        return [
            AuditLogResponse(
                id=log.id,
                category=log.category,
                actor=log.actor,
                action=log.action,
                target=log.target,
                details=log.details,
                severity=log.severity,
                timestamp=log.timestamp,
                hash_prev=log.hash_prev,
                hash_self=log.hash_self,
                chain_id=log.chain_id,
                signature=log.signature,
                blockchain_tx=log.blockchain_tx,
                resolved=log.resolved
            )
            for log in logs
        ]
        
    except Exception as e:
        logger.error(f"Error fetching audit logs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch audit logs"
        )

@router.get("/stats", response_model=AuditStats)
async def get_audit_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get audit statistics for the specified time period."""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get total logs
        total_logs = db.query(AuditLog).filter(
            AuditLog.timestamp >= start_date
        ).count()
        
        # Get logs by category
        category_stats = {}
        category_results = db.query(
            AuditLog.category,
            db.func.count(AuditLog.id)
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(AuditLog.category).all()
        
        for category, count in category_results:
            category_stats[category] = count
        
        # Get logs by severity
        severity_stats = {}
        severity_results = db.query(
            AuditLog.severity,
            db.func.count(AuditLog.id)
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(AuditLog.severity).all()
        
        for severity, count in severity_results:
            severity_stats[severity] = count
        
        # Get logs by actor
        actor_stats = {}
        actor_results = db.query(
            AuditLog.actor,
            db.func.count(AuditLog.id)
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(AuditLog.actor).order_by(
            db.func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        for actor, count in actor_results:
            actor_stats[actor] = count
        
        # Get recent activity
        recent_logs = db.query(AuditLog).filter(
            AuditLog.timestamp >= start_date
        ).order_by(desc(AuditLog.timestamp)).limit(10).all()
        
        recent_activity = [
            {
                "id": log.id,
                "category": log.category,
                "actor": log.actor,
                "action": log.action,
                "severity": log.severity,
                "timestamp": log.timestamp.isoformat()
            }
            for log in recent_logs
        ]
        
        return AuditStats(
            total_logs=total_logs,
            logs_by_category=category_stats,
            logs_by_severity=severity_stats,
            logs_by_actor=actor_stats,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        logger.error(f"Error fetching audit stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch audit statistics"
        )

@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get specific audit log by ID."""
    try:
        log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
        
        if not log:
            raise HTTPException(
                status_code=404,
                detail="Audit log not found"
            )
        
        return AuditLogResponse(
            id=log.id,
            category=log.category,
            actor=log.actor,
            action=log.action,
            target=log.target,
            details=log.details,
            severity=log.severity,
            timestamp=log.timestamp,
            hash_prev=log.hash_prev,
            hash_self=log.hash_self,
            chain_id=log.chain_id,
            signature=log.signature,
            blockchain_tx=log.blockchain_tx,
            resolved=log.resolved
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching audit log {log_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch audit log"
        )

@router.put("/{log_id}/resolve")
async def resolve_audit_log(
    log_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Mark audit log as resolved."""
    try:
        log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
        
        if not log:
            raise HTTPException(
                status_code=404,
                detail="Audit log not found"
            )
        
        log.resolved = True
        db.commit()
        
        # Log the resolution
        await _log_audit_query(
            db,
            current_user["username"],
            {
                "action": "resolve_audit_log",
                "log_id": log_id,
                "previous_status": False,
                "new_status": True
            }
        )
        
        return {"message": "Audit log marked as resolved"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving audit log {log_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to resolve audit log"
        )

@router.get("/export/csv")
async def export_audit_logs_csv(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    category: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Export audit logs to CSV format."""
    try:
        # Build query
        query = db.query(AuditLog)
        
        # Apply filters
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        if category:
            query = query.filter(AuditLog.category == category)
        
        # Get all logs
        logs = query.order_by(desc(AuditLog.timestamp)).all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID", "Category", "Actor", "Action", "Target", "Severity",
            "Timestamp", "Details", "Resolved", "Chain ID", "Signature"
        ])
        
        # Write data
        for log in logs:
            writer.writerow([
                log.id,
                log.category,
                log.actor,
                log.action,
                log.target or "",
                log.severity,
                log.timestamp.isoformat(),
                json.dumps(log.details),
                log.resolved,
                log.chain_id or "",
                log.signature or ""
            ])
        
        # Log the export
        await _log_audit_query(
            db,
            current_user["username"],
            {
                "action": "export_audit_logs_csv",
                "filters": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                    "category": category
                },
                "exported_count": len(logs)
            }
        )
        
        return {
            "csv_data": output.getvalue(),
            "filename": f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
            "record_count": len(logs)
        }
        
    except Exception as e:
        logger.error(f"Error exporting audit logs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to export audit logs"
        )

@router.get("/categories")
async def get_audit_categories(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get list of available audit categories."""
    try:
        categories = db.query(AuditLog.category).distinct().all()
        return [category[0] for category in categories]
        
    except Exception as e:
        logger.error(f"Error fetching audit categories: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch audit categories"
        )

@router.get("/actors")
async def get_audit_actors(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get list of audit actors."""
    try:
        actors = db.query(AuditLog.actor).distinct().order_by(AuditLog.actor).all()
        return [actor[0] for actor in actors]
        
    except Exception as e:
        logger.error(f"Error fetching audit actors: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch audit actors"
        )

async def _log_audit_query(db: Session, actor: str, details: Dict[str, Any]):
    """Log audit query for tracking."""
    try:
        audit_log = AuditLog(
            category="audit",
            actor=actor,
            action="audit_query",
            target="audit_logs",
            details=details,
            severity="info",
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log audit query: {e}") 