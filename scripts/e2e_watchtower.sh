#!/bin/bash
# E2E test for Watchtower as ALEX OS module
set -e

# 1. Start backend (assume systemd)
echo "[E2E] Starting Watchtower backend..."
sudo systemctl restart watchtower.service
sleep 5

# 2. Check health
echo "[E2E] Checking /api/status..."
curl -sf http://localhost:5000/api/status

# 3. Register agent
echo "[E2E] Registering agent..."
AGENT_UUID=$(uuidgen)
AGENT_PAYLOAD=$(cat <<EOF
{
  "uuid": "$AGENT_UUID",
  "name": "E2E Agent",
  "agent_type": "monitoring",
  "owner": "e2e-test",
  "description": "E2E test agent",
  "status": "online",
  "score": 100
}
EOF
)
curl -sf -X POST http://localhost:5000/api/agents/ -H 'Content-Type: application/json' -d "$AGENT_PAYLOAD"

# 4. Stream events (simulate via API)
echo "[E2E] Creating event..."
EVENT_PAYLOAD=$(cat <<EOF
{
  "event_type": "test_event",
  "agent_uuid": "$AGENT_UUID",
  "severity": "info",
  "payload": {"message": "E2E event"},
  "source": "e2e-test"
}
EOF
)
curl -sf -X POST http://localhost:5000/api/events/ -H 'Content-Type: application/json' -d "$EVENT_PAYLOAD"

# 5. Validate audit log (list events)
echo "[E2E] Validating event log..."
curl -sf http://localhost:5000/api/events | grep 'E2E event'

echo "[E2E] SUCCESS: Watchtower E2E test passed." 