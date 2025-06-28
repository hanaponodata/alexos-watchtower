#!/usr/bin/env python3
"""
Test script for ALEX OS Watchtower Integration
Verifies that all components can be imported and initialized correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        # Test Watchtower module import
        from alexos_integration.modules.watchtower import create_watchtower_agent
        print("✅ Watchtower module import successful")
        
        # Test API routes import
        from alexos_integration.api.watchtower_routes import register_watchtower_routes, set_watchtower_agent
        print("✅ Watchtower API routes import successful")
        
        # Test configuration import
        from alexos_integration.config import watchtower_config
        print("✅ Watchtower configuration import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_agent_creation():
    """Test Watchtower agent creation."""
    print("\n🔧 Testing agent creation...")
    
    try:
        from alexos_integration.modules.watchtower import create_watchtower_agent
        
        # Create test configuration
        test_config = {
            'watchtower': {
                'update_interval': 300,
                'cleanup': True,
                'auto_update': False,
                'monitoring_enabled': True,
                'monitoring_interval': 30,
                'webhook_enabled': True,
                'log_level': 'INFO'
            }
        }
        
        # Create agent
        agent = create_watchtower_agent(
            "test-watchtower-001",
            "Test Watchtower Monitor",
            event_bus=None,
            ledger=None,
            config=test_config
        )
        
        print(f"✅ Agent created successfully: {agent.name} (ID: {agent.agent_id})")
        print(f"   Status: {agent.status}")
        print(f"   Config: {agent.watchtower_config}")
        
        return agent
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return None

async def test_agent_lifecycle(agent):
    """Test agent startup and shutdown."""
    print("\n🚀 Testing agent lifecycle...")
    
    try:
        # Test agent start
        print("   Starting agent...")
        await agent.start()
        print(f"   ✅ Agent started successfully. Status: {agent.status}")
        
        # Test status methods
        status = await agent.get_status()
        print(f"   ✅ Status retrieved: {status['status']}")
        
        containers = await agent.get_containers()
        print(f"   ✅ Containers retrieved: {len(containers)} containers")
        
        updates = await agent.get_update_history()
        print(f"   ✅ Update history retrieved: {len(updates)} updates")
        
        # Test agent stop
        print("   Stopping agent...")
        await agent.stop()
        print(f"   ✅ Agent stopped successfully. Status: {agent.status}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Agent lifecycle test failed: {e}")
        return False

def test_template_exists():
    """Test that the Watchtower template exists."""
    print("\n📄 Testing template files...")
    
    template_path = Path("dashboard/templates/watchtower.html")
    if template_path.exists():
        print(f"✅ Watchtower template found: {template_path}")
        return True
    else:
        print(f"❌ Watchtower template not found: {template_path}")
        return False

def test_api_routes():
    """Test API routes registration."""
    print("\n🌐 Testing API routes...")
    
    try:
        from fastapi import FastAPI
        from alexos_integration.api.watchtower_routes import register_watchtower_routes
        
        # Create test app
        app = FastAPI()
        
        # Register routes
        register_watchtower_routes(app)
        
        # Check if routes were registered
        route_count = len(app.routes)
        print(f"✅ API routes registered: {route_count} total routes")
        print("   - Watchtower routes should be available at /api/watchtower/*")
        
        return True
        
    except Exception as e:
        print(f"❌ API routes test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 ALEX OS Watchtower Integration Test Suite")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Exiting.")
        return False
    
    # Test agent creation
    agent = test_agent_creation()
    if not agent:
        print("\n❌ Agent creation failed. Exiting.")
        return False
    
    # Test agent lifecycle
    if not await test_agent_lifecycle(agent):
        print("\n❌ Agent lifecycle test failed.")
        return False
    
    # Test template files
    if not test_template_exists():
        print("\n❌ Template file test failed.")
        return False
    
    # Test API routes
    if not test_api_routes():
        print("\n❌ API routes test failed.")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! ALEX OS Watchtower integration is working correctly.")
    print("\n📋 Next steps:")
    print("   1. Start the application: python3 main.py")
    print("   2. Access the dashboard: http://localhost:8000/dashboard/")
    print("   3. Access Watchtower dashboard: http://localhost:8000/dashboard/watchtower")
    print("   4. View API docs: http://localhost:8000/api/docs")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1) 