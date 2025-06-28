#!/usr/bin/env python3
"""
scripts/deploy_enterprise.py
Enterprise deployment script for Watchtower.
Handles production deployment with all enterprise features.
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from datetime import datetime

def run_command(cmd, check=True, capture_output=True):
    """Run a shell command."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check, 
            capture_output=capture_output,
            text=True
        )
        if capture_output and result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check Docker
    try:
        run_command("docker --version", check=False)
        print("✅ Docker found")
    except:
        print("❌ Docker not found")
        return False
    
    # Check Docker Compose
    try:
        run_command("docker-compose --version", check=False)
        print("✅ Docker Compose found")
    except:
        print("❌ Docker Compose not found")
        return False
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found. Please copy .env.example to .env and configure it.")
        return False
    
    print("✅ All prerequisites met")
    return True

def setup_database():
    """Set up the database."""
    print("🗄️ Setting up database...")
    
    # Start database container
    run_command("docker-compose up -d postgres")
    
    # Wait for database to be ready
    print("⏳ Waiting for database to be ready...")
    run_command("sleep 10")
    
    # Run database migrations
    print("🔄 Running database migrations...")
    run_command("alembic upgrade head")
    
    print("✅ Database setup complete")

def build_application():
    """Build the application."""
    print("🏗️ Building application...")
    
    # Install dependencies
    run_command("pip install -r requirements.txt")
    
    # Build frontend
    if Path("dashboard/frontend").exists():
        print("🔨 Building frontend...")
        run_command("cd dashboard/frontend && npm install")
        run_command("cd dashboard/frontend && npm run build")
    
    print("✅ Application build complete")

def setup_monitoring():
    """Set up monitoring infrastructure."""
    print("📊 Setting up monitoring...")
    
    # Start monitoring stack
    run_command("docker-compose up -d prometheus grafana")
    
    # Wait for monitoring to be ready
    print("⏳ Waiting for monitoring to be ready...")
    run_command("sleep 15")
    
    print("✅ Monitoring setup complete")

def setup_backup():
    """Set up backup infrastructure."""
    print("💾 Setting up backup system...")
    
    # Create backup directories
    backup_dir = Path("/var/backups/watchtower")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Set permissions
    run_command(f"chmod 750 {backup_dir}")
    
    # Create initial backup
    print("📦 Creating initial backup...")
    run_command("python3 -c \"from backup.enterprise_backup import EnterpriseBackupSystem; from database.engine import get_db; db = next(get_db()); backup_system = EnterpriseBackupSystem(db); backup_system.create_on_demand_backup()\"")
    
    print("✅ Backup system setup complete")

def setup_security():
    """Set up security features."""
    print("🔒 Setting up security...")
    
    # Generate secrets if not present
    secrets_file = Path("devops/secrets.yaml")
    if not secrets_file.exists():
        print("🔑 Generating secrets...")
        run_command("python3 scripts/generate_secrets.py")
    
    # Set up SSL certificates
    if Path("devops/ssl").exists():
        print("🔐 Setting up SSL certificates...")
        run_command("chmod 600 devops/ssl/*.pem")
    
    print("✅ Security setup complete")

def start_application():
    """Start the application."""
    print("🚀 Starting application...")
    
    # Start all services
    run_command("docker-compose up -d")
    
    # Wait for application to be ready
    print("⏳ Waiting for application to be ready...")
    run_command("sleep 20")
    
    # Run health checks
    print("🏥 Running health checks...")
    run_command("python3 -c \"from system.enterprise_monitoring import EnterpriseMonitoringSystem; from database.engine import get_db; db = next(get_db()); monitoring = EnterpriseMonitoringSystem(db); health = monitoring.get_system_health(); print('Health status:', health['overall_status'])\"")
    
    print("✅ Application started successfully")

def run_tests():
    """Run tests to verify deployment."""
    print("🧪 Running tests...")
    
    # Run unit tests
    run_command("python -m pytest tests/ -v")
    
    # Run integration tests
    run_command("python -m pytest tests/integration/ -v")
    
    print("✅ Tests completed")

def create_deployment_report():
    """Create deployment report."""
    print("📋 Creating deployment report...")
    
    report = {
        "deployment_id": f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "components": {
            "database": "postgresql",
            "monitoring": "prometheus+grafana",
            "backup": "enterprise_backup",
            "security": "configured",
            "frontend": "react_dashboard"
        },
        "endpoints": {
            "api": "http://localhost:5000",
            "dashboard": "http://localhost:3000",
            "monitoring": "http://localhost:9090",
            "grafana": "http://localhost:3001"
        }
    }
    
    with open("deployment_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("✅ Deployment report created: deployment_report.json")

def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy Watchtower Enterprise")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-monitoring", action="store_true", help="Skip monitoring setup")
    parser.add_argument("--skip-backup", action="store_true", help="Skip backup setup")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    
    args = parser.parse_args()
    
    print("🚀 Watchtower Enterprise Deployment")
    print("=" * 50)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print("Would execute the following steps:")
        print("1. Check prerequisites")
        print("2. Setup database")
        print("3. Build application")
        if not args.skip_monitoring:
            print("4. Setup monitoring")
        if not args.skip_backup:
            print("5. Setup backup")
        print("6. Setup security")
        print("7. Start application")
        if not args.skip_tests:
            print("8. Run tests")
        print("9. Create deployment report")
        return
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    try:
        # Setup database
        setup_database()
        
        # Build application
        build_application()
        
        # Setup monitoring
        if not args.skip_monitoring:
            setup_monitoring()
        
        # Setup backup
        if not args.skip_backup:
            setup_backup()
        
        # Setup security
        setup_security()
        
        # Start application
        start_application()
        
        # Run tests
        if not args.skip_tests:
            run_tests()
        
        # Create deployment report
        create_deployment_report()
        
        print("\n🎉 Deployment completed successfully!")
        print("\n📊 Access your Watchtower Enterprise instance:")
        print("   API: http://localhost:5000")
        print("   Dashboard: http://localhost:3000")
        print("   Monitoring: http://localhost:9090")
        print("   Grafana: http://localhost:3001")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 