#!/usr/bin/env python3
"""
Dashboard Build Script
Builds the React dashboard frontend for production deployment.
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    """Build the dashboard frontend."""
    dashboard_dir = Path(__file__).parent.parent / "dashboard" / "frontend"
    
    if not dashboard_dir.exists():
        print("❌ Dashboard frontend directory not found!")
        print(f"Expected path: {dashboard_dir}")
        sys.exit(1)
    
    print("🚀 Building Watchtower Dashboard...")
    print(f"📁 Working directory: {dashboard_dir}")
    
    # Check if node_modules exists
    node_modules = dashboard_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Installing dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=dashboard_dir, check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("❌ npm not found. Please install Node.js and npm.")
            sys.exit(1)
    
    # Build the dashboard
    print("🔨 Building dashboard...")
    try:
        subprocess.run(["npm", "run", "build"], cwd=dashboard_dir, check=True)
        print("✅ Dashboard built successfully!")
        
        # Check if build directory exists
        build_dir = dashboard_dir / "build"
        if build_dir.exists():
            print(f"📁 Build output: {build_dir}")
            
            # List build contents
            index_html = build_dir / "index.html"
            if index_html.exists():
                print("✅ index.html found")
            else:
                print("⚠️  index.html not found in build output")
                
            static_dir = build_dir / "static"
            if static_dir.exists():
                print("✅ static/ directory found")
            else:
                print("⚠️  static/ directory not found in build output")
        else:
            print("❌ Build directory not found after build")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm.")
        sys.exit(1)
    
    print("\n🎉 Dashboard build completed!")
    print("📋 Next steps:")
    print("   1. Start the FastAPI backend: python main.py")
    print("   2. Visit http://localhost:5000/dashboard")
    print("   3. The dashboard will be served by the FastAPI backend")

if __name__ == "__main__":
    main() 