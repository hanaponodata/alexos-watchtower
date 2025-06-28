#!/usr/bin/env python3
"""
scripts/deploy_frontend.py
Deploy the built frontend to the Raspberry Pi.
"""

import os
import subprocess
import sys
from pathlib import Path

# Configuration
PI_IP = "10.42.69.208"
PI_USER = "alex"  # Change if different
PI_SSH_PORT = "5420"
PI_PATH = "/opt/alexos/watchtower/dashboard/frontend/build"
LOCAL_BUILD_PATH = "dashboard/frontend/build"
SUDO_PASSWORD = "P0n0p0n0$&@"

def run_command(cmd, check=True):
    """Run a shell command."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def main():
    print("🚀 Deploying frontend to Raspberry Pi...")
    
    # Check if build directory exists
    if not Path(LOCAL_BUILD_PATH).exists():
        print(f"❌ Build directory not found: {LOCAL_BUILD_PATH}")
        print("Please run 'npm run build' in dashboard/frontend first")
        sys.exit(1)
    
    print(f"✅ Found build directory: {LOCAL_BUILD_PATH}")
    
    # Create remote directory if it doesn't exist
    print("📁 Creating remote directory...")
    run_command(f"ssh -p {PI_SSH_PORT} {PI_USER}@{PI_IP} 'mkdir -p {PI_PATH}'")
    
    # Copy build files to Pi
    print("📤 Copying files to Pi...")
    run_command(f"scp -P {PI_SSH_PORT} -r {LOCAL_BUILD_PATH}/* {PI_USER}@{PI_IP}:{PI_PATH}/")
    
    # Restart the watchtower service on Pi
    print("🔄 Restarting watchtower service...")
    # Create a temporary script on the Pi to handle sudo
    temp_script = f"""
#!/bin/bash
echo "{SUDO_PASSWORD}" | sudo -S systemctl restart watchtower
"""
    run_command(f"ssh -p {PI_SSH_PORT} {PI_USER}@{PI_IP} 'cat > /tmp/restart_watchtower.sh << \"EOF\"\n{temp_script}\nEOF'")
    run_command(f"ssh -p {PI_SSH_PORT} {PI_USER}@{PI_IP} 'chmod +x /tmp/restart_watchtower.sh && /tmp/restart_watchtower.sh'")
    run_command(f"ssh -p {PI_SSH_PORT} {PI_USER}@{PI_IP} 'rm /tmp/restart_watchtower.sh'")
    
    print("✅ Deployment complete!")
    print(f"🌐 Dashboard should be available at: http://{PI_IP}:5000/dashboard")

if __name__ == "__main__":
    main() 