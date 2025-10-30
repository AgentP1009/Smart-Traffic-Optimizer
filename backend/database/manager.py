from .config import DatabaseConfig
from .postgres_db import test_postgres_connection, init_postgres_tables
from .mongo_db import test_mongo_connection

class DatabaseManager:
    def __init__(self):
        self.db_type = DatabaseConfig.DATABASE_TYPE
        self.is_connected = False
    
    async def initialize(self):
        """Initialize database connection based on configuration"""
        print(f"🔄 Initializing {self.db_type} database...")
        
        if self.db_type == "postgresql":
            success = await test_postgres_connection()
            if success:
                await init_postgres_tables()
                self.is_connected = True
                
        elif self.db_type == "mongodb":
            success = await test_mongo_connection()
            self.is_connected = success
            
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
        
        if self.is_connected:
            print(f"✅ {self.db_type.upper()} database initialized successfully!")
        else:
            print(f"❌ Failed to initialize {self.db_type} database!")
        
        return self.is_connected
    
    async def health_check(self):
        """Check database health"""
        if self.db_type == "postgresql":
            return await test_postgres_connection()
        elif self.db_type == "mongodb":
            return await test_mongo_connection()
        return False

# Global database manager instance
db_manager = DatabaseManager()