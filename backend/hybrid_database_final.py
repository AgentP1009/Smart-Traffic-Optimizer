"""
Smart Traffic Optimizer - Hybrid Database System FINAL VERSION
Handles both SQLite and MongoDB with automatic fallback
"""

import os
import sys
import sqlite3
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add the parent directory to path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import configuration
try:
    from backend.config import db_config
    print("✅ Configuration imported successfully")
except ImportError as e:
    print(f"❌ Config import failed: {e}")
    sys.exit(1)

# Define TrafficData model
class TrafficData:
    """Traffic Data Model"""
    def __init__(self, intersection_id: str, vehicle_count: int, average_speed: float, 
                 traffic_light_id: str, timestamp: datetime = None, id: Optional[int] = None):
        self.id = id
        self.intersection_id = intersection_id
        self.vehicle_count = vehicle_count
        self.average_speed = average_speed
        self.traffic_light_id = traffic_light_id
        self.timestamp = timestamp or datetime.now()
    
    def dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "intersection_id": self.intersection_id,
            "vehicle_count": self.vehicle_count,
            "average_speed": self.average_speed,
            "traffic_light_id": self.traffic_light_id,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            id=data.get('id'),
            intersection_id=data['intersection_id'],
            vehicle_count=data['vehicle_count'],
            average_speed=data['average_speed'],
            traffic_light_id=data['traffic_light_id'],
            timestamp=data.get('timestamp', datetime.now())
        )

