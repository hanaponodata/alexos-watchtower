"""
database/engine.py
Postgres SQLAlchemy engine, session, and database utilities for Watchtower.
Supports connection pooling, echo, timeout, and dynamic config.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from config.settings import settings

DATABASE_URL = settings.db_url
POOL_SIZE = settings.db_pool_size
TIMEOUT = settings.db_timeout
ECHO = settings.db_echo

# Engine creation with connection pooling
def get_engine(url: str = DATABASE_URL, pool_size: int = POOL_SIZE, timeout: int = TIMEOUT, echo: bool = ECHO):
    return create_engine(
        url,
        pool_size=pool_size,
        pool_timeout=timeout,
        echo=echo,
        pool_pre_ping=True,
        pool_recycle=1800,
        poolclass=NullPool if pool_size == 0 else None
    )

engine = get_engine()

# SessionLocal: for use in async/background tasks
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_session():
    """Yield a new database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# For Alembic and migrations
def get_engine_for_migrations():
    """Returns an engine for use in migration scripts (usually with env var override)."""
    return get_engine()

if __name__ == "__main__":
    print(f"Engine created: {engine}")
    # Try connecting to verify DB
    try:
        conn = engine.connect()
        print("Database connection successful.")
        conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")
