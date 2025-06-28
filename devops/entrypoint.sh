#!/bin/bash
# devops/entrypoint.sh
set -e

echo "Starting Watchtower..."

# Run database migrations if using Alembic (optional)
if [ -f "./alembic.ini" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

# Start the FastAPI server
exec uvicorn main:app --host 0.0.0.0 --port 5000
