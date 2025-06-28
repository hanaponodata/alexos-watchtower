#!/usr/bin/env python3
"""
Critical Security Fixes Script
Addresses the most critical security issues identified in the enterprise audit.
"""

import os
import re
import shutil
from pathlib import Path

def create_env_example():
    """Create .env.example with all required environment variables."""
    env_content = """# Watchtower Environment Configuration
# Copy this file to .env and update with your actual values

# Core server
WATCHTOWER_ENV=production
WATCHTOWER_DEBUG=false
WATCHTOWER_HOST=0.0.0.0
WATCHTOWER_PORT=5000

# Database (CRITICAL: Change these passwords!)
WATCHTOWER_DB_URL=postgresql+psycopg2://watchtower:CHANGE_THIS_PASSWORD@localhost:5432/watchtower
WATCHTOWER_DB_POOL_SIZE=20
WATCHTOWER_DB_TIMEOUT=30
WATCHTOWER_DB_ECHO=false

# Logging
WATCHTOWER_LOG_LEVEL=INFO
WATCHTOWER_LOG_DIR=logs
WATCHTOWER_LOG_ROTATION=10 MB
WATCHTOWER_LOG_BACKUP_COUNT=7
WATCHTOWER_AUDIT_LOG=true

# Secrets Management (CRITICAL: Use proper secrets management)
WATCHTOWER_SECRET_FILE=/path/to/secrets.json
WATCHTOWER_VAULT_ADDR=https://vault.example.com:8200

# API Authentication (CRITICAL: Generate secure keys)
WATCHTOWER_API_KEYS=your-secure-api-key-here
WATCHTOWER_ADMIN_KEY=your-secure-admin-key-here

# Federation/Cluster
WATCHTOWER_NODE_ID=watchtower-01
WATCHTOWER_PEERS=node2.example.com,node3.example.com
WATCHTOWER_CONSENSUS_ENGINE=raft
WATCHTOWER_ENABLE_FEDERATION=true

# Message Bus
WATCHTOWER_MESSAGE_BUS=nats
WATCHTOWER_MESSAGE_BUS_URL=nats://localhost:4222

# LLM/AI Agents
WATCHTOWER_LLM_PROXY_URL=https://api.openai.com/v1
WATCHTOWER_LLM_API_KEY=your-llm-api-key-here
WATCHTOWER_SHADOW_COPILOT_ENABLED=true

# Blockchain/Tokenization
WATCHTOWER_ENABLE_BLOCKCHAIN=false
WATCHTOWER_BLOCKCHAIN_NETWORK=ethereum
WATCHTOWER_BLOCKCHAIN_RPC=https://mainnet.infura.io/v3/your-project-id

# Entropy/Quantum
WATCHTOWER_USE_HARDWARE_ENTROPY=true
WATCHTOWER_ENTROPY_DEVICE=/dev/hwrng

# Plugins
WATCHTOWER_ENABLE_PLUGINS=true
WATCHTOWER_PLUGIN_DIR=plugins

# Compliance
WATCHTOWER_ENABLE_COMPLIANCE=true
WATCHTOWER_COMPLIANCE_EXPORT_DIR=compliance
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    print("✅ Created .env.example with all required variables")

def fix_docker_compose():
    """Fix hardcoded credentials in docker-compose.yml."""
    compose_file = 'docker-compose.yml'
    if not os.path.exists(compose_file):
        print(f"⚠️  {compose_file} not found, skipping")
        return
    
    with open(compose_file, 'r') as f:
        content = f.read()
    
    # Replace hardcoded passwords with environment variables
    content = re.sub(
        r'POSTGRES_PASSWORD: m3t4ph0r\$&@',
        'POSTGRES_PASSWORD: ${DB_PASSWORD}',
        content
    )
    content = re.sub(
        r'POSTGRES_PASSWORD: t3stpw\$&@',
        'POSTGRES_PASSWORD: ${DB_TEST_PASSWORD}',
        content
    )
    
    # Add environment file reference
    if 'env_file:' not in content:
        content = content.replace('version: "3.9"\n\nservices:', 
                                'version: "3.9"\n\nservices:')
        content = content.replace('  db-main:', 
                                '  db-main:\n    env_file:\n      - .env')
        content = content.replace('  db-test:', 
                                '  db-test:\n    env_file:\n      - .env')
    
    with open(compose_file, 'w') as f:
        f.write(content)
    print("✅ Fixed hardcoded credentials in docker-compose.yml")

def fix_k8s_manifests():
    """Fix hardcoded credentials in Kubernetes manifests."""
    k8s_file = 'devops/k8s.yaml'
    if not os.path.exists(k8s_file):
        print(f"⚠️  {k8s_file} not found, skipping")
        return
    
    with open(k8s_file, 'r') as f:
        content = f.read()
    
    # Replace hardcoded database URL with secret reference
    content = re.sub(
        r'value: "postgresql\+psycopg2://watchtower:password@watchtower-db:5432/watchtower"',
        'valueFrom:\n              secretKeyRef:\n                name: watchtower-secrets\n                key: db-url',
        content
    )
    
    # Replace hardcoded password with secret reference
    content = re.sub(
        r'value: password',
        'valueFrom:\n              secretKeyRef:\n                name: watchtower-secrets\n                key: db-password',
        content
    )
    
    with open(k8s_file, 'w') as f:
        f.write(content)
    print("✅ Fixed hardcoded credentials in k8s.yaml")

def create_secrets_template():
    """Create Kubernetes secrets template."""
    secrets_content = """apiVersion: v1
