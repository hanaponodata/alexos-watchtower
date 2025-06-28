#!/usr/bin/env python3
"""Test script to debug authentication token validation."""

import os
import hashlib
import hmac
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(".env")
if env_path.exists():
    load_dotenv(env_path)

# Get admin key
admin_key = os.environ.get("WATCHTOWER_ADMIN_KEY", "default")
print(f"Admin key: {admin_key}")

# Test token generation
user_id = "admin-001"
username = "admin"
role = "admin"
timestamp = datetime.utcnow().isoformat()
payload = f"{user_id}:{username}:{role}:{timestamp}"

print(f"Payload: {payload}")

signature = hmac.new(
    admin_key.encode(),
    payload.encode(),
    hashlib.sha256
).hexdigest()

print(f"Signature: {signature}")

token = f"{payload}:{signature}"
print(f"Token: {token}")

# Test token validation
parts = token.split(":")
if len(parts) == 5:
    user_id_val, username_val, role_val, timestamp_val, signature_val = parts
    
    # Check expiration
    token_time = datetime.fromisoformat(timestamp_val)
    if datetime.utcnow() - token_time > timedelta(hours=24):
        print("Token expired")
    else:
        # Verify signature
        payload_val = f"{user_id_val}:{username_val}:{role_val}:{timestamp_val}"
        expected_signature = hmac.new(
            admin_key.encode(),
            payload_val.encode(),
            hashlib.sha256
        ).hexdigest()
        
        print(f"Expected signature: {expected_signature}")
        print(f"Received signature: {signature_val}")
        print(f"Signatures match: {hmac.compare_digest(signature_val, expected_signature)}")
else:
    print(f"Invalid token format: {len(parts)} parts") 