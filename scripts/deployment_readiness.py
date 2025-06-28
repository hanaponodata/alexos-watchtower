#!/usr/bin/env python3
"""
Deployment Readiness Assessment Script
Evaluates the current state of the Watchtower project for enterprise deployment.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class DeploymentReadinessChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
        self.score = 0
        self.max_score = 100
        
    def check_file_exists(self, filepath: str, critical: bool = False) -> bool:
        """Check if a file exists and record the result."""
        exists = os.path.exists(filepath)
        if exists:
            self.successes.append(f"✅ {filepath} exists")
            self.score += 2
        else:
            msg = f"❌ {filepath} missing"
            if critical:
                self.issues.append(msg)
                self.score -= 10
            else:
                self.warnings.append(msg)
                self.score -= 2
        return exists
    
    def check_security_issues(self):
        """Check for critical security issues."""
        print("🔒 Checking security...")
        
        # Check for hardcoded credentials
        files_to_check = [
            'docker-compose.yml',
            'devops/k8s.yaml',
            'devops/docker-compose.yml'
        ]
        
        for filepath in files_to_check:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Look for actual hardcoded passwords, not secretKeyRef keys
                    if ('m3t4ph0r' in content or 't3stpw' in content or 
                        'POSTGRES_PASSWORD: password' in content or
                        'POSTGRES_PASSWORD: watchtower' in content or
                        'value: password' in content or
                        'value: watchtower' in content):
                        self.issues.append(f"🔴 Hardcoded credentials found in {filepath}")
                        self.score -= 15
                    else:
                        self.successes.append(f"✅ No hardcoded credentials in {filepath}")
                        self.score += 5
        
        # Check for environment configuration
        if self.check_file_exists('.env.example'):
            self.successes.append("✅ Environment template exists")
            self.score += 3
        
        if not self.check_file_exists('.env'):
            self.warnings.append("⚠️  No .env file found (use .env.example as template)")
            self.score -= 2
    
    def check_infrastructure(self):
        """Check infrastructure readiness."""
        print("🏗️  Checking infrastructure...")
        
        # Docker
        if self.check_file_exists('devops/Dockerfile'):
            self.successes.append("✅ Dockerfile exists")
            self.score += 3
        
        if self.check_file_exists('docker-compose.yml'):
            self.successes.append("✅ Docker Compose exists")
            self.score += 3
        
        # Kubernetes
        if self.check_file_exists('devops/k8s.yaml'):
            self.successes.append("✅ Kubernetes manifests exist")
            self.score += 3
        
        if self.check_file_exists('devops/secrets.yaml'):
            self.successes.append("✅ Kubernetes secrets template exists")
            self.score += 2
        
        # CI/CD
        if self.check_file_exists('.github/workflows/ci.yml'):
            self.successes.append("✅ CI/CD pipeline exists")
            self.score += 3
    
    def check_database(self):
        """Check database configuration."""
        print("🗄️  Checking database...")
        
        # Check for migrations
        migrations_dir = 'database/migrations'
        if os.path.exists(migrations_dir):
            migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.py')]
            if migration_files:
                self.successes.append(f"✅ Database migrations exist ({len(migration_files)} files)")
                self.score += 5
            else:
                self.warnings.append("⚠️  No database migration files found")
                self.score -= 3
        else:
            self.warnings.append("⚠️  No migrations directory found")
            self.score -= 3
    
    def check_testing(self):
        """Check testing infrastructure."""
        print("🧪 Checking testing...")
        
        # Look for test files
        test_dirs = ['tests', 'test']
        test_files = []
        
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                for root, dirs, files in os.walk(test_dir):
                    test_files.extend([f for f in files if f.startswith('test_') or f.endswith('_test.py')])
        
        if test_files:
            self.successes.append(f"✅ Test files found ({len(test_files)} files)")
            self.score += 5
        else:
            self.warnings.append("⚠️  No test files found")
            self.score -= 5
    
    def check_documentation(self):
        """Check documentation."""
        print("📚 Checking documentation...")
        
        docs = [
            'README.md',
            'SECURITY_CHECKLIST.md',
            'ENTERPRISE_AUDIT_REPORT.md'
        ]
        
        for doc in docs:
            if self.check_file_exists(doc):
                self.score += 2
    
    def check_dependencies(self):
        """Check dependency management."""
        print("📦 Checking dependencies...")
        
        if self.check_file_exists('requirements.txt'):
            self.successes.append("✅ Requirements.txt exists")
            self.score += 2
        
        if self.check_file_exists('pyproject.toml'):
            self.successes.append("✅ PyProject.toml exists")
            self.score += 2
    
    def check_todo_items(self):
        """Check for incomplete TODO items."""
        print("📝 Checking TODO items...")
        
        todo_count = 0
        for root, dirs, files in os.walk('.'):
            if 'venv' in root or '__pycache__' in root:
                continue
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                            todos = content.count('TODO') + content.count('FIXME') + content.count('HACK')
                            todo_count += todos
                    except:
                        continue
        
        if todo_count == 0:
            self.successes.append("✅ No TODO items found")
            self.score += 3
        else:
            self.warnings.append(f"⚠️  {todo_count} TODO/FIXME/HACK items found")
            self.score -= todo_count
    
    def run_assessment(self) -> Dict:
        """Run the complete deployment readiness assessment."""
        print("🚀 Watchtower Deployment Readiness Assessment")
        print("=" * 50)
        
        self.check_security_issues()
        self.check_infrastructure()
        self.check_database()
        self.check_testing()
        self.check_documentation()
        self.check_dependencies()
        self.check_todo_items()
        
        # Calculate final score
        self.score = max(0, min(100, self.score))
        
        return {
            'score': self.score,
            'issues': self.issues,
            'warnings': self.warnings,
            'successes': self.successes
        }
    
    def print_report(self, results: Dict):
        """Print the assessment report."""
        print("\n" + "=" * 50)
        print("📊 DEPLOYMENT READINESS REPORT")
        print("=" * 50)
        
        # Overall score
        score = results['score']
        if score >= 80:
            status = "🟢 READY"
            recommendation = "Ready for deployment with minor improvements"
        elif score >= 60:
            status = "🟡 NEARLY READY"
            recommendation = "Address high-priority issues before deployment"
        elif score >= 40:
            status = "🟠 NEEDS WORK"
            recommendation = "Significant improvements needed before deployment"
        else:
            status = "🔴 NOT READY"
            recommendation = "Major issues must be resolved before deployment"
        
        print(f"Overall Score: {score}/100 - {status}")
        print(f"Recommendation: {recommendation}")
        
        # Critical issues
        if results['issues']:
            print(f"\n🔴 CRITICAL ISSUES ({len(results['issues'])}):")
            for issue in results['issues']:
                print(f"  {issue}")
        
        # Warnings
        if results['warnings']:
            print(f"\n⚠️  WARNINGS ({len(results['warnings'])}):")
            for warning in results['warnings']:
                print(f"  {warning}")
        
        # Successes
        if results['successes']:
            print(f"\n✅ SUCCESSES ({len(results['successes'])}):")
            for success in results['successes'][:10]:  # Show first 10
                print(f"  {success}")
            if len(results['successes']) > 10:
                print(f"  ... and {len(results['successes']) - 10} more")
        
        # Action items
        print(f"\n📋 IMMEDIATE ACTION ITEMS:")
        if results['issues']:
            print("  1. Fix all critical issues above")
        if results['warnings']:
            print("  2. Address warnings based on priority")
        print("  3. Complete security checklist in SECURITY_CHECKLIST.md")
        print("  4. Set up monitoring and alerting")
        print("  5. Perform security testing")
        
        return score

def main():
    """Main function."""
    checker = DeploymentReadinessChecker()
    results = checker.run_assessment()
    score = checker.print_report(results)
    
    # Exit with appropriate code
    if score >= 80:
        return 0
    elif score >= 60:
        return 1
    else:
        return 2

if __name__ == "__main__":
    exit(main()) 