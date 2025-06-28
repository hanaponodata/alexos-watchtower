#!/bin/bash

# ALEX OS Raspberry Pi Deployment Script
# This script deploys ALEX OS with Watchtower integration to a Raspberry Pi

set -e

# Configuration
PI_HOST="alex@10.42.69.208"
PI_PORT="5420"
PI_DIR="/opt/alexos/watchtower"
LOCAL_DIR="$(pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if SSH connection is available
check_ssh() {
    log_info "Checking SSH connection to Raspberry Pi..."
    if ssh -p $PI_PORT -o ConnectTimeout=10 -o BatchMode=yes $PI_HOST "echo 'SSH connection successful'" 2>/dev/null; then
        log_success "SSH connection established"
        return 0
    else
        log_error "SSH connection failed. Please check your connection settings."
        return 1
    fi
}

# Update system packages
update_system() {
    log_info "Updating system packages..."
    ssh -p $PI_PORT $PI_HOST "sudo apt update && sudo apt upgrade -y"
    log_success "System packages updated"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    # Install system packages
    ssh -p $PI_PORT $PI_HOST "sudo apt install -y python3 python3-pip python3-venv git curl wget build-essential libssl-dev libffi-dev python3-dev"
    
    # Install Docker
    ssh -p $PI_PORT $PI_HOST "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo usermod -aG docker alex"
    
    # Install additional packages
    ssh -p $PI_PORT $PI_HOST "sudo apt install -y htop iotop nethogs"
    
    log_success "Dependencies installed"
}

# Create ALEX OS directory structure
setup_directories() {
    log_info "Setting up ALEX OS directory structure..."
    
    ssh -p $PI_PORT $PI_HOST "sudo mkdir -p $PI_DIR"
    ssh -p $PI_PORT $PI_HOST "sudo chown alex:alex $PI_DIR"
    ssh -p $PI_PORT $PI_HOST "mkdir -p $PI_DIR/{config,logs,backup,data}"
    
    log_success "Directory structure created"
}

# Deploy ALEX OS files
deploy_files() {
    log_info "Deploying ALEX OS files..."
    
    # Create deployment package
    tar -czf alexos_deploy.tar.gz \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        --exclude='logs/*' \
        .
    
    # Upload to Pi
    scp -P $PI_PORT alexos_deploy.tar.gz $PI_HOST:$PI_DIR/
    
    # Extract on Pi
    ssh -p $PI_PORT $PI_HOST "cd $PI_DIR && tar -xzf alexos_deploy.tar.gz && rm alexos_deploy.tar.gz"
    
    # Clean up local package
    rm alexos_deploy.tar.gz
    
    log_success "ALEX OS files deployed"
}

# Setup Python virtual environment
setup_python_env() {
    log_info "Setting up Python virtual environment..."
    
    ssh -p $PI_PORT $PI_HOST "cd $PI_DIR && python3 -m venv venv"
    ssh -p $PI_PORT $PI_HOST "cd $PI_DIR && source venv/bin/activate && pip install --upgrade pip"
    ssh -p $PI_PORT $PI_HOST "cd $PI_DIR && source venv/bin/activate && pip install -r requirements.txt"
    
    # Install additional Pi-specific packages
    ssh -p $PI_PORT $PI_HOST "cd $PI_DIR && source venv/bin/activate && pip install RPi.GPIO psutil docker pyyaml fastapi uvicorn"
    
    log_success "Python environment setup complete"
}

# Configure ALEX OS
configure_alexos() {
    log_info "Configuring ALEX OS..."
    
    # Create configuration file
    cat > alexos_config.yml << EOF
system:
  name: "ALEX OS Pi"
  environment: "production"
  log_level: "INFO"

api:
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["*"]

web:
  enabled: true
  port: 8080

agents:
  watchtower:
    enabled: true
    config:
      update_interval: 300
      cleanup: true
      auto_update: false
      monitoring_enabled: true
      monitoring_interval: 30

ledger:
  enabled: true
  max_events: 10000

system:
  health_monitor:
    enabled: true
    interval: 60
  backup_manager:
    enabled: true
    schedule: "0 2 * * *"
EOF

    # Upload configuration
    scp -P $PI_PORT alexos_config.yml $PI_HOST:$PI_DIR/config/
    rm alexos_config.yml
    
    log_success "ALEX OS configured"
}

