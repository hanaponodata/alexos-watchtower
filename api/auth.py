"""
api/auth.py
Authentication API for Watchtower with user management, session handling, and audit logging.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from database.engine import get_session
from database.models.audit import AuditLog
from config import settings, logger
from datetime import datetime, timedelta
import hashlib
import hmac
import secrets
import json

router = APIRouter(tags=["authentication"])
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    created_at: datetime
    last_login: Optional[datetime]

class TokenValidation(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None

# In-memory user store (replace with database in production)
USERS = {
    "admin": {
        "id": "admin-001",
        "username": "admin",
        "email": "admin@watchtower.local",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "created_at": datetime.utcnow(),
        "last_login": None
    }
}

# In-memory session store (replace with Redis/database in production)
SESSIONS = {}

def _hash_password(password: str) -> str:
    """Hash password using SHA-256 (use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()

def _verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hmac.compare_digest(_hash_password(password), hashed)

def _generate_token(user_id: str, username: str, role: str) -> str:
    """Generate authentication token."""
    timestamp = datetime.utcnow().isoformat()
    payload = f"{user_id}|{username}|{role}|{timestamp}"
    
    # Create signature
    admin_key = settings.admin_key if settings.admin_key else "default"
    logger.info(f"Token generation: admin_key='{admin_key}', payload='{payload}'")
    
    signature = hmac.new(
        admin_key.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    logger.info(f"Token generation: signature='{signature}'")
    
    return f"{payload}|{signature}"

def _validate_token(token: str) -> Optional[Dict[str, Any]]:
    """Validate authentication token."""
    try:
        parts = token.split("|")
        if len(parts) != 5:
            logger.error(f"Token validation failed: wrong number of parts ({len(parts)})")
            return None
            
        user_id, username, role, timestamp, signature = parts
        
        # Check expiration (24 hours)
        token_time = datetime.fromisoformat(timestamp)
        if datetime.utcnow() - token_time > timedelta(hours=24):
            logger.error(f"Token validation failed: token expired")
            return None
        
        # Verify signature
        payload = f"{user_id}|{username}|{role}|{timestamp}"
        admin_key = settings.admin_key if settings.admin_key else "default"
        logger.info(f"Token validation: admin_key='{admin_key}', payload='{payload}'")
        
        expected_signature = hmac.new(
            admin_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        logger.info(f"Token validation: expected_signature='{expected_signature}', received_signature='{signature}'")
        
        if hmac.compare_digest(signature, expected_signature):
            return {
                "user_id": user_id,
                "username": username,
                "role": role,
                "timestamp": timestamp
            }
        
        logger.error(f"Token validation failed: signature mismatch")
        return None
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return None

async def _log_audit_event(
    db: Session, 
    actor: str, 
    action: str, 
    target: str, 
    details: Dict[str, Any], 
    severity: str = "info"
):
    """Log audit event to database."""
    try:
        audit_log = AuditLog(
            category="authentication",
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
        logger.error(f"Failed to log audit event: {e}")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Get current authenticated user from token."""
    token = credentials.credentials
    user_info = _validate_token(token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user exists
    user = USERS.get(user_info["username"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_session)
):
    """Authenticate user and return access token."""
    try:
        # Check if user exists
        user = USERS.get(login_data.username)
        if not user:
            await _log_audit_event(
                db, 
                login_data.username, 
                "login_failed", 
                "authentication", 
                {"reason": "user_not_found", "ip": request.client.host if request.client else "unknown"},
                "warning"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not _verify_password(login_data.password, user["password_hash"]):
            await _log_audit_event(
                db, 
                login_data.username, 
                "login_failed", 
                "authentication", 
                {"reason": "invalid_password", "ip": request.client.host if request.client else "unknown"},
                "warning"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Generate token
        token = _generate_token(user["id"], user["username"], user["role"])
        
        # Update last login
        user["last_login"] = datetime.utcnow()
        
        # Store session
        SESSIONS[token] = {
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        # Log successful login
        await _log_audit_event(
            db, 
            user["username"], 
            "login_success", 
            "authentication", 
            {"ip": request.client.host if request.client else "unknown", "user_agent": request.headers.get("user-agent")},
            "info"
        )
        
        return LoginResponse(
            access_token=token,
            expires_in=86400,  # 24 hours
            user_id=user["id"],
            username=user["username"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout")
async def logout(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Logout user and invalidate session."""
    try:
        # Get token from request
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if token in SESSIONS:
                del SESSIONS[token]
        
        # Log logout
        await _log_audit_event(
            db, 
            current_user["username"], 
            "logout", 
            "authentication", 
            {"ip": request.client.host if request.client else "unknown"},
            "info"
        )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current user information."""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        role=current_user["role"],
        created_at=current_user["created_at"],
        last_login=current_user["last_login"]
    )

@router.post("/validate", response_model=TokenValidation)
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Validate authentication token."""
    token = credentials.credentials
    user_info = _validate_token(token)
    
    if user_info:
        return TokenValidation(
            valid=True,
            user_id=user_info["user_id"],
            username=user_info["username"],
            role=user_info["role"]
        )
    else:
        return TokenValidation(valid=False)

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Create new user (admin only)."""
    # Check if current user is admin
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Check if username already exists
    if user_data.username in USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create user
    user_id = f"user-{secrets.token_hex(8)}"
    new_user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": _hash_password(user_data.password),
        "role": user_data.role,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    USERS[user_data.username] = new_user
    
    # Log user creation
    await _log_audit_event(
        db, 
        current_user["username"], 
        "user_created", 
        user_data.username, 
        {"role": user_data.role, "email": user_data.email},
        "info"
    )
    
    return UserResponse(
        id=new_user["id"],
        username=new_user["username"],
        email=new_user["email"],
        role=new_user["role"],
        created_at=new_user["created_at"],
        last_login=new_user["last_login"]
    )

@router.get("/sessions")
async def get_active_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get active sessions (admin only)."""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return {
        "active_sessions": len(SESSIONS),
        "sessions": [
            {
                "username": session["username"],
                "role": session["role"],
                "created_at": session["created_at"],
                "last_activity": session["last_activity"]
            }
            for session in SESSIONS.values()
        ]
    } 