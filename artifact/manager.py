"""
artifact/manager.py
Enterprise-grade artifact manager for Watchtower.
Handles storage, registration, metadata, and access for knowledge packs and plugin artifacts.
"""

from typing import Dict, Any, List, Optional
from database.models.artifact import Artifact
from sqlalchemy.orm import Session
from datetime import datetime

class ArtifactManager:
    def __init__(self, session: Session):
        self.session = session

    def register_artifact(self, artifact_id: str, name: str, type: str, owner: str, metadata: Optional[Dict[str, Any]] = None, description: str = "") -> Artifact:
        artifact = Artifact(
            artifact_id=artifact_id,
            name=name,
            type=type,
            owner=owner,
            metadata=metadata or {},
            description=description,
            created_at=datetime.utcnow(),
        )
        self.session.add(artifact)
        self.session.commit()
        return artifact

    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        return self.session.query(Artifact).filter_by(artifact_id=artifact_id).first()

    def list_artifacts(self, owner: Optional[str] = None, type: Optional[str] = None) -> List[Artifact]:
        query = self.session.query(Artifact)
        if owner:
            query = query.filter_by(owner=owner)
        if type:
            query = query.filter_by(type=type)
        return query.all()

    def archive_artifact(self, artifact_id: str) -> bool:
        artifact = self.get_artifact(artifact_id)
        if artifact:
            artifact.archived = True
            self.session.commit()
            return True
        return False

if __name__ == "__main__":
    print("ArtifactManager requires an active SQLAlchemy session.")
