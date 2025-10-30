"""
Smart Traffic Optimizer - Requirements & Environment Check
Checks if all required packages are installed and environment is properly set up
"""

import sys
import sqlite3
import os
from dotenv import load_dotenv

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("   ✅ Python version compatible")
        return True
    else:
        print("   ❌ Python 3.8+ required")
        return False

def check_required_packages():
    """Check if all required packages are installed"""
    print("\n📦 Checking required packages...")
    
    required_packages = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "pydantic": "Pydantic",
        "python-dotenv": "python-dotenv",
        "sqlite3": "SQLite3 (built-in)",
    }
    
    # Optional packages for MongoDB
    optional_packages = {
        "motor": "Motor (MongoDB async driver)",
        "pymongo": "PyMongo",
        "dnspython": "DNS Python (for MongoDB SRV)"
    }
    
    all_required_ok = True
    installed_optional = []
    
    for package, description in required_packages.items():
        try:
            if package == "sqlite3":
                # SQLite is built-in
                print(f"   ✅ {description:25} - Installed")
            else:
                __import__(package)
                print(f"   ✅ {description:25} - Installed")
        except ImportError:
            print(f"   ❌ {description:25} - Missing")
            all_required_ok = False
    
    print("\n🔧 Checking optional packages (for MongoDB)...")
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"   ✅ {description:25} - Installed")
            installed_optional.append(package)
        except ImportError:
            print(f"   ⚠️  {description:25} - Missing (MongoDB will not work)")
    
    return all_required_ok, installed_optional

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    load_dotenv()
    
    env_checks = {
        "DATABASE_TYPE": os.getenv("DATABASE_TYPE", "sqlite"),
        "MONGO_URL": os.getenv("MONGO_URL"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME", "smart_traffic_optimizer"),
    }
    
    env_ok = True
    
    for key, value in env_checks.items():
        if value:
            if key == "MONGO_URL" and "mongodb" in value:
                print(f"   ✅ {key:20} - Configured")
            else:
                print(f"   ✅ {key:20} - {value}")
        else:
            if key == "MONGO_URL":
                print(f"   ⚠️  {key:20} - Not configured (MongoDB disabled)")
            else:
                print(f"   ✅ {key:20} - Using default: {value}")
    
    return env_ok

def check_sqlite():
    """Check SQLite functionality"""
    print("\n💾 Checking SQLite database...")
    try:
        # Test SQLite connection and basic operations
        conn = sqlite3.connect(":memory:")  # Use in-memory database for testing
        cursor = conn.cursor()
        
        # Test table creation
        cursor.execute("""
            CREATE TABLE test_traffic_data (
                id INTEGER PRIMARY KEY,
                intersection_id TEXT,
                vehicle_count INTEGER
            )
        """)
        
        # Test insert
        cursor.execute("INSERT INTO test_traffic_data (intersection_id, vehicle_count) VALUES (?, ?)", 
                      ("test_intersection", 10))
        
        # Test select
        cursor.execute("SELECT * FROM test_traffic_data")
        results = cursor.fetchall()
        
        conn.close()
        
        print("   ✅ SQLite database operational")
        print("   ✅ Basic CRUD operations working")
        return True
        
    except Exception as e:
        print(f"   ❌ SQLite test failed: {e}")
        return False

def check_file_permissions():
    """Check file and directory permissions"""
    print("\n📁 Checking file permissions...")
    
    required_dirs = ["backend", "data"]
    required_files = ["backend/main.py", "backend/database.py", ".env"]
    
    all_ok = True
    
    for directory in required_dirs:
        if os.path.exists(directory) and os.path.isdir(directory):
            print(f"   ✅ Directory '{directory}' exists")
        else:
            print(f"   ⚠️  Directory '{directory}' missing (will be created if needed)")
    
    for file in required_files:
        if os.path.exists(file):
            # Check if readable
            if os.access(file, os.R_OK):
                print(f"   ✅ File '{file}' readable")
            else:
                print(f"   ❌ File '{file}' not readable")
                all_ok = False
        else:
            if file == ".env":
                print(f"   ⚠️  File '{file}' missing (will use defaults)")
            else:
                print(f"   ❌ File '{file}' missing")
                all_ok = False
    
    return all_ok

def generate_requirements():
    """Generate requirements.txt content"""
    print("\n📄 Generating requirements.txt...")
    
    requirements = """fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
python-dotenv>=1.0.0
motor>=3.3.0
pymongo>=4.5.0
dnspython>=2.4.0
"""
    
    try:
        with open("requirements.txt", "w") as f:
            f.write(requirements)
        print("   ✅ requirements.txt generated")
        return True
    except Exception as e:
        print(f"   ❌ Failed to generate requirements.txt: {e}")
        return False

def main():
    print("🚦 Smart Traffic Optimizer - System Check")
    print("=" * 50)
    
    # Run all checks
    python_ok = check_python_version()
    packages_ok, optional_packages = check_required_packages()
    env_ok = check_environment()
    sqlite_ok = check_sqlite()
    files_ok = check_file_permissions()
    requirements_ok = generate_requirements()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CHECK SUMMARY")
    print("=" * 50)
    
    checks = {
        "Python Version": python_ok,
        "Required Packages": packages_ok,
        "Environment": env_ok,
        "SQLite Database": sqlite_ok,
        "File Permissions": files_ok,
        "Requirements File": requirements_ok,
    }
    
    all_passed = all(checks.values())
    
    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {check:25} - {status}")
    
    print(f"\n   Optional MongoDB packages: {len(optional_packages)}/3 installed")
    
    if all_passed:
        print("\n🎉 ALL CHECKS PASSED! System is ready.")
        print("   You can run: python -m uvicorn backend.main:app --reload")
    else:
        print("\n⚠️  SOME CHECKS FAILED!")
        print("   Please fix the issues above before running the application")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if "motor" not in optional_packages:
        print("   - Install MongoDB packages: pip install motor pymongo dnspython")
    if not os.getenv("MONGO_URL"):
        print("   - Configure MONGO_URL in .env file for MongoDB support")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)