#!/bin/bash
P95=$(curl -s http://localhost:8000/api/performance | jq .p95_agents_status)
echo "P95 /api/agents/status: $P95 ms"
if [ "$P95" -gt 200 ]; then
  echo "Performance regression detected!"
  exit 1
fi 