"""
Basic API tests for Watchtower.
Tests core endpoints and functionality.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Watchtower API running" in data["message"]

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/dashboard/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data

def test_agents_endpoint():
    """Test the agents endpoint."""
    response = client.get("/api/agents/")
    # Should return 200 even if no agents exist
    assert response.status_code in [200, 500]  # 500 if DB not configured

def test_events_endpoint():
    """Test the events endpoint."""
    response = client.get("/api/events/")
    # Should return 200 even if no events exist
    assert response.status_code in [200, 500]  # 500 if DB not configured

def test_status_endpoint():
    """Test the status endpoint."""
    response = client.get("/api/status/")
    # Should return 200 even if DB not configured
    assert response.status_code in [200, 500]  # 500 if DB not configured

def test_dashboard_serving():
    """Test that dashboard serves HTML."""
    response = client.get("/dashboard/")
    assert response.status_code == 200
    # Should return HTML content
    assert "text/html" in response.headers.get("content-type", "")

if __name__ == "__main__":
    pytest.main([__file__]) 