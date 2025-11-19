import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    # Database Type
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "mongodb")
    
    # PostgreSQL Configuration
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    
    # MongoDB Configuration
    MONGO_URL = os.getenv("MONGO_URL")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "smart_traffic_optimizer")
    
    @classmethod
    def validate_config(cls):
        if cls.DATABASE_TYPE == "postgresql" and not cls.POSTGRES_URL:
            raise ValueError("POSTGRES_URL is required when DATABASE_TYPE is postgresql")
        elif cls.DATABASE_TYPE == "mongodb" and not cls.MONGO_URL:
            raise ValueError("MONGO_URL is required when DATABASE_TYPE is mongodb")
        
        print(f"✅ Database configuration loaded: {cls.DATABASE_TYPE}")
        return True