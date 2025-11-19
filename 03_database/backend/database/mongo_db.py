from motor.motor_asyncio import AsyncIOMotorClient
from .config import DatabaseConfig

# MongoDB setup
client = AsyncIOMotorClient(DatabaseConfig.MONGO_URL)
database = client[DatabaseConfig.DATABASE_NAME]

# Collections
traffic_data_collection = database.traffic_data
intersections_collection = database.intersections
analytics_collection = database.analytics

async def test_mongo_connection():
    try:
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # List collections to verify database access
        collections = await database.list_collection_names()
        print(f"Available collections: {collections}")
        
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def get_mongo_collection(collection_name: str):
    return database[collection_name]