# Setup systemd service
setup_service() {
    log_info "Setting up systemd service..."
    
    # Create service file
    cat > alexos.service << EOF
[Unit]
Description=ALEX OS with Watchtower Integration
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=alex
Group=alex
WorkingDirectory=$PI_DIR
Environment=PATH=$PI_DIR/venv/bin
ExecStart=$PI_DIR/venv/bin/python -m main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Upload and install service
    scp -P $PI_PORT alexos.service $PI_HOST:/tmp/
    ssh -p $PI_PORT $PI_HOST "sudo mv /tmp/alexos.service /etc/systemd/system/"
    ssh -p $PI_PORT $PI_HOST "sudo systemctl daemon-reload"
    ssh -p $PI_PORT $PI_HOST "sudo systemctl enable alexos"
    
    rm alexos.service
    
    log_success "Systemd service configured"
}

# Configure firewall
configure_firewall() {
    log_info "Configuring firewall..."
    
    ssh -p $PI_PORT $PI_HOST "sudo ufw allow 8000/tcp"  # API
    ssh -p $PI_PORT $PI_HOST "sudo ufw allow 8080/tcp"  # Web Dashboard
    ssh -p $PI_PORT $PI_HOST "sudo ufw allow 22/tcp"    # SSH
    ssh -p $PI_PORT $PI_HOST "sudo ufw --force enable"
    
    log_success "Firewall configured"
}

# Setup database
setup_database() {
    log_info "Setting up database..."
    
    ssh -p $PI_PORT $PI_HOST "cd $PI_DIR && source venv/bin/activate && python scripts/setup_db.py"
    
    log_success "Database setup complete"
}

# Start services
start_services() {
    log_info "Starting ALEX OS services..."
    
    ssh -p $PI_PORT $PI_HOST "sudo systemctl start alexos"
    sleep 5
    
    # Check service status
    if ssh -p $PI_PORT $PI_HOST "sudo systemctl is-active alexos" | grep -q "active"; then
        log_success "ALEX OS service started successfully"
    else
        log_error "ALEX OS service failed to start"
        ssh -p $PI_PORT $PI_HOST "sudo journalctl -u alexos -n 20"
        return 1
    fi
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Test API
    if curl -s http://$PI_HOST:8000/api/status/ > /dev/null; then
        log_success "API is responding"
    else
        log_error "API is not responding"
        return 1
    fi
    
    # Test web dashboard
    if curl -s http://$PI_HOST:8080/web/ > /dev/null; then
        log_success "Web dashboard is accessible"
    else
        log_error "Web dashboard is not accessible"
        return 1
    fi
    
    # Test Watchtower integration
    if curl -s http://$PI_HOST:8000/api/watchtower/status/ > /dev/null; then
        log_success "Watchtower integration is working"
    else
        log_warning "Watchtower integration may not be fully configured"
    fi
    
    log_success "Deployment verification complete"
}

# Main deployment function
main() {
    log_info "Starting ALEX OS Raspberry Pi deployment..."
    
    # Check prerequisites
    if ! check_ssh; then
        exit 1
    fi
    
    # Execute deployment steps
    update_system
    install_dependencies
    setup_directories
    deploy_files
    setup_python_env
    configure_alexos
    setup_service
    configure_firewall
    setup_database
    start_services
    verify_deployment
    
    log_success "ALEX OS deployment completed successfully!"
    log_info "Access your ALEX OS dashboard at: http://$PI_HOST:8080/web/"
    log_info "API documentation at: http://$PI_HOST:8000/api/docs"
    log_info "Check service status with: ssh -p $PI_PORT $PI_HOST 'sudo systemctl status alexos'"
}

# Run main function
main "$@" 