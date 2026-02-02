#!/usr/bin/env python3
"""
Quick test script to verify EdgeLab components work
Run this before docker compose to catch issues early
"""

import sys
import subprocess
import os

def test_docker():
    """Check if Docker is installed and running"""
    print("Testing Docker installation...")
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ {result.stdout.strip()}")
            return True
        else:
            print("  ❌ Docker not working")
            return False
    except FileNotFoundError:
        print("  ❌ Docker not installed")
        return False

def test_docker_compose():
    """Check if docker compose is available"""
    print("Testing Docker Compose...")
    try:
        result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ {result.stdout.strip()}")
            return True
        else:
            print("  ❌ Docker Compose not working")
            return False
    except:
        print("  ❌ Docker Compose not available")
        return False

def test_python_version():
    """Check Python version"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ⚠️  Python {version.major}.{version.minor} (recommend 3.9+)")
        return True  # not critical

def test_assignment_files():
    """Check if assignment JSON files exist"""
    print("Testing assignment files...")
    required = [
        'assignments/python_two_sum.json',
        'assignments/sql_top_salaries.json', 
        'assignments/java_palindrome.json'
    ]
    
    all_exist = True
    for f in required:
        if os.path.exists(f):
            print(f"  ✅ {f}")
        else:
            print(f"  ❌ Missing: {f}")
            all_exist = False
    
    return all_exist

def test_python_imports():
    """Check if required Python packages can be imported"""
    print("Testing Python dependencies...")
    packages = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
    ]
    
    all_ok = True
    for module, name in packages:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ⚠️  {name} not installed (will be installed in Docker)")
            # Not critical since docker will install
    
    return True

def test_file_structure():
    """Check if required directories and files exist"""
    print("Testing file structure...")
    required = [
        'api/app.py',
        'api/database.py',
        'api/executor.py',
        'ui/streamlit_app.py',
        'docker-compose.yml',
        'Dockerfile.api',
        'Dockerfile.ui'
    ]
    
    all_exist = True
    for f in required:
        if os.path.exists(f):
            print(f"  ✅ {f}")
        else:
            print(f"  ❌ Missing: {f}")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 50)
    print("EdgeLab Pre-Flight Check")
    print("=" * 50)
    print()
    
    tests = [
        test_docker,
        test_docker_compose,
        test_python_version,
        test_file_structure,
        test_assignment_files,
        test_python_imports
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    print("=" * 50)
    if all(results):
        print("✅ All checks passed!")
        print()
        print("Ready to launch:")
        print("  docker compose up")
        print()
        return 0
    else:
        print("⚠️  Some checks failed")
        print()
        print("Critical issues must be fixed before running.")
        print("Warning issues will be handled by Docker.")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
