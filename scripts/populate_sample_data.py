#!/usr/bin/env python3
"""
Sample data population script for Watchtower.
Adds sample agents and events for testing and demonstration.
"""

import os
import sys
from pathlib import Path
import uuid
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import sessionmaker
from database.engine import get_engine_for_migrations
from database.models.agents import Agent
from database.models.events import Event
from config import settings, logger

def create_sample_agents(db):
    """Create sample agents."""
    sample_agents = [
        {
            "uuid": "primary-node-001",
            "name": "Primary Node",
            "agent_type": "system",
            "owner": "System",
            "description": "Main system monitoring node",
            "status": "online",
            "score": 95
        },
        {
            "uuid": "backup-node-002", 
            "name": "Backup Node",
            "agent_type": "backup",
            "owner": "System",
            "description": "Backup and redundancy node",
            "status": "online",
            "score": 88
        },
        {
            "uuid": "monitoring-agent-003",
            "name": "Monitoring Agent",
            "agent_type": "monitoring",
            "owner": "Admin",
            "description": "System monitoring and alerting agent",
            "status": "degraded",
            "score": 72
        },
        {
            "uuid": "security-agent-004",
            "name": "Security Agent",
            "agent_type": "security",
            "owner": "Security Team",
            "description": "Security monitoring and threat detection",
            "status": "online",
            "score": 91
        },
        {
            "uuid": "compliance-agent-005",
            "name": "Compliance Agent",
            "agent_type": "compliance",
            "owner": "Compliance Team",
            "description": "Compliance monitoring and reporting",
            "status": "online",
            "score": 89
        }
    ]
    
    for agent_data in sample_agents:
        # Check if agent already exists
        existing = db.query(Agent).filter(Agent.uuid == agent_data["uuid"]).first()
        if not existing:
            agent = Agent(**agent_data)
            db.add(agent)
            logger.info(f"Created agent: {agent_data['name']}")
        else:
            logger.info(f"Agent already exists: {agent_data['name']}")
    
    db.commit()

def create_sample_events(db):
    """Create sample events."""
    # Get agent UUIDs for reference
    agents = db.query(Agent).all()
    agent_uuids = [agent.uuid for agent in agents]
    
    sample_events = [
        {
            "event_type": "system_startup",
            "agent_uuid": agent_uuids[0] if agent_uuids else None,
            "severity": "info",
            "payload": {"message": "System initialized successfully", "version": "1.0.0"},
            "source": "system"
        },
        {
            "event_type": "agent_registered",
            "agent_uuid": agent_uuids[1] if len(agent_uuids) > 1 else None,
            "severity": "info",
            "payload": {"message": "New agent registered", "agent_name": "Backup Node"},
            "source": "registry"
        },
        {
            "event_type": "security_scan",
            "agent_uuid": agent_uuids[3] if len(agent_uuids) > 3 else None,
            "severity": "info",
            "payload": {"message": "Security scan completed", "threats_found": 0},
            "source": "security"
        },
        {
            "event_type": "high_cpu_usage",
            "agent_uuid": agent_uuids[2] if len(agent_uuids) > 2 else None,
            "severity": "warning",
            "payload": {"message": "High CPU usage detected", "cpu_percent": 85},
            "source": "monitoring"
        },
        {
            "event_type": "backup_completed",
            "agent_uuid": agent_uuids[1] if len(agent_uuids) > 1 else None,
            "severity": "info",
            "payload": {"message": "System backup completed successfully", "size_mb": 1024},
            "source": "backup"
        },
        {
            "event_type": "compliance_check",
            "agent_uuid": agent_uuids[4] if len(agent_uuids) > 4 else None,
            "severity": "info",
            "payload": {"message": "Compliance check passed", "score": 95},
            "source": "compliance"
        },
        {
            "event_type": "network_latency",
            "agent_uuid": agent_uuids[0] if agent_uuids else None,
            "severity": "warning",
            "payload": {"message": "Increased network latency detected", "latency_ms": 150},
            "source": "network"
        },
        {
            "event_type": "disk_space_low",
            "agent_uuid": agent_uuids[2] if len(agent_uuids) > 2 else None,
            "severity": "error",
            "payload": {"message": "Disk space running low", "free_space_gb": 2.5},
            "source": "monitoring"
        },
        {
            "event_type": "user_login",
            "agent_uuid": None,
            "severity": "info",
            "payload": {"message": "User login successful", "user": "admin"},
            "source": "auth"
        },
        {
            "event_type": "system_update",
            "agent_uuid": agent_uuids[0] if agent_uuids else None,
            "severity": "info",
            "payload": {"message": "System update completed", "version": "1.0.1"},
            "source": "system"
        }
    ]
    
    # Create events with different timestamps
    for i, event_data in enumerate(sample_events):
        # Spread events over the last 24 hours
        timestamp = datetime.utcnow() - timedelta(hours=24-i*2.4)
        event = Event(
            **event_data,
            timestamp=timestamp
        )
        db.add(event)
        logger.info(f"Created event: {event_data['event_type']}")
    
    db.commit()

def main():
    """Main function to populate sample data."""
    print("🚀 Watchtower Sample Data Population")
    print("=" * 40)
    
    try:
        # Create database session
        engine = get_engine_for_migrations()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            print("1. Creating sample agents...")
            create_sample_agents(db)
            print("✅ Sample agents created")
            
            print("2. Creating sample events...")
            create_sample_events(db)
            print("✅ Sample events created")
            
            # Show summary
            agent_count = db.query(Agent).count()
            event_count = db.query(Event).count()
            
            print("=" * 40)
            print("✅ Sample data population completed!")
            print(f"Agents created: {agent_count}")
            print(f"Events created: {event_count}")
            print("\nYou can now access the dashboard to see the data.")
            
    except Exception as e:
        print(f"❌ Error populating sample data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 