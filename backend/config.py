"""
Smart Traffic Optimizer - Configuration Manager
Centralized configuration for database selection and settings
"""

import os
from dotenv import load_dotenv
from typing import Literal, Dict, Any

# Load environment variables
load_dotenv()

class DatabaseConfig:
    """Database configuration manager"""
    
    # Database selection (sqlite, mongodb, auto)
    DATABASE_TYPE: Literal["sqlite", "mongodb", "auto"] = os.getenv("DATABASE_TYPE", "auto")
    
    # SQLite configuration
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "traffic_data.db")
    SQLITE_ENABLED: bool = True  # Always enabled as fallback
    
    # MongoDB configuration
    MONGO_URL: str = os.getenv("MONGO_URL", "")
    MONGO_DB_NAME: str = os.getenv("DATABASE_NAME", "smart_traffic_optimizer")
    MONGO_ENABLED: bool = bool(MONGO_URL)
    
    # Auto-detection settings
    AUTO_PREFER_MONGO: bool = True  # Prefer MongoDB if available
    
    @classmethod
    def get_active_database(cls) -> str:
        """Determine which database to use based on configuration"""
        if cls.DATABASE_TYPE == "sqlite":
            return "sqlite"
        elif cls.DATABASE_TYPE == "mongodb":
            return "mongodb" if cls.MONGO_ENABLED else "sqlite"
        else:  # auto
            if cls.MONGO_ENABLED and cls.AUTO_PREFER_MONGO:
                return "mongodb"
            else:
                return "sqlite"
    
    @classmethod
    def get_config_status(cls) -> Dict[str, Any]:
        """Get current configuration status"""
        active_db = cls.get_active_database()
        
        return {
            "database_type": cls.DATABASE_TYPE,
            "active_database": active_db,
            "sqlite": {
                "enabled": cls.SQLITE_ENABLED,
                "path": cls.SQLITE_PATH,
                "status": "ready"
            },
            "mongodb": {
                "enabled": cls.MONGO_ENABLED,
                "url": cls.MONGO_URL[:20] + "..." if cls.MONGO_URL else "not configured",
                "database_name": cls.MONGO_DB_NAME,
                "status": "ready" if cls.MONGO_ENABLED else "disabled"
            },
            "recommendation": f"Using {active_db.upper()} database"
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate the current configuration"""
        if cls.DATABASE_TYPE not in ["sqlite", "mongodb", "auto"]:
            print(f"❌ Invalid DATABASE_TYPE: {cls.DATABASE_TYPE}")
            return False
        
        if cls.DATABASE_TYPE == "mongodb" and not cls.MONGO_ENABLED:
            print("❌ MongoDB selected but MONGO_URL not configured")
            return False
        
        print("✅ Configuration validated successfully")
        return True

class AppConfig:
    """Application configuration"""
    
    # API Settings
    API_TITLE: str = "Smart Traffic Optimizer API"
    API_VERSION: str = "2.1.0"
    API_DESCRIPTION: str = "Hybrid database traffic data management system"
    
    # Server Settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    # Feature Flags
    ENABLE_STATS: bool = True
    ENABLE_DELETE: bool = True
    ENABLE_HEALTH_CHECK: bool = True

# Configuration instances
db_config = DatabaseConfig
app_config = AppConfig

if __name__ == "__main__":
    # Test configuration
    print("🔧 Configuration Test")
    print("=" * 40)
    
    status = db_config.get_config_status()
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")
    
    print(f"\nActive database: {db_config.get_active_database()}")
    print(f"Configuration valid: {db_config.validate_config()}")