class SQLiteManager:
    """SQLite database manager"""
    
    def __init__(self):
        self.db_path = db_config.SQLITE_PATH
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS traffic_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    intersection_id TEXT NOT NULL,
                    vehicle_count INTEGER NOT NULL,
                    average_speed REAL NOT NULL,
                    traffic_light_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_intersection_id 
                ON traffic_data(intersection_id)
            ''')
            
            conn.commit()
        print("✅ SQLite database initialized")
    
    @contextmanager
    def get_connection(self):
        """Database connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _parse_timestamp(self, timestamp_str):
        """Parse timestamp string safely"""
        try:
            if 'T' in timestamp_str:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                if '.' in timestamp_str:
                    parts = timestamp_str.split('.')
                    base_time = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
                    microseconds = int(parts[1][:6].ljust(6, '0'))
                    return base_time.replace(microsecond=microseconds)
                else:
                    return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"⚠️  Timestamp parsing failed: {e}")
            return datetime.now()
    
    async def create_traffic_data(self, data: TrafficData) -> int:
        """Create traffic data in SQLite"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO traffic_data 
                (intersection_id, vehicle_count, average_speed, traffic_light_id, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data.intersection_id, 
                data.vehicle_count, 
                data.average_speed, 
                data.traffic_light_id, 
                data.timestamp.isoformat()
            ))
            conn.commit()
            return cursor.lastrowid
    
    async def get_all_traffic_data(self) -> List[TrafficData]:
        """Get all traffic data from SQLite"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM traffic_data ORDER BY timestamp DESC')
            rows = cursor.fetchall()
            
            data = []
            for row in rows:
                data.append(TrafficData(
                    id=row['id'],
                    intersection_id=row['intersection_id'],
                    vehicle_count=row['vehicle_count'],
                    average_speed=row['average_speed'],
                    traffic_light_id=row['traffic_light_id'],
                    timestamp=self._parse_timestamp(row['timestamp'])
                ))
            return data
    
    async def get_traffic_by_intersection(self, intersection_id: str) -> List[TrafficData]:
        """Get traffic data for specific intersection"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM traffic_data 
                WHERE intersection_id = ? 
                ORDER BY timestamp DESC
            ''', (intersection_id,))
            rows = cursor.fetchall()
            
            data = []
            for row in rows:
                data.append(TrafficData(
                    id=row['id'],
                    intersection_id=row['intersection_id'],
                    vehicle_count=row['vehicle_count'],
                    average_speed=row['average_speed'],
                    traffic_light_id=row['traffic_light_id'],
                    timestamp=self._parse_timestamp(row['timestamp'])
                ))
            return data
    
    async def get_traffic_stats(self) -> Dict[str, Any]:
        """Get traffic statistics from SQLite"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as total FROM traffic_data')
            total = cursor.fetchone()['total']
            
            cursor.execute('SELECT COUNT(DISTINCT intersection_id) as intersections FROM traffic_data')
            intersections = cursor.fetchone()['intersections']
            
            cursor.execute('SELECT AVG(vehicle_count) as avg_vehicles FROM traffic_data')
            avg_vehicles = cursor.fetchone()['avg_vehicles'] or 0
            
            cursor.execute('SELECT AVG(average_speed) as avg_speed FROM traffic_data')
            avg_speed = cursor.fetchone()['avg_speed'] or 0
            
            return {
                "total_records": total,
                "unique_intersections": intersections,
                "average_vehicles": round(avg_vehicles, 2),
                "average_speed": round(avg_speed, 2)
            }

class MongoDBManager:
    """MongoDB database manager"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False
        self._init_database()
    
    def _init_database(self):
        """Initialize MongoDB connection"""
        if not db_config.MONGO_ENABLED:
            print("⚠️  MongoDB disabled - URL not configured")
            return
        
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            self.client = AsyncIOMotorClient(
                db_config.MONGO_URL, 
                serverSelectionTimeoutMS=10000
            )
            self.db = self.client[db_config.MONGO_DB_NAME]
            self.collection = self.db.traffic_data
            self.connected = True
            print("✅ MongoDB client initialized")
            
        except Exception as e:
            print(f"⚠️  MongoDB connection failed: {e}")
            self.connected = False
    
    async def test_connection(self) -> bool:
        """Test MongoDB connection"""
        if not self.connected:
            return False
        
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            print(f"   ❌ MongoDB connection test failed: {e}")
            self.connected = False
            return False
    
    async def create_traffic_data(self, data: TrafficData) -> str:
        """Create traffic data in MongoDB"""
        if not await self.test_connection():
            raise Exception("MongoDB not connected")
        
        data_dict = data.dict()
        if data.id:
            data_dict['sqlite_id'] = data.id
        
        result = await self.collection.insert_one(data_dict)
        return str(result.inserted_id)
    
    async def get_all_traffic_data(self) -> List[TrafficData]:
        """Get all traffic data from MongoDB"""
        if not await self.test_connection():
            raise Exception("MongoDB not connected")
        
        cursor = self.collection.find().sort("timestamp", -1)
        data = []
        async for document in cursor:
            data.append(TrafficData.from_dict(document))
        return data

