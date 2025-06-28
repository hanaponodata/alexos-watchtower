#!/bin/bash

# ALEX OS Custom Raspberry Pi Distribution Creator
# This script creates a custom Raspberry Pi OS image with ALEX OS pre-installed

set -e

# Configuration
IMAGE_URL="https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf-lite.img.xz"
IMAGE_NAME="2023-05-03-raspios-bullseye-armhf-lite.img"
CUSTOM_IMAGE_NAME="alexos-pi-distribution.img"
WORK_DIR="$(pwd)/distribution_build"
MOUNT_DIR="$WORK_DIR/mount"
ALEXOS_DIR="$MOUNT_DIR/opt/alexos"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Create work directory
setup_work_dir() {
    log_info "Setting up work directory..."
    mkdir -p "$WORK_DIR"
    mkdir -p "$MOUNT_DIR"
    cd "$WORK_DIR"
}

# Download Raspberry Pi OS image
download_image() {
    log_info "Downloading Raspberry Pi OS image..."
    
    if [[ ! -f "$IMAGE_NAME.xz" ]]; then
        wget "$IMAGE_URL"
    else
        log_info "Image already downloaded"
    fi
    
    if [[ ! -f "$IMAGE_NAME" ]]; then
        log_info "Extracting image..."
        xz -d "$IMAGE_NAME.xz"
    fi
    
    log_success "Image downloaded and extracted"
}

# Mount image
mount_image() {
    log_info "Mounting image..."
    
    # Find loop device
    LOOP_DEVICE=$(losetup -f)
    
    # Setup loop device
    losetup -P "$LOOP_DEVICE" "$IMAGE_NAME"
    
    # Mount partitions
    mount "${LOOP_DEVICE}p2" "$MOUNT_DIR"
    mount "${LOOP_DEVICE}p1" "$MOUNT_DIR/boot"
    
    log_success "Image mounted at $MOUNT_DIR"
}