kind: Secret
metadata:
  name: watchtower-secrets
type: Opaque
data:
  # Base64 encoded values - replace with your actual values
  db-url: cG9zdGdyZXNxbCtwc3ljb3BnMjovL3dhdGNodG93ZXI6Q0hBTkdFX1RISVNfUEFTU1dPUkRAZGI6NTQzMi93YXRjaHRvd2Vy
  db-password: Q0hBTkdFX1RISVNfUEFTU1dPUkQ=
  api-key: eW91ci1zZWN1cmUtYXBpLWtleS1oZXJl
  admin-key: eW91ci1zZWN1cmUtYWRtaW4ta2V5LWhlcmU=
  llm-api-key: eW91ci1sbG0tYXBpLWtleS1oZXJl
"""
    
    with open('devops/secrets.yaml', 'w') as f:
        f.write(secrets_content)
    print("✅ Created Kubernetes secrets template")

def create_security_checklist():
    """Create a security checklist for deployment."""
    checklist_content = """# Security Deployment Checklist

## Pre-Deployment Security Tasks

### 🔴 Critical (Must Complete)
- [ ] Change all default passwords in .env file
- [ ] Generate secure API keys and admin keys
- [ ] Configure proper secrets management (Vault, K8s secrets, etc.)
- [ ] Complete authentication implementations in auth/ modules
- [ ] Implement TLS/HTTPS for all endpoints
- [ ] Configure proper CORS policies
- [ ] Set up rate limiting and DDoS protection

### 🟡 High Priority
- [ ] Implement proper RBAC and access controls
- [ ] Set up audit logging and monitoring
- [ ] Configure intrusion detection/prevention
- [ ] Implement proper session management
- [ ] Set up backup and disaster recovery
- [ ] Configure network segmentation

### 🟢 Medium Priority
- [ ] Perform security penetration testing
- [ ] Conduct code security review
- [ ] Set up vulnerability scanning
- [ ] Implement data encryption at rest
- [ ] Configure proper logging aggregation
- [ ] Set up security incident response procedures

## Post-Deployment Security Tasks

### Monitoring
- [ ] Set up security monitoring and alerting
- [ ] Configure log analysis and correlation
- [ ] Implement automated security scanning
- [ ] Set up compliance reporting

### Maintenance
- [ ] Regular security updates and patches
- [ ] Periodic security assessments
- [ ] Access review and cleanup
- [ ] Backup verification and testing

## Emergency Procedures
- [ ] Incident response plan documented
- [ ] Security team contacts established
- [ ] Rollback procedures tested
- [ ] Communication plan ready
"""
    
    with open('SECURITY_CHECKLIST.md', 'w') as f:
        f.write(checklist_content)
    print("✅ Created security deployment checklist")

def main():
    """Run all critical security fixes."""
    print("🔒 Applying Critical Security Fixes...")
    print("=" * 50)
    
    try:
        create_env_example()
        fix_docker_compose()
        fix_k8s_manifests()
        create_secrets_template()
        create_security_checklist()
        
        print("\n" + "=" * 50)
        print("✅ Critical security fixes applied successfully!")
        print("\n📋 Next Steps:")
        print("1. Copy .env.example to .env and update with secure values")
        print("2. Complete the security checklist in SECURITY_CHECKLIST.md")
        print("3. Review and update Kubernetes secrets in devops/secrets.yaml")
        print("4. Complete authentication implementations in auth/ modules")
        print("5. Implement proper monitoring and logging")
        
    except Exception as e:
        print(f"❌ Error applying security fixes: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 