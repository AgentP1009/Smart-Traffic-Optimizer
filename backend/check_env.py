"""
Check current environment configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

def check_env():
    print("🔍 Current Environment Configuration")
    print("=" * 50)
    
    # Check all relevant environment variables
    env_vars = {
        "DATABASE_TYPE": os.getenv("DATABASE_TYPE"),
        "MONGO_URL": os.getenv("MONGO_URL"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME"),
        "SQLITE_PATH": os.getenv("SQLITE_PATH")
    }
    
    for key, value in env_vars.items():
        status = "✅ Configured" if value else "❌ Missing"
        display_value = value if value else "Not set"
        
        # Hide MongoDB password for security
        if key == "MONGO_URL" and value:
            # Show only the first part of the URL
            display_value = value.split('@')[0] + "@***"
        
        print(f"{key:15} - {status}")
        print(f"   Value: {display_value}")
        print()

if __name__ == "__main__":
    check_env()