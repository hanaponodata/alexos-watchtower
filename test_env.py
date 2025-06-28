#!/usr/bin/env python3
"""Test script to check .env loading."""

import os
from pathlib import Path
from dotenv import load_dotenv

print("Before loading .env:")
print(f"WATCHTOWER_ADMIN_KEY: {os.environ.get('WATCHTOWER_ADMIN_KEY')}")

env_path = Path(".env")
print(f"Env file exists: {env_path.exists()}")

if env_path.exists():
    load_dotenv(env_path)
    print("After loading .env:")
    print(f"WATCHTOWER_ADMIN_KEY: {os.environ.get('WATCHTOWER_ADMIN_KEY')}")
else:
    print("No .env file found") 