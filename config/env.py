"""
config/env.py
Environment variable and runtime environment utilities for Watchtower.
Handles detection of environment, containerization, user/hostname, and .env file loading.
"""

import os
import socket
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists (for local/dev)
dotenv_path = Path(".env")
if dotenv_path.exists():
    load_dotenv(dotenv_path)

def get_env(var: str, default=None):
    """Get environment variable with optional default."""
    return os.environ.get(var, default)

def is_docker():
    """Detect if running inside a Docker container."""
    path = "/proc/1/cgroup"
    if os.path.exists(path):
        with open(path, "r") as f:
            return "docker" in f.read() or "containerd" in f.read()
    return False

def is_kubernetes():
    """Detect if running inside a Kubernetes pod."""
    return "KUBERNETES_SERVICE_HOST" in os.environ

def running_env():
    """Return human-readable environment info."""
    env = get_env("WATCHTOWER_ENV", "production")
    if is_docker():
        env += " (docker)"
    if is_kubernetes():
        env += " (k8s)"
    return env

def get_hostname():
    """Get system hostname."""
    return socket.gethostname()

def get_user():
    """Get effective user."""
    try:
        return os.getlogin()
    except Exception:
        return os.environ.get("USER") or "unknown"

def env_summary():
    """Return key environment details for diagnostics/logging."""
    return {
        "environment": running_env(),
        "hostname": get_hostname(),
        "user": get_user(),
        "docker": is_docker(),
        "kubernetes": is_kubernetes()
    }

if __name__ == "__main__":
    # Quick diagnostic printout
    import pprint
    pprint.pprint(env_summary())
