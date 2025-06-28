"""
auth/session_fusion.py
Enhanced session and context fusion system for Watchtower.
Implements cryptographic tracking, context inheritance, chain-of-custody, and cross-session queries.
"""

import hashlib
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from database.models.events import Event
from database.models.ledger import LedgerEntry

@dataclass
class SessionContext:
    """Represents a session context with full lineage tracking."""
    session_id: str
    parent_session_id: Optional[str]
    user_id: str
    role: str
    context_hash: str
    metadata: Dict[str, Any]
    created_at: datetime
    expires_at: datetime
    is_active: bool = True
    chain_of_custody: List[str] = None
    inherited_contexts: Set[str] = None

    def __post_init__(self):
        if self.chain_of_custody is None:
            self.chain_of_custody = []
        if self.inherited_contexts is None:
            self.inherited_contexts = set()

class SessionFusionManager:
    """Manages session fusion, context inheritance, and chain-of-custody tracking."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.active_sessions: Dict[str, SessionContext] = {}
        self.context_registry: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, user_id: str, role: str, parent_session_id: Optional[str] = None, 
                      metadata: Optional[Dict[str, Any]] = None) -> SessionContext:
        """Create a new session with optional context inheritance."""
        
        session_id = secrets.token_urlsafe(32)
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=24)
        
        # Inherit context from parent session if specified
        inherited_contexts = set()
        chain_of_custody = []
        
        if parent_session_id and parent_session_id in self.active_sessions:
            parent = self.active_sessions[parent_session_id]
            inherited_contexts = parent.inherited_contexts.copy()
            inherited_contexts.add(parent_session_id)
            chain_of_custody = parent.chain_of_custody.copy()
            chain_of_custody.append(parent_session_id)
        
        # Compute context hash
        context_data = {
            "user_id": user_id,
            "role": role,
            "parent_session_id": parent_session_id,
            "inherited_contexts": list(inherited_contexts),
            "metadata": metadata or {},
            "created_at": now.isoformat()
        }
        context_hash = self._compute_context_hash(context_data)
        
        session = SessionContext(
            session_id=session_id,
            parent_session_id=parent_session_id,
            user_id=user_id,
            role=role,
            context_hash=context_hash,
            metadata=metadata or {},
            created_at=now,
            expires_at=expires_at,
            chain_of_custody=chain_of_custody,
            inherited_contexts=inherited_contexts
        )
        
        self.active_sessions[session_id] = session
        self.context_registry[context_hash] = context_data
        
        # Log session creation
        self._log_session_event(session, "session_created", {
            "parent_session_id": parent_session_id,
            "inherited_contexts": list(inherited_contexts),
            "chain_of_custody": chain_of_custody
        })
        
        return session
    
    def merge_sessions(self, session_ids: List[str], merge_metadata: Optional[Dict[str, Any]] = None) -> SessionContext:
        """Merge multiple sessions into a new fused session."""
        
        if len(session_ids) < 2:
            raise ValueError("At least 2 sessions required for fusion")
        
        # Validate all sessions exist and are active
        sessions = []
        for session_id in session_ids:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            session = self.active_sessions[session_id]
            if not session.is_active:
                raise ValueError(f"Session {session_id} is not active")
            sessions.append(session)
        
        # Create merged session
        merged_user_id = sessions[0].user_id  # Use first session's user
        merged_role = sessions[0].role  # Use first session's role
        
        # Combine inherited contexts and chain of custody
        all_inherited = set()
        all_chain = []
        for session in sessions:
            all_inherited.update(session.inherited_contexts)
            all_inherited.add(session.session_id)
            all_chain.extend(session.chain_of_custody)
            all_chain.append(session.session_id)
        
        # Remove duplicates while preserving order
        unique_chain = []
        seen = set()
        for item in all_chain:
            if item not in seen:
                unique_chain.append(item)
                seen.add(item)
        
        merged_metadata = merge_metadata or {}
        merged_metadata["fused_from"] = session_ids
        merged_metadata["fusion_timestamp"] = datetime.utcnow().isoformat()
        
        merged_session = self.create_session(
            user_id=merged_user_id,
            role=merged_role,
            metadata=merged_metadata
        )
        
        # Update inherited contexts and chain of custody
        merged_session.inherited_contexts.update(all_inherited)
        merged_session.chain_of_custody.extend(unique_chain)
        
        # Log fusion event
        self._log_session_event(merged_session, "session_fused", {
            "fused_sessions": session_ids,
            "inherited_contexts": list(all_inherited),
            "chain_of_custody": unique_chain
        })
        
        return merged_session
    
    def rescue_session(self, session_id: str, rescue_context: Dict[str, Any]) -> SessionContext:
        """Rescue a session with new context data."""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        original_session = self.active_sessions[session_id]
        
        # Create rescue session
        rescue_metadata = {
            "rescue_from": session_id,
            "rescue_context": rescue_context,
            "rescue_timestamp": datetime.utcnow().isoformat()
        }
        
        rescue_session = self.create_session(
            user_id=original_session.user_id,
            role=original_session.role,
            parent_session_id=session_id,
            metadata=rescue_metadata
        )
        
        # Log rescue event
        self._log_session_event(rescue_session, "session_rescued", {
            "original_session_id": session_id,
            "rescue_context": rescue_context
        })
        
        return rescue_session
    
    def query_cross_sessions(self, query_context: Dict[str, Any]) -> List[SessionContext]:
        """Query sessions across the entire session graph."""
        
        matching_sessions = []
        
        for session in self.active_sessions.values():
            if not session.is_active:
                continue
            
            # Check if session matches query criteria
            if self._matches_query(session, query_context):
                matching_sessions.append(session)
        
        return matching_sessions
    
    def get_session_lineage(self, session_id: str, depth: int = 3) -> Dict[str, Any]:
        """Get the lineage tree for a session up to specified depth."""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        lineage = {
            "session_id": session_id,
            "context_hash": session.context_hash,
            "chain_of_custody": session.chain_of_custody,
            "inherited_contexts": list(session.inherited_contexts),
            "children": [],
            "depth": 0
        }
        
        # Find child sessions
        children = [s for s in self.active_sessions.values() 
                   if s.parent_session_id == session_id and s.is_active]
        
        if depth > 0:
            for child in children:
                child_lineage = self.get_session_lineage(child.session_id, depth - 1)
                child_lineage["depth"] = lineage["depth"] + 1
                lineage["children"].append(child_lineage)
        
        return lineage
    
    def _compute_context_hash(self, context_data: Dict[str, Any]) -> str:
        """Compute cryptographic hash of context data."""
        context_str = json.dumps(context_data, sort_keys=True, default=str)
        return hashlib.sha256(context_str.encode()).hexdigest()
    
    def _matches_query(self, session: SessionContext, query_context: Dict[str, Any]) -> bool:
        """Check if session matches query criteria."""
        
        for key, value in query_context.items():
            if key == "user_id" and session.user_id != value:
                return False
            elif key == "role" and session.role != value:
                return False
            elif key == "context_hash" and session.context_hash != value:
                return False
            elif key in session.metadata and session.metadata[key] != value:
                return False
        
        return True
    
    def _log_session_event(self, session: SessionContext, event_type: str, details: Dict[str, Any]):
        """Log session events to the audit trail."""
        
        event_data = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "role": session.role,
            "context_hash": session.context_hash,
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Create ledger entry
        ledger_entry = LedgerEntry(
            entry_type="session_event",
            reference_id=session.session_id,
            data=event_data,
            node_id="session_fusion_manager",
            timestamp=datetime.utcnow()
        )
        
        self.db_session.add(ledger_entry)
        
        # Create event log
        event = Event(
            event_type=event_type,
            severity="info",
            payload=event_data
        )
        
        self.db_session.add(event)
        self.db_session.commit()
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        now = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if now > session.expires_at:
                expired_sessions.append(session_id)
                session.is_active = False
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        return len(expired_sessions) 