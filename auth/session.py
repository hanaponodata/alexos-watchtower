"""
auth/session.py
Session and identity management for Watchtower.
Supports login, session tokens, agent/user context, and escrow/multi-party sessions.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict

class SessionManager:
    def __init__(self, timeout_minutes: int = 60):
        self.sessions: Dict[str, Dict] = {}
        self.timeout = timedelta(minutes=timeout_minutes)

    def create_session(self, user_id: str, role: str) -> str:
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            "user_id": user_id,
            "role": role,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + self.timeout,
            "active": True
        }
        return session_id

    def validate_session(self, session_id: str) -> Optional[Dict]:
        session = self.sessions.get(session_id)
        if not session:
            return None
        if datetime.utcnow() > session["expires_at"] or not session["active"]:
            session["active"] = False
            return None
        return session

    def revoke_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id]["active"] = False

    def get_user_role(self, session_id: str) -> Optional[str]:
        session = self.validate_session(session_id)
        if session:
            return session.get("role")
        return None

    def get_user_id(self, session_id: str) -> Optional[str]:
        session = self.validate_session(session_id)
        if session:
            return session.get("user_id")
        return None

    def cleanup_expired(self):
        now = datetime.utcnow()
        expired = [sid for sid, s in self.sessions.items() if now > s["expires_at"] or not s["active"]]
        for sid in expired:
            del self.sessions[sid]

if __name__ == "__main__":
    mgr = SessionManager()
    sid = mgr.create_session("user123", "admin")
    print("Session ID:", sid)
    print("Validate:", mgr.validate_session(sid))
    print("User Role:", mgr.get_user_role(sid))
    mgr.revoke_session(sid)
    print("Validate after revoke:", mgr.validate_session(sid))
