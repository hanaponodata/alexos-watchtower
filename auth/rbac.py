"""
auth/rbac.py
Role-based access control (RBAC) for Watchtower.
Defines roles, permissions, and role assignment/validation for users, agents, and services.
"""

from typing import Dict, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Define possible roles
ROLES = [
    "admin",        # Full system access, upgrade approval, all ops
    "operator",     # Dashboard, system, agent, event mgmt, no protocol approval
    "agent",        # Registered agent, can log events, self-audit, query own logs
    "viewer",       # Read-only access to dashboard and logs
    "compliance",   # Export, audit, reporting rights only
]

# Permissions mapping
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "admin": ["*"],
    "operator": [
        "dashboard:view", "agents:manage", "events:ingest", "events:query",
        "logs:view", "logs:export", "selfaudit:run", "upgrade:propose"
    ],
    "agent": [
        "events:ingest", "selfaudit:run", "logs:view:own", "feedback:submit"
    ],
    "viewer": [
        "dashboard:view", "agents:list", "events:query", "logs:view"
    ],
    "compliance": [
        "logs:view", "logs:export", "selfaudit:report", "compliance:export"
    ],
}

# Security scheme for API authentication
security = HTTPBearer(auto_error=False)

class User:
    """Simple User model for authentication."""
    def __init__(self, user_id: str, role: str = "viewer"):
        self.user_id = user_id
        self.role = role

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """
    Get current user from authentication token.
    For now, returns a default user for development.
    """
    # TODO: Implement proper JWT token validation
    # For development, return a default admin user
    if credentials:
        # In a real implementation, you would validate the JWT token here
        # and extract user information from it
        return User(user_id="admin", role="admin")
    else:
        # For development, allow unauthenticated access with viewer role
        return User(user_id="anonymous", role="viewer")

class RoleManager:
    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS

    def has_permission(self, role: str, permission: str) -> bool:
        perms = self.role_permissions.get(role, [])
        return "*" in perms or permission in perms

    def get_permissions(self, role: str) -> List[str]:
        return self.role_permissions.get(role, [])

    def is_valid_role(self, role: str) -> bool:
        return role in ROLES

    def assign_role(self, user_or_agent, role: str) -> bool:
        """Assign a role to a user or agent (expects .role attribute)."""
        if self.is_valid_role(role):
            user_or_agent.role = role
            return True
        return False

if __name__ == "__main__":
    mgr = RoleManager()
    for role in ROLES:
        print(f"Role: {role}, Perms: {mgr.get_permissions(role)}")
