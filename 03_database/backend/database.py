import os
import sqlite3
from contextlib import contextmanager
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/traffic_optimizer?retryWrites=true&w=majority"
client = AsyncIOMotorClient(MONGO_URI)
db = client.traffic_optimizer  # database

load_dotenv()

# Database configuration
DATABASE_PATH = "traffic_data.db"

class TrafficData(BaseModel):
    id: Optional[int] = None
    intersection_id: str
    vehicle_count: int
    average_speed: float
    traffic_light_id: str
    timestamp: datetime = Field(default_factory=datetime.now)

# SQLite database setup
def init_database():
    """Initialize SQLite database and create tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create traffic data table
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
        
        # Create index for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_intersection_id 
            ON traffic_data(intersection_id)
        ''')
        
        conn.commit()
    print("✅ SQLite database initialized!")

@contextmanager
def get_db_connection():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    try:
        yield conn
    finally:
        conn.close()

async def test_connection():
    """Test database connection"""
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
        print("✅ SQLite database connected successfully!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def create_traffic_data(data: TrafficData) -> int:
    """Create new traffic data record"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO traffic_data 
            (intersection_id, vehicle_count, average_speed, traffic_light_id, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (data.intersection_id, data.vehicle_count, data.average_speed, 
              data.traffic_light_id, data.timestamp))
        
        conn.commit()
        return cursor.lastrowid

async def get_all_traffic_data() -> List[TrafficData]:
    """Get all traffic data"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM traffic_data ORDER BY timestamp DESC
        ''')
        
        rows = cursor.fetchall()
        data = []
        for row in rows:
            data.append(TrafficData(
                id=row['id'],
                intersection_id=row['intersection_id'],
                vehicle_count=row['vehicle_count'],
                average_speed=row['average_speed'],
                traffic_light_id=row['traffic_light_id'],
                timestamp=datetime.fromisoformat(row['timestamp'])
            ))
        return data

async def get_traffic_by_intersection(intersection_id: str) -> List[TrafficData]:
    """Get traffic data for specific intersection"""
    with get_db_connection() as conn:
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
                timestamp=datetime.fromisoformat(row['timestamp'])
            ))
        return data

async def get_traffic_stats():
    """Get traffic statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total records
        cursor.execute('SELECT COUNT(*) as total FROM traffic_data')
        total = cursor.fetchone()['total']
        
        # Unique intersections
        cursor.execute('SELECT COUNT(DISTINCT intersection_id) as intersections FROM traffic_data')
        intersections = cursor.fetchone()['intersections']
        
        # Average vehicle count
        cursor.execute('SELECT AVG(vehicle_count) as avg_vehicles FROM traffic_data')
        avg_vehicles = cursor.fetchone()['avg_vehicles'] or 0
        
        return {
            "total_records": total,
            "unique_intersections": intersections,
            "average_vehicles": round(avg_vehicles, 2)
        }

# Initialize database on import
init_database()