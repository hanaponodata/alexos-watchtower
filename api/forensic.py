"""
api/forensic.py
Forensic API for Watchtower providing system snapshots, state dumps, and forensic recall.
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
import hashlib
import hmac
import os
import psutil
import platform
from pathlib import Path
import tarfile
import tempfile

router = APIRouter(tags=["forensic"])

class ForensicSnapshot(BaseModel):
    id: str
    snapshot_type: str
    timestamp: datetime
    description: str
    checksum: str
    size_bytes: int
    metadata: Dict[str, Any]
    chain_of_custody: List[Dict[str, Any]]
    signature: Optional[str]
    blockchain_tx: Optional[str]

class SnapshotRequest(BaseModel):
    snapshot_type: str
    description: str
    include_audit_logs: bool = True
    include_system_state: bool = True
    include_database: bool = False
    include_files: bool = False

class SnapshotResponse(BaseModel):
    snapshot_id: str
    status: str
    message: str
    checksum: str
    size_bytes: int
    download_url: Optional[str]

@router.post("/snapshots", response_model=SnapshotResponse)
async def create_forensic_snapshot(
    request: SnapshotRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Create a forensic snapshot of the system state."""
    try:
        snapshot_id = f"snapshot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(request.dict()).encode()).hexdigest()[:8]}"
        
        # Create snapshot directory
        snapshot_dir = Path(settings.backup_dir) / "forensic" / snapshot_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize chain of custody
        chain_of_custody = [{
            "timestamp": datetime.utcnow().isoformat(),
            "actor": current_user["username"],
            "action": "snapshot_created",
            "details": request.dict()
        }]
        
        # Collect system state
        system_state = {}
        if request.include_system_state:
            system_state = {
                "timestamp": datetime.utcnow().isoformat(),
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "processes": len(psutil.pids()),
                "network_connections": len(psutil.net_connections()),
                "environment": dict(os.environ)
            }
            
            # Save system state
            with open(snapshot_dir / "system_state.json", "w") as f:
                json.dump(system_state, f, indent=2, default=str)
        
        # Collect audit logs
        if request.include_audit_logs:
            audit_logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10000).all()
            audit_data = []
            for log in audit_logs:
                audit_data.append({
                    "id": log.id,
                    "category": log.category,
                    "actor": log.actor,
                    "action": log.action,
                    "target": log.target,
                    "details": log.details,
                    "severity": log.severity,
                    "timestamp": log.timestamp.isoformat(),
                    "hash_prev": log.hash_prev,
                    "hash_self": log.hash_self,
                    "chain_id": log.chain_id,
                    "signature": log.signature,
                    "blockchain_tx": log.blockchain_tx,
                    "resolved": log.resolved
                })
            
            # Save audit logs
            with open(snapshot_dir / "audit_logs.json", "w") as f:
                json.dump(audit_data, f, indent=2, default=str)
        
        # Create metadata
        metadata = {
            "snapshot_type": request.snapshot_type,
            "description": request.description,
            "created_by": current_user["username"],
            "created_at": datetime.utcnow().isoformat(),
            "components": {
                "system_state": request.include_system_state,
                "audit_logs": request.include_audit_logs,
                "database": request.include_database,
                "files": request.include_files
            },
            "system_info": {
                "node_id": settings.node_id,
                "environment": settings.env,
                "version": "1.0.0"
            }
        }
        
        # Save metadata
        with open(snapshot_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        
        # Create archive
        archive_path = snapshot_dir.parent / f"{snapshot_id}.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(snapshot_dir, arcname=snapshot_id)
        
        # Calculate checksum
        with open(archive_path, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        
        # Create signature
        signature = None
        if settings.admin_key:
            signature_data = f"{snapshot_id}:{checksum}:{datetime.utcnow().isoformat()}"
            signature = hmac.new(
                settings.admin_key.encode(),
                signature_data.encode(),
                hashlib.sha256
            ).hexdigest()
        
        # Update chain of custody
        chain_of_custody.append({
            "timestamp": datetime.utcnow().isoformat(),
            "actor": "system",
            "action": "snapshot_completed",
            "details": {
                "checksum": checksum,
                "size_bytes": archive_path.stat().st_size,
                "signature": signature
            }
        })
        
        # Save chain of custody
        with open(snapshot_dir / "chain_of_custody.json", "w") as f:
            json.dump(chain_of_custody, f, indent=2, default=str)
        
        # Log forensic event
        await _log_forensic_event(
            db,
            current_user["username"],
            "forensic_snapshot_created",
            "forensic_snapshot",
            {
                "snapshot_id": snapshot_id,
                "snapshot_type": request.snapshot_type,
                "checksum": checksum,
                "size_bytes": archive_path.stat().st_size
            },
            "info"
        )
        
        return SnapshotResponse(
            snapshot_id=snapshot_id,
            status="completed",
            message="Forensic snapshot created successfully",
            checksum=checksum,
            size_bytes=archive_path.stat().st_size,
            download_url=f"/api/forensic/snapshots/{snapshot_id}/download"
        )
        
    except Exception as e:
        logger.error(f"Failed to create forensic snapshot: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create forensic snapshot"
        )

@router.get("/snapshots", response_model=List[ForensicSnapshot])
async def list_forensic_snapshots(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    snapshot_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """List forensic snapshots with filtering and pagination."""
    try:
        snapshot_dir = Path(settings.backup_dir) / "forensic"
        if not snapshot_dir.exists():
            return []
        
        snapshots = []
        for archive_file in snapshot_dir.glob("*.tar.gz"):
            try:
                # Extract metadata from archive
                with tarfile.open(archive_file, "r:gz") as tar:
                    metadata_file = None
                    for member in tar.getmembers():
                        if member.name.endswith("/metadata.json"):
                            metadata_file = member
                            break
                    
                    if metadata_file:
                        extract_file = tar.extractfile(metadata_file)
                        if extract_file:
                            metadata_content = extract_file.read()
                            metadata = json.loads(metadata_content)
                            
                            # Apply filters
                            if snapshot_type and metadata.get("snapshot_type") != snapshot_type:
                                continue
                            
                            created_at = datetime.fromisoformat(metadata["created_at"])
                            if start_date and created_at < start_date:
                                continue
                            if end_date and created_at > end_date:
                                continue
                            
                            # Calculate checksum
                            with open(archive_file, "rb") as f:
                                checksum = hashlib.sha256(f.read()).hexdigest()
                            
                            snapshot = ForensicSnapshot(
                                id=archive_file.stem,
                                snapshot_type=metadata["snapshot_type"],
                                timestamp=created_at,
                                description=metadata["description"],
                                checksum=checksum,
                                size_bytes=archive_file.stat().st_size,
                                metadata=metadata,
                                chain_of_custody=[],  # Would need to extract from archive
                                signature=None,  # Would need to extract from archive
                                blockchain_tx=None
                            )
                            snapshots.append(snapshot)
                        
            except Exception as e:
                logger.error(f"Error reading snapshot {archive_file}: {e}")
                continue
        
        # Sort by timestamp (newest first)
        snapshots.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        total = len(snapshots)
        snapshots = snapshots[skip:skip + limit]
        
        return snapshots
        
    except Exception as e:
        logger.error(f"Error listing forensic snapshots: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list forensic snapshots"
        )

@router.get("/snapshots/{snapshot_id}")
async def get_forensic_snapshot(
    snapshot_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get detailed information about a specific forensic snapshot."""
    try:
        archive_path = Path(settings.backup_dir) / "forensic" / f"{snapshot_id}.tar.gz"
        if not archive_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Forensic snapshot not found"
            )
        
        # Extract metadata
        with tarfile.open(archive_path, "r:gz") as tar:
            metadata_file = None
            chain_file = None
            for member in tar.getmembers():
                if member.name.endswith("/metadata.json"):
                    metadata_file = member
                elif member.name.endswith("/chain_of_custody.json"):
                    chain_file = member
            
            metadata = {}
            if metadata_file:
                extract_file = tar.extractfile(metadata_file)
                if extract_file:
                    metadata_content = extract_file.read()
                    metadata = json.loads(metadata_content)
            
            chain_of_custody = []
            if chain_file:
                extract_file = tar.extractfile(chain_file)
                if extract_file:
                    chain_content = extract_file.read()
                    chain_of_custody = json.loads(chain_content)
        
        # Calculate checksum
        with open(archive_path, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        
        return ForensicSnapshot(
            id=snapshot_id,
            snapshot_type=metadata.get("snapshot_type", "unknown"),
            timestamp=datetime.fromisoformat(metadata.get("created_at", datetime.utcnow().isoformat())),
            description=metadata.get("description", ""),
            checksum=checksum,
            size_bytes=archive_path.stat().st_size,
            metadata=metadata,
            chain_of_custody=chain_of_custody,
            signature=None,  # Would need to extract from archive
            blockchain_tx=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting forensic snapshot {snapshot_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get forensic snapshot"
        )

@router.get("/snapshots/{snapshot_id}/download")
async def download_forensic_snapshot(
    snapshot_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Download a forensic snapshot archive."""
    try:
        archive_path = Path(settings.backup_dir) / "forensic" / f"{snapshot_id}.tar.gz"
        if not archive_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Forensic snapshot not found"
            )
        
        # Log download event
        from fastapi.responses import FileResponse
        return FileResponse(
            path=archive_path,
            filename=f"{snapshot_id}.tar.gz",
            media_type="application/gzip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading forensic snapshot {snapshot_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to download forensic snapshot"
        )

@router.delete("/snapshots/{snapshot_id}")
async def delete_forensic_snapshot(
    snapshot_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Delete a forensic snapshot."""
    try:
        archive_path = Path(settings.backup_dir) / "forensic" / f"{snapshot_id}.tar.gz"
        if not archive_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Forensic snapshot not found"
            )
        
        # Log deletion event
        await _log_forensic_event(
            db,
            current_user["username"],
            "forensic_snapshot_deleted",
            "forensic_snapshot",
            {"snapshot_id": snapshot_id},
            "warning"
        )
        
        # Delete the archive
        archive_path.unlink()
        
        return {"message": "Forensic snapshot deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting forensic snapshot {snapshot_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete forensic snapshot"
        )

async def _log_forensic_event(
    db: Session, 
    actor: str, 
    action: str, 
    target: str, 
    details: Dict[str, Any], 
    severity: str = "info"
):
    """Log forensic event to audit trail."""
    try:
        audit_log = AuditLog(
            category="forensic",
            actor=actor,
            action=action,
            target=target,
            details=details,
            severity=severity,
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log forensic event: {e}") 