# Install ALEX OS
install_alexos() {
    log_info "Installing ALEX OS..."
    
    # Create ALEX OS directory
    mkdir -p "$ALEXOS_DIR"
    
    # Copy ALEX OS files (excluding venv and cache)
    rsync -av --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' --exclude='logs/*' \
        ../ "$ALEXOS_DIR/"
    
    # Create ALEX OS user
    chroot "$MOUNT_DIR" useradd -m -s /bin/bash alexos
    chroot "$MOUNT_DIR" usermod -aG docker alexos
    
    # Set ownership
    chown -R alexos:alexos "$ALEXOS_DIR"
    
    log_success "ALEX OS installed"
}

# Setup Python environment
setup_python_env() {
    log_info "Setting up Python environment..."
    
    # Install Python packages
    chroot "$MOUNT_DIR" apt update
    chroot "$MOUNT_DIR" apt install -y python3 python3-pip python3-venv git curl wget build-essential libssl-dev libffi-dev python3-dev
    
    # Create virtual environment
    chroot "$MOUNT_DIR" bash -c "cd /opt/alexos && python3 -m venv venv"
    chroot "$MOUNT_DIR" bash -c "cd /opt/alexos && source venv/bin/activate && pip install --upgrade pip"
    chroot "$MOUNT_DIR" bash -c "cd /opt/alexos && source venv/bin/activate && pip install -r requirements.txt"
    
    # Install additional packages
    chroot "$MOUNT_DIR" bash -c "cd /opt/alexos && source venv/bin/activate && pip install RPi.GPIO psutil docker pyyaml fastapi uvicorn"
    
    log_success "Python environment setup complete"
}

# Configure system
configure_system() {
    log_info "Configuring system..."
    
    # Update hostname
    echo "alexos-pi" > "$MOUNT_DIR/etc/hostname"
    sed -i 's/raspberrypi/alexos-pi/g' "$MOUNT_DIR/etc/hosts"
    
    # Configure network
    cat > "$MOUNT_DIR/etc/network/interfaces.d/alexos" << EOF
auto eth0
iface eth0 inet dhcp

auto wlan0
iface wlan0 inet dhcp
    wpa-ssid "ALEX_OS_NETWORK"
    wpa-psk "your_password_here"
EOF
    
    # Configure firewall
    chroot "$MOUNT_DIR" ufw allow 8000/tcp
    chroot "$MOUNT_DIR" ufw allow 8080/tcp
    chroot "$MOUNT_DIR" ufw allow 22/tcp
    chroot "$MOUNT_DIR" ufw --force enable
    
    log_success "System configured"
}

# Configure boot
configure_boot() {
    log_info "Configuring boot options..."
    
    # Configure config.txt
    cat > "$MOUNT_DIR/boot/config.txt" << EOF
# ALEX OS Configuration
dtoverlay=disable-wifi
dtoverlay=disable-bt
gpu_mem=16
max_usb_current=1
enable_uart=1
EOF
    
    # Configure cmdline
    sed -i 's/console=serial0,115200 console=tty1/console=tty1/g' "$MOUNT_DIR/boot/cmdline.txt"
    
    log_success "Boot configuration complete"
}

# Setup systemd service
setup_service() {
    log_info "Setting up systemd service..."
    
    cat > "$MOUNT_DIR/etc/systemd/system/alexos.service" << EOF
[Unit]
Description=ALEX OS with Watchtower Integration
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=alexos
Group=alexos
WorkingDirectory=/opt/alexos
Environment=PATH=/opt/alexos/venv/bin
ExecStart=/opt/alexos/venv/bin/python -m main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable service
    chroot "$MOUNT_DIR" systemctl enable alexos
    
    log_success "Systemd service configured"
}

# Install Docker
install_docker() {
    log_info "Installing Docker..."
    
    # Install Docker
    chroot "$MOUNT_DIR" curl -fsSL https://get.docker.com -o get-docker.sh
    chroot "$MOUNT_DIR" sh get-docker.sh
    chroot "$MOUNT_DIR" usermod -aG docker alexos
    
    log_success "Docker installed"
}

# Setup database
setup_database() {
    log_info "Setting up database..."
    
    chroot "$MOUNT_DIR" bash -c "cd /opt/alexos && source venv/bin/activate && python scripts/setup_db.py"
    
    log_success "Database setup complete"
}

# Create first boot script
create_first_boot() {
    log_info "Creating first boot script..."
    
    cat > "$MOUNT_DIR/opt/alexos/first_boot.sh" << 'EOF'
#!/bin/bash

# ALEX OS First Boot Script
# This script runs on first boot to complete setup

set -e

LOG_FILE="/var/log/alexos-first-boot.log"

log() {
    echo "$(date): $1" | tee -a "$LOG_FILE"
}

log "Starting ALEX OS first boot setup..."

# Update system
log "Updating system packages..."
apt update && apt upgrade -y

# Configure network (if needed)
log "Configuring network..."

# Start ALEX OS service
log "Starting ALEX OS service..."
systemctl start alexos

# Mark first boot as complete
log "First boot setup complete"
touch /opt/alexos/.first_boot_complete

log "ALEX OS is ready!"
log "Access dashboard at: http://$(hostname -I | awk '{print $1}'):8080/web/"
EOF
    
    chmod +x "$MOUNT_DIR/opt/alexos/first_boot.sh"
    
    # Add to rc.local for first boot
    cat > "$MOUNT_DIR/etc/rc.local" << EOF
#!/bin/bash

# Run first boot script if not already completed
if [[ ! -f /opt/alexos/.first_boot_complete ]]; then
    /opt/alexos/first_boot.sh &
fi

exit 0
EOF
    
    chmod +x "$MOUNT_DIR/etc/rc.local"
    
    log_success "First boot script created"
}

# Unmount image
unmount_image() {
    log_info "Unmounting image..."
    
    # Unmount partitions
    umount "$MOUNT_DIR/boot"
    umount "$MOUNT_DIR"
    
    # Remove loop device
    losetup -d /dev/loop0
    
    log_success "Image unmounted"
}

# Compress final image
compress_image() {
    log_info "Compressing final image..."
    
    xz -z "$IMAGE_NAME"
    mv "$IMAGE_NAME.xz" "$CUSTOM_IMAGE_NAME.xz"
    
    log_success "Final image compressed: $CUSTOM_IMAGE_NAME.xz"
}

# Create installer script
create_installer() {
    log_info "Creating installer script..."
    
    cat > alexos-installer.sh << 'EOF'
#!/bin/bash

# ALEX OS Installer Script
# This script installs ALEX OS on a Raspberry Pi

set -e

# Configuration
ALEXOS_IMAGE="alexos-pi-distribution.img.xz"
TARGET_DEVICE=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Select target device
select_device() {
    log_info "Available storage devices:"
    lsblk -d -o NAME,SIZE,MODEL
    
    read -p "Enter target device (e.g., /dev/sdb): " TARGET_DEVICE
    
    if [[ ! -b "$TARGET_DEVICE" ]]; then
        log_error "Invalid device: $TARGET_DEVICE"
        exit 1
    fi
    
    read -p "This will erase all data on $TARGET_DEVICE. Continue? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        log_info "Installation cancelled"
        exit 0
    fi
}

# Write image to device
write_image() {
    log_info "Writing ALEX OS image to $TARGET_DEVICE..."
    
    if [[ ! -f "$ALEXOS_IMAGE" ]]; then
        log_error "Image file not found: $ALEXOS_IMAGE"
        exit 1
    fi
    
    # Uncompress and write
    xz -dc "$ALEXOS_IMAGE" | dd of="$TARGET_DEVICE" bs=4M status=progress
    
    # Sync to ensure writing is complete
    sync
    
    log_success "Image written successfully"
}

# Main installation
main() {
    log_info "Starting ALEX OS installation..."
    
    check_root
    select_device
    write_image
    
    log_success "ALEX OS installation complete!"
    log_info "Insert the SD card into your Raspberry Pi and boot it up."
    log_info "ALEX OS will automatically configure itself on first boot."
    log_info "Access the dashboard at: http://[PI_IP]:8080/web/"
}

main "$@"
EOF
    
    chmod +x alexos-installer.sh
    
    log_success "Installer script created: alexos-installer.sh"
}

# Main build function
main() {
    log_info "Starting ALEX OS custom distribution build..."
    
    check_root
    setup_work_dir
    download_image
    mount_image
    
    install_alexos
    setup_python_env
    configure_system
    configure_boot
    setup_service
    install_docker
    setup_database
    create_first_boot
    
    unmount_image
    compress_image
    create_installer
    
    log_success "ALEX OS custom distribution build completed!"
    log_info "Distribution image: $CUSTOM_IMAGE_NAME.xz"
    log_info "Installer script: alexos-installer.sh"
    log_info "To install on SD card: sudo ./alexos-installer.sh"
}

# Run main function
main "$@" 