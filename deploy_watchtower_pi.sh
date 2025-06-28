#!/bin/bash

set -e

PI_HOST="alex@10.42.69.208"
PI_PORT=5420
PI_DIR="/opt/alexos/watchtower"
PI_VENV="$PI_DIR/venv/bin/activate"
PI_PY="$PI_DIR/venv/bin/python3"
WATCHTOWER_PORT=8100

echo "---- [1/8] SSH: Creating watchtower directory on Pi ----"
ssh -p $PI_PORT $PI_HOST "
  mkdir -p $PI_DIR
"

echo "---- [2/8] SSH: Stopping all Watchtower/Python processes on Pi ----"
ssh -p $PI_PORT $PI_HOST "
  cd $PI_DIR
  pkill -f 'python3 main.py' || true
  pkill -f 'uvicorn' || true
  lsof -ti:8081 | xargs kill -9 || true
  lsof -ti:8100 | xargs kill -9 || true
  lsof -ti:5000 | xargs kill -9 || true
"

echo "---- [3/8] SSH: Copying files to Pi ----"
rsync -avz -e "ssh -p $PI_PORT" --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' . $PI_HOST:$PI_DIR/

echo "---- [4/8] SSH: Setting correct port in .env ----"
ssh -p $PI_PORT $PI_HOST "
  cd $PI_DIR
  if grep -q '^WATCHTOWER_PORT=' .env; then
    sed -i 's/^WATCHTOWER_PORT=.*/WATCHTOWER_PORT=$WATCHTOWER_PORT/' .env
  else
    echo 'WATCHTOWER_PORT=$WATCHTOWER_PORT' >> .env
  fi
"

echo "---- [5/8] SSH: Creating virtual environment ----"
ssh -p $PI_PORT $PI_HOST "
  cd $PI_DIR
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
"

echo "---- [6/8] SSH: Starting Watchtower on port $WATCHTOWER_PORT ----"
ssh -p $PI_PORT $PI_HOST "
  cd $PI_DIR
  source venv/bin/activate
  nohup python3 main.py > deploy.log 2>&1 &
  sleep 5
"

echo "---- [7/8] SSH: Checking Watchtower health endpoint ----"
ssh -p $PI_PORT $PI_HOST "
  curl -s http://localhost:$WATCHTOWER_PORT/api/health || echo 'Health endpoint not responding'
"

echo "---- [8/8] SSH: Checking Watchtower status endpoint ----"
ssh -p $PI_PORT $PI_HOST "
  curl -s http://localhost:$WATCHTOWER_PORT/api/watchtower/status || echo 'Status endpoint not responding'
"

echo "---- Deployment complete! ----" 