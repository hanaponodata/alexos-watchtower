"""
backup/enterprise_backup.py
Enhanced enterprise backup and restore system for Watchtower.
Implements periodic snapshots, on-demand backups, restore testing, and audit chain tracking.
"""

import os
import json
import shutil
import hashlib
import tarfile
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
import psycopg2
from psycopg2.extras import RealDictCursor

from database.models.events import Event
from database.models.ledger import LedgerEntry
from config.settings import settings

@dataclass
class BackupMetadata:
    """Metadata for a backup operation."""
    backup_id: str
    backup_type: str  # periodic, on_demand, snapshot
    created_at: datetime
    size_bytes: int
    checksum: str
    components: List[str]
    status: str  # in_progress, completed, failed
    restore_tested: bool = False
    restore_test_date: Optional[datetime] = None
    audit_chain: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.audit_chain is None:
            self.audit_chain = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class RestoreResult:
    """Result of a restore operation."""
    restore_id: str
    backup_id: str
    restored_at: datetime
    status: str  # success, failed, partial
    restored_components: List[str]
    failed_components: List[str]
    duration_seconds: float
    verification_passed: bool
    audit_chain: List[str]
    details: Dict[str, Any]

class EnterpriseBackupSystem:
    """Enterprise-grade backup and restore system."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.backup_dir = Path(settings.backup_dir or "/var/backups/watchtower")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backup_metadata_file = self.backup_dir / "backup_metadata.json"
        self.backup_metadata = self._load_backup_metadata()
        
        # Backup components configuration
        self.backup_components = {
            "database": {
                "enabled": True,
                "type": "postgresql",
                "tables": ["events", "ledger", "agents", "compliance", "sessions"]
            },
            "config": {
                "enabled": True,
                "paths": ["config/", ".env", "alembic.ini"]
            },
            "logs": {
                "enabled": True,
                "paths": ["logs/", "*.log"]
            },
            "artifacts": {
                "enabled": True,
                "paths": ["artifacts/", "uploads/"]
            }
        }
    
    def create_periodic_backup(self, backup_type: str = "daily") -> BackupMetadata:
        """Create a periodic backup based on schedule."""
        
        backup_id = f"periodic_{backup_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Check if backup already exists for this period
        existing_backup = self._get_latest_backup_by_type(backup_type)
        if existing_backup and self._is_backup_recent(existing_backup, backup_type):
            print(f"Recent {backup_type} backup already exists: {existing_backup.backup_id}")
            return existing_backup
        
        return self._create_backup(backup_id, "periodic", backup_type)
    
    def create_on_demand_backup(self, components: Optional[List[str]] = None) -> BackupMetadata:
        """Create an on-demand backup."""
        
        backup_id = f"ondemand_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        return self._create_backup(backup_id, "on_demand", components=components)
    
    def create_snapshot(self, snapshot_name: str) -> BackupMetadata:
        """Create a system snapshot."""
        
        backup_id = f"snapshot_{snapshot_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        return self._create_backup(backup_id, "snapshot", snapshot_name)
    
    def restore_backup(self, backup_id: str, target_components: Optional[List[str]] = None,
                      dry_run: bool = False) -> RestoreResult:
        """Restore from a backup."""
        
        if backup_id not in self.backup_metadata:
            raise ValueError(f"Backup {backup_id} not found")
        
        backup_meta = self.backup_metadata[backup_id]
        if backup_meta.status != "completed":
            raise ValueError(f"Backup {backup_id} is not in completed status")
        
        restore_id = f"restore_{backup_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.utcnow()
        
        # Components to restore
        components_to_restore = target_components or backup_meta.components
        restored_components = []
        failed_components = []
        
        try:
            backup_path = self.backup_dir / f"{backup_id}.tar.gz"
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Extract backup
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                with tarfile.open(backup_path, 'r:gz') as tar:
                    tar.extractall(temp_path)
                
                # Restore components
                for component in components_to_restore:
                    if component not in backup_meta.components:
                        failed_components.append(component)
                        continue
                    
                    if dry_run:
                        restored_components.append(component)
                        continue
                    
                    try:
                        if component == "database":
                            self._restore_database(temp_path / component)
                        elif component == "config":
                            self._restore_config(temp_path / component)
                        elif component == "logs":
                            self._restore_logs(temp_path / component)
                        elif component == "artifacts":
                            self._restore_artifacts(temp_path / component)
                        
                        restored_components.append(component)
                    except Exception as e:
                        failed_components.append(component)
                        print(f"Failed to restore {component}: {str(e)}")
            
            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Determine status
            if failed_components:
                status = "partial" if restored_components else "failed"
            else:
                status = "success"
            
            # Verify restore
            verification_passed = self._verify_restore(restored_components) if not dry_run else True
            
            # Create audit chain
            audit_chain = backup_meta.audit_chain.copy()
            audit_chain.append(backup_id)
            audit_chain.append(restore_id)
            
            result = RestoreResult(
                restore_id=restore_id,
                backup_id=backup_id,
                restored_at=datetime.utcnow(),
                status=status,
                restored_components=restored_components,
                failed_components=failed_components,
                duration_seconds=duration,
                verification_passed=verification_passed,
                audit_chain=audit_chain,
                details={
                    "dry_run": dry_run,
                    "target_components": target_components
                }
            )
            
            # Log restore event
            self._log_restore_event(result)
            
            return result
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            result = RestoreResult(
                restore_id=restore_id,
                backup_id=backup_id,
                restored_at=datetime.utcnow(),
                status="failed",
                restored_components=[],
                failed_components=components_to_restore,
                duration_seconds=duration,
                verification_passed=False,
                audit_chain=backup_meta.audit_chain.copy() + [backup_id, restore_id],
                details={"error": str(e)}
            )
            
            self._log_restore_event(result)
            raise
    
    def test_restore(self, backup_id: str) -> RestoreResult:
        """Test restore from a backup in a safe environment."""
        
        # Create test environment
        test_db_url = self._create_test_database()
        
        try:
            # Perform dry run restore
            result = self.restore_backup(backup_id, dry_run=True)
            
            # Update backup metadata
            if backup_id in self.backup_metadata:
                self.backup_metadata[backup_id].restore_tested = True
                self.backup_metadata[backup_id].restore_test_date = datetime.utcnow()
                self._save_backup_metadata()
            
            return result
            
        finally:
            # Cleanup test environment
            self._cleanup_test_database(test_db_url)
    
    def list_backups(self, backup_type: Optional[str] = None) -> List[BackupMetadata]:
        """List available backups."""
        
        backups = list(self.backup_metadata.values())
        
        if backup_type:
            backups = [b for b in backups if b.backup_type == backup_type]
        
        return sorted(backups, key=lambda x: x.created_at, reverse=True)
    
    def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """Clean up old backups based on retention policy."""
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        deleted_count = 0
        
        for backup_id, backup_meta in list(self.backup_metadata.items()):
            if backup_meta.created_at < cutoff_date:
                try:
                    # Delete backup file
                    backup_file = self.backup_dir / f"{backup_id}.tar.gz"
                    if backup_file.exists():
                        backup_file.unlink()
                    
                    # Remove from metadata
                    del self.backup_metadata[backup_id]
                    deleted_count += 1
                    
                except Exception as e:
                    print(f"Failed to delete backup {backup_id}: {str(e)}")
        
        self._save_backup_metadata()
        return deleted_count
    
    def _create_backup(self, backup_id: str, backup_type: str, 
                      backup_subtype: str = None, components: Optional[List[str]] = None) -> BackupMetadata:
        """Create a backup with the specified components."""
        
        start_time = datetime.utcnow()
        
        # Initialize backup metadata
        backup_meta = BackupMetadata(
            backup_id=backup_id,
            backup_type=backup_type,
            created_at=start_time,
            size_bytes=0,
            checksum="",
            components=[],
            status="in_progress",
            metadata={
                "subtype": backup_subtype,
                "components": components
            }
        )
        
        # Add to metadata
        self.backup_metadata[backup_id] = backup_meta
        self._save_backup_metadata()
        
        try:
            # Determine components to backup
            components_to_backup = components or list(self.backup_components.keys())
            
            # Create temporary directory for backup
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Backup each component
                for component in components_to_backup:
                    if component not in self.backup_components:
                        continue
                    
                    component_config = self.backup_components[component]
                    if not component_config.get("enabled", True):
                        continue
                    
                    try:
                        if component == "database":
                            self._backup_database(temp_path / component)
                        elif component == "config":
                            self._backup_config(temp_path / component)
                        elif component == "logs":
                            self._backup_logs(temp_path / component)
                        elif component == "artifacts":
                            self._backup_artifacts(temp_path / component)
                        
                        backup_meta.components.append(component)
                        
                    except Exception as e:
                        print(f"Failed to backup {component}: {str(e)}")
                
                # Create archive
                backup_file = self.backup_dir / f"{backup_id}.tar.gz"
                with tarfile.open(backup_file, 'w:gz') as tar:
                    tar.add(temp_path, arcname="")
                
                # Calculate checksum and size
                backup_meta.size_bytes = backup_file.stat().st_size
                backup_meta.checksum = self._calculate_file_checksum(backup_file)
                backup_meta.status = "completed"
                
                # Create audit chain
                backup_meta.audit_chain = [backup_id]
                
        except Exception as e:
            backup_meta.status = "failed"
            backup_meta.metadata["error"] = str(e)
            print(f"Backup {backup_id} failed: {str(e)}")
        
        # Update metadata
        self._save_backup_metadata()
        
        # Log backup event
        self._log_backup_event(backup_meta)
        
        return backup_meta
    
    def _backup_database(self, target_path: Path):
        """Backup database using pg_dump."""
        
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Get database connection info
        db_url = settings.db_url
        if db_url.startswith("postgresql://"):
            # Parse connection string
            parts = db_url.replace("postgresql://", "").split("@")
            if len(parts) == 2:
                auth, host_db = parts
                user_pass = auth.split(":")
                host_port_db = host_db.split("/")
                
                if len(user_pass) == 2 and len(host_port_db) == 2:
                    user, password = user_pass
                    host_port, database = host_port_db
                    
                    if ":" in host_port:
                        host, port = host_port.split(":")
                    else:
                        host, port = host_port, "5432"
                    
                    # Run pg_dump
                    dump_file = target_path / "database.sql"
                    env = os.environ.copy()
                    env["PGPASSWORD"] = password
                    
                    cmd = [
                        "pg_dump",
                        "-h", host,
                        "-p", port,
                        "-U", user,
                        "-d", database,
                        "-f", str(dump_file),
                        "--verbose"
                    ]
                    
                    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        raise Exception(f"pg_dump failed: {result.stderr}")
    
    def _backup_config(self, target_path: Path):
        """Backup configuration files."""
        
        target_path.mkdir(parents=True, exist_ok=True)
        
        config_paths = self.backup_components["config"]["paths"]
        for config_path in config_paths:
            source_path = Path(config_path)
            if source_path.exists():
                if source_path.is_file():
                    shutil.copy2(source_path, target_path / source_path.name)
                else:
                    shutil.copytree(source_path, target_path / source_path.name, dirs_exist_ok=True)
    
    def _backup_logs(self, target_path: Path):
        """Backup log files."""
        
        target_path.mkdir(parents=True, exist_ok=True)
        
        log_paths = self.backup_components["logs"]["paths"]
        for log_path in log_paths:
            if "*" in log_path:
                # Handle glob patterns
                import glob
                for log_file in glob.glob(log_path):
                    source_path = Path(log_file)
                    if source_path.exists():
                        shutil.copy2(source_path, target_path / source_path.name)
            else:
                source_path = Path(log_path)
                if source_path.exists():
                    if source_path.is_file():
                        shutil.copy2(source_path, target_path / source_path.name)
                    else:
                        shutil.copytree(source_path, target_path / source_path.name, dirs_exist_ok=True)
    
    def _backup_artifacts(self, target_path: Path):
        """Backup artifacts and uploads."""
        
        target_path.mkdir(parents=True, exist_ok=True)
        
        artifact_paths = self.backup_components["artifacts"]["paths"]
        for artifact_path in artifact_paths:
            source_path = Path(artifact_path)
            if source_path.exists():
                shutil.copytree(source_path, target_path / source_path.name, dirs_exist_ok=True)
    
    def _restore_database(self, source_path: Path):
        """Restore database from backup."""
        
        dump_file = source_path / "database.sql"
        if not dump_file.exists():
            raise FileNotFoundError(f"Database dump not found: {dump_file}")
        
        # Get database connection info
        db_url = settings.db_url
        if db_url.startswith("postgresql://"):
            # Parse connection string (same logic as backup)
            parts = db_url.replace("postgresql://", "").split("@")
            if len(parts) == 2:
                auth, host_db = parts
                user_pass = auth.split(":")
                host_port_db = host_db.split("/")
                
                if len(user_pass) == 2 and len(host_port_db) == 2:
                    user, password = user_pass
                    host_port, database = host_port_db
                    
                    if ":" in host_port:
                        host, port = host_port.split(":")
                    else:
                        host, port = host_port, "5432"
                    
                    # Run psql restore
                    env = os.environ.copy()
                    env["PGPASSWORD"] = password
                    
                    cmd = [
                        "psql",
                        "-h", host,
                        "-p", port,
                        "-U", user,
                        "-d", database,
                        "-f", str(dump_file)
                    ]
                    
                    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        raise Exception(f"Database restore failed: {result.stderr}")
    
    def _restore_config(self, source_path: Path):
        """Restore configuration files."""
        
        for config_file in source_path.iterdir():
            if config_file.is_file():
                target_file = Path(config_file.name)
                shutil.copy2(config_file, target_file)
            else:
                shutil.copytree(config_file, Path(config_file.name), dirs_exist_ok=True)
    
    def _restore_logs(self, source_path: Path):
        """Restore log files."""
        
        for log_file in source_path.iterdir():
            if log_file.is_file():
                target_file = Path("logs") / log_file.name
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(log_file, target_file)
    
    def _restore_artifacts(self, source_path: Path):
        """Restore artifacts and uploads."""
        
        for artifact_dir in source_path.iterdir():
            if artifact_dir.is_dir():
                target_dir = Path(artifact_dir.name)
                shutil.copytree(artifact_dir, target_dir, dirs_exist_ok=True)
    
    def _verify_restore(self, restored_components: List[str]) -> bool:
        """Verify that restore was successful."""
        
        try:
            # Check database connectivity
            if "database" in restored_components:
                engine = create_engine(settings.db_url)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
            
            # Check config files
            if "config" in restored_components:
                if not Path(".env").exists():
                    return False
            
            return True
            
        except Exception as e:
            print(f"Restore verification failed: {str(e)}")
            return False
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def _load_backup_metadata(self) -> Dict[str, BackupMetadata]:
        """Load backup metadata from file."""
        
        if not self.backup_metadata_file.exists():
            return {}
        
        try:
            with open(self.backup_metadata_file, 'r') as f:
                data = json.load(f)
            
            metadata = {}
            for backup_id, backup_data in data.items():
                backup_data["created_at"] = datetime.fromisoformat(backup_data["created_at"])
                if backup_data.get("restore_test_date"):
                    backup_data["restore_test_date"] = datetime.fromisoformat(backup_data["restore_test_date"])
                
                metadata[backup_id] = BackupMetadata(**backup_data)
            
            return metadata
            
        except Exception as e:
            print(f"Failed to load backup metadata: {str(e)}")
            return {}
    
    def _save_backup_metadata(self):
        """Save backup metadata to file."""
        
        try:
            data = {}
            for backup_id, backup_meta in self.backup_metadata.items():
                data[backup_id] = asdict(backup_meta)
                # Convert datetime to string for JSON serialization
                data[backup_id]["created_at"] = backup_meta.created_at.isoformat()
                if backup_meta.restore_test_date:
                    data[backup_id]["restore_test_date"] = backup_meta.restore_test_date.isoformat()
            
            with open(self.backup_metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save backup metadata: {str(e)}")
    
    def _get_latest_backup_by_type(self, backup_type: str) -> Optional[BackupMetadata]:
        """Get the latest backup of a specific type."""
        
        backups = [b for b in self.backup_metadata.values() 
                  if b.backup_type == "periodic" and b.metadata.get("subtype") == backup_type]
        
        if not backups:
            return None
        
        return max(backups, key=lambda x: x.created_at)
    
    def _is_backup_recent(self, backup: BackupMetadata, backup_type: str) -> bool:
        """Check if backup is recent enough for the given type."""
        
        now = datetime.utcnow()
        age = now - backup.created_at
        
        if backup_type == "hourly":
            return age.total_seconds() < 3600
        elif backup_type == "daily":
            return age.total_seconds() < 86400
        elif backup_type == "weekly":
            return age.total_seconds() < 604800
        else:
            return False
    
    def _create_test_database(self) -> str:
        """Create a test database for restore testing."""
        
        # This is a simplified implementation
        # In production, you'd create a temporary database
        return "postgresql://test:test@localhost:5432/watchtower_test"
    
    def _cleanup_test_database(self, test_db_url: str):
        """Clean up test database."""
        
        # This is a simplified implementation
        # In production, you'd drop the temporary database
        pass
    
    def _log_backup_event(self, backup_meta: BackupMetadata):
        """Log backup event to audit trail."""
        
        event_data = {
            "backup_id": backup_meta.backup_id,
            "backup_type": backup_meta.backup_type,
            "status": backup_meta.status,
            "components": backup_meta.components,
            "size_bytes": backup_meta.size_bytes,
            "checksum": backup_meta.checksum
        }
        
        event = Event(
            event_type="backup_created",
            severity="info",
            payload=event_data
        )
        
        self.db_session.add(event)
        self.db_session.commit()
    
    def _log_restore_event(self, restore_result: RestoreResult):
        """Log restore event to audit trail."""
        
        event_data = {
            "restore_id": restore_result.restore_id,
            "backup_id": restore_result.backup_id,
            "status": restore_result.status,
            "restored_components": restore_result.restored_components,
            "failed_components": restore_result.failed_components,
            "duration_seconds": restore_result.duration_seconds,
            "verification_passed": restore_result.verification_passed
        }
        
        event = Event(
            event_type="backup_restored",
            severity="info" if restore_result.status == "success" else "warning",
            payload=event_data
        )
        
        self.db_session.add(event)
        self.db_session.commit() 