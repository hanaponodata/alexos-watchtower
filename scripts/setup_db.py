#!/usr/bin/env python3
"""
Database setup script for Watchtower.
Creates database tables and initializes the schema.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from database.engine import get_engine_for_migrations
from database.models.base import Base
from database.models.agents import Agent
from database.models.events import Event
from database.models.audit import AuditLog
from database.models.ledger import LedgerEntry
from database.models.artifact import Artifact
from database.models.feedback import Feedback
from database.models.token import Token
from database.models.upgrade import UpgradeProposal
from database.models.lineage import LineageNode
from config import settings, logger

def create_tables():
    """Create all database tables."""
    try:
        engine = get_engine_for_migrations()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Verify tables were created
        with engine.connect() as conn:
            if "sqlite" in str(engine.url):
                # SQLite doesn't have information_schema
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            else:
                # PostgreSQL/MySQL use information_schema
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """))
            tables = [row[0] for row in result]
            logger.info(f"Created tables: {', '.join(tables)}")
            
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False

def check_database_connection():
    """Check if database connection is working."""
    try:
        engine = get_engine_for_migrations()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def create_initial_data():
    """Create initial data for development/testing."""
    try:
        from sqlalchemy.orm import sessionmaker
        engine = get_engine_for_migrations()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            # Create a sample agent
            sample_agent = Agent(
                uuid="sample-agent-001",
                name="Sample Agent",
                agent_type="monitoring",
                owner="System",
                description="Sample agent for testing",
                status="online",
                score=95
            )
            db.add(sample_agent)
            
            # Create a sample event
            sample_event = Event(
                event_type="system_startup",
                severity="info",
                payload={"message": "System initialized successfully"},
                source="database_setup"
            )
            db.add(sample_event)
            
            db.commit()
            logger.info("Initial data created successfully")
            return True
    except Exception as e:
        logger.error(f"Failed to create initial data: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Watchtower Database Setup")
    print("=" * 40)
    
    # Check database connection
    print("1. Checking database connection...")
    if not check_database_connection():
        print("❌ Database connection failed. Please check your configuration.")
        sys.exit(1)
    print("✅ Database connection successful")
    
    # Create tables
    print("2. Creating database tables...")
    if not create_tables():
        print("❌ Failed to create tables.")
        sys.exit(1)
    print("✅ Database tables created")
    
    # Create initial data (optional)
    if settings.env == "development":
        print("3. Creating initial data...")
        if create_initial_data():
            print("✅ Initial data created")
        else:
            print("⚠️  Failed to create initial data (continuing anyway)")
    
    print("=" * 40)
    print("✅ Database setup completed successfully!")
    print(f"Database URL: {settings.db_url}")
    print(f"Environment: {settings.env}")

if __name__ == "__main__":
    main()
