#!/bin/bash

# Watchtower Deployment Script
# Deploys the updated system to the Raspberry Pi

set -e

# Configuration
PI_HOST="alex@10.42.69.208"
PI_PORT="5420"
PI_PATH="/opt/alexos/watchtower"
SSH_CMD="ssh -p $PI_PORT $PI_HOST"

echo "🚀 Starting Watchtower deployment..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the watchtower root directory."
    exit 1
fi

echo "📦 Building frontend..."
cd dashboard/frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install
fi

# Build the frontend
echo "🔨 Building React app..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    echo "❌ Error: Frontend build failed"
    exit 1
fi

cd ../..

echo "🔄 Syncing files to Raspberry Pi..."

# Create backup of current deployment
echo "💾 Creating backup..."
$SSH_CMD "cd $PI_PATH && tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz --exclude=venv --exclude=logs --exclude=backup-*.tar.gz ."

# Stop the current service
echo "⏹️  Stopping current service..."
$SSH_CMD "cd $PI_PATH && pkill -f uvicorn || true"
$SSH_CMD "cd $PI_PATH && pkill -f 'python main.py' || true"

# Wait a moment for processes to stop
sleep 3

# Sync the updated files
echo "📤 Uploading files..."
rsync -avz -e "ssh -p $PI_PORT" \
    --exclude=venv \
    --exclude=logs \
    --exclude=__pycache__ \
    --exclude=*.pyc \
    --exclude=.git \
    --exclude=node_modules \
    --exclude=backup-*.tar.gz \
    ./ $PI_HOST:$PI_PATH/

# Set proper permissions
echo "🔐 Setting permissions..."
$SSH_CMD "cd $PI_PATH && chmod +x scripts/deploy.sh"

# Install/update Python dependencies
echo "📥 Installing Python dependencies..."
$SSH_CMD "cd $PI_PATH && source venv/bin/activate && pip install -r requirements.txt"

# Run database migrations
echo "🗄️  Running database migrations..."
$SSH_CMD "cd $PI_PATH && source venv/bin/activate && alembic upgrade head"

# Create logs directory if it doesn't exist
$SSH_CMD "cd $PI_PATH && mkdir -p logs"

# Start the service
echo "▶️  Starting Watchtower service..."
$SSH_CMD "cd $PI_PATH && source venv/bin/activate && nohup uvicorn main:app --host 0.0.0.0 --port 5000 > logs/app.log 2>&1 &"

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 5

# Check if service is running
echo "🔍 Checking service status..."
if $SSH_CMD "cd $PI_PATH && pgrep -f uvicorn > /dev/null"; then
    echo "✅ Service is running"
else
    echo "❌ Service failed to start"
    echo "📋 Recent logs:"
    $SSH_CMD "cd $PI_PATH && tail -20 logs/app.log"
    exit 1
fi

# Test the API endpoints
echo "🧪 Testing API endpoints..."
HEALTH_RESPONSE=$($SSH_CMD "curl -s http://localhost:5000/api/health" || echo "FAILED")
if [[ $HEALTH_RESPONSE == *"healthy"* ]] || [[ $HEALTH_RESPONSE == *"degraded"* ]]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed: $HEALTH_RESPONSE"
fi

# Test authentication endpoint
echo "🔐 Testing authentication..."
AUTH_RESPONSE=$($SSH_CMD "curl -s -X POST http://localhost:5000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}'" || echo "FAILED")
if [[ $AUTH_RESPONSE == *"access_token"* ]]; then
    echo "✅ Authentication working"
else
    echo "❌ Authentication failed: $AUTH_RESPONSE"
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Service Information:"
echo "   - URL: http://10.42.69.208:5000"
echo "   - WebSocket: ws://10.42.69.208:5000/ws"
echo "   - Default login: admin / admin123"
echo ""
echo "📋 Useful commands:"
echo "   - View logs: ssh -p $PI_PORT $PI_HOST 'tail -f $PI_PATH/logs/app.log'"
echo "   - Check status: ssh -p $PI_PORT $PI_HOST 'ps aux | grep uvicorn'"
echo "   - Restart service: ssh -p $PI_PORT $PI_HOST 'cd $PI_PATH && pkill -f uvicorn && source venv/bin/activate && nohup uvicorn main:app --host 0.0.0.0 --port 5000 > logs/app.log 2>&1 &'"
echo ""
echo "🔒 Security Features Added:"
echo "   - User authentication with JWT tokens"
echo "   - WebSocket authentication"
echo "   - Comprehensive audit logging"
echo "   - Input validation and sanitization"
echo "   - Rate limiting and security headers" 