class HybridDatabase:
    """
    Hybrid Database Manager
    Uses configuration to determine which database to use
    """
    
    def __init__(self):
        self.sqlite = SQLiteManager()
        self.mongodb = MongoDBManager()
        self.active_db = db_config.get_active_database()
        
        print(f"🎯 Hybrid Database initialized")
        print(f"   Active database: {self.active_db.upper()}")
        print(f"   SQLite: {'✅ Enabled' if db_config.SQLITE_ENABLED else '❌ Disabled'}")
        print(f"   MongoDB: {'✅ Connected' if self.mongodb.connected else '❌ Disconnected'}")
    
    async def get_database_status(self) -> Dict[str, Any]:
        """Get status of all databases"""
        mongo_connected = await self.mongodb.test_connection()
        
        return {
            "active_database": self.active_db,
            "sqlite": {
                "enabled": db_config.SQLITE_ENABLED,
                "status": "connected"
            },
            "mongodb": {
                "enabled": db_config.MONGO_ENABLED,
                "connected": mongo_connected,
                "status": "connected" if mongo_connected else "disconnected"
            }
        }
    
    async def create_traffic_data(self, data: TrafficData) -> Dict[str, Any]:
        """Create traffic data using active database"""
        result = {
            "database_used": self.active_db,
            "data_id": None,
            "details": {}
        }
        
        try:
            mongo_available = await self.mongodb.test_connection()
            
            if self.active_db == "mongodb" and mongo_available:
                print("   🚀 Using MongoDB...")
                try:
                    mongo_id = await self.mongodb.create_traffic_data(data)
                    result["data_id"] = mongo_id
                    result["details"]["mongodb_id"] = mongo_id
                except Exception as mongo_error:
                    print(f"   ❌ MongoDB failed: {mongo_error}")
                    # Fall back to SQLite
                    sqlite_id = await self.sqlite.create_traffic_data(data)
                    result["database_used"] = "sqlite"
                    result["data_id"] = sqlite_id
                    result["details"]["fallback_sqlite_id"] = sqlite_id
                    
            else:
                print("   💾 Using SQLite...")
                sqlite_id = await self.sqlite.create_traffic_data(data)
                result["data_id"] = sqlite_id
                result["details"]["sqlite_id"] = sqlite_id
            
            return result
            
        except Exception as e:
            print(f"   ❌ Primary database failed: {e}")
            # Ultimate fallback - always try SQLite
            try:
                sqlite_id = await self.sqlite.create_traffic_data(data)
                result["database_used"] = "sqlite"
                result["data_id"] = sqlite_id
                result["details"]["fallback_sqlite_id"] = sqlite_id
                return result
            except Exception as fallback_error:
                raise Exception(f"All databases failed: {fallback_error}")
    
    async def get_all_traffic_data(self) -> List[TrafficData]:
        """Get all traffic data from active database"""
        try:
            mongo_available = await self.mongodb.test_connection()
            
            if self.active_db == "mongodb" and mongo_available:
                return await self.mongodb.get_all_traffic_data()
            else:
                return await self.sqlite.get_all_traffic_data()
        except Exception as e:
            print(f"⚠️  Active database failed, falling back to SQLite: {e}")
            return await self.sqlite.get_all_traffic_data()
    
    async def get_traffic_by_intersection(self, intersection_id: str) -> List[TrafficData]:
        """Get intersection data from active database"""
        try:
            mongo_available = await self.mongodb.test_connection()
            
            if self.active_db == "mongodb" and mongo_available:
                return await self.mongodb.get_traffic_by_intersection(intersection_id)
            else:
                return await self.sqlite.get_traffic_by_intersection(intersection_id)
        except Exception as e:
            print(f"⚠️  Active database failed, falling back to SQLite: {e}")
            return await self.sqlite.get_traffic_by_intersection(intersection_id)
    
    async def get_traffic_stats(self) -> Dict[str, Any]:
        """Get traffic statistics (always from SQLite for consistency)"""
        return await self.sqlite.get_traffic_stats()

# Global instance
hybrid_db = HybridDatabase()

# Test function
async def test_hybrid_database():
    """Test the hybrid database system"""
    print("\n🧪 Testing Hybrid Database System")
    print("=" * 50)
    
    status = await hybrid_db.get_database_status()
    print("Database Status:")
    print(f"  Active: {status['active_database'].upper()}")
    print(f"  SQLite: {status['sqlite']['status']}")
    print(f"  MongoDB: {status['mongodb']['status']}")
    
    test_data = TrafficData(
        intersection_id="test_intersection",
        vehicle_count=42,
        average_speed=38.5,
        traffic_light_id="test_light"
    )
    
    print(f"\n📝 Testing data creation...")
    result = await hybrid_db.create_traffic_data(test_data)
    print(f"✅ Creation result:")
    print(f"   Database used: {result['database_used']}")
    
    print("\n📊 Testing data retrieval...")
    all_data = await hybrid_db.get_all_traffic_data()
    print(f"✅ Retrieved {len(all_data)} records")
    
    return result

if __name__ == "__main__":
    import asyncio
    print("🚀 Starting Hybrid Database Test...")
    asyncio.run(test_hybrid_database())