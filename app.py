"""
Smart Traffic Optimizer - Simple Working Version
Uses Pydantic models properly with FastAPI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Import the working hybrid database
from backend.hybrid_database_final import hybrid_db

# Define proper Pydantic models for FastAPI
class TrafficData(BaseModel):
    intersection_id: str
    vehicle_count: int
    average_speed: float
    traffic_light_id: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class TrafficDataResponse(TrafficData):
    id: int

class DatabaseStatus(BaseModel):
    active_database: str
    sqlite: dict
    mongodb: dict
    config: dict

# Create FastAPI app
app = FastAPI(
    title="Smart Traffic Optimizer API",
    description="Real-time traffic data management system",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Starting Smart Traffic Optimizer API...")
    status = await hybrid_db.get_database_status()
    print(f"✅ Hybrid Database Active: {status['active_database'].upper()}")
    print(f"📊 SQLite: {status['sqlite']['status']}")
    print(f"🌐 MongoDB: {status['mongodb']['status']}")
    print(f"💡 Using {status['active_database']} for operations")

@app.get("/")
async def root():
    """Root endpoint with system info"""
    status = await hybrid_db.get_database_status()
    return {
        "message": "Smart Traffic Optimizer API",
        "version": "2.0.0",
        "status": "running",
        "database": {
            "active": status["active_database"],
            "sqlite": status["sqlite"]["status"],
            "mongodb": status["mongodb"]["status"]
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = await hybrid_db.get_database_status()
    return {
        "status": "healthy",
        "active_database": status["active_database"],
        "databases": {
            "sqlite": status["sqlite"]["status"],
            "mongodb": status["mongodb"]["status"]
        }
    }

@app.get("/database-status")
async def get_database_status():
    """Get detailed database status"""
    return await hybrid_db.get_database_status()

@app.post("/traffic-data/")
async def add_traffic_data(data: TrafficData):
    """Add new traffic data"""
    try:
        # Convert Pydantic model to our internal TrafficData
        from .hybrid_database_final import TrafficData as InternalTrafficData
        
        internal_data = InternalTrafficData(
            intersection_id=data.intersection_id,
            vehicle_count=data.vehicle_count,
            average_speed=data.average_speed,
            traffic_light_id=data.traffic_light_id,
            timestamp=data.timestamp
        )
        
        result = await hybrid_db.create_traffic_data(internal_data)
        return {
            "message": "Traffic data added successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add traffic data: {str(e)}")

@app.get("/traffic-data/")
async def get_traffic_data():
    """Get all traffic data"""
    try:
        data = await hybrid_db.get_all_traffic_data()
        stats = await hybrid_db.get_traffic_stats()
        
        # Convert internal data to response format
        response_data = []
        for item in data:
            response_data.append({
                "id": item.id,
                "intersection_id": item.intersection_id,
                "vehicle_count": item.vehicle_count,
                "average_speed": item.average_speed,
                "traffic_light_id": item.traffic_light_id,
                "timestamp": item.timestamp
            })
        
        return {
            "count": len(data),
            "stats": stats,
            "data": response_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get traffic data: {str(e)}")

@app.get("/traffic-data/intersection/{intersection_id}")
async def get_intersection_data(intersection_id: str):
    """Get traffic data for specific intersection"""
    try:
        data = await hybrid_db.get_traffic_by_intersection(intersection_id)
        
        # Convert internal data to response format
        response_data = []
        for item in data:
            response_data.append({
                "id": item.id,
                "intersection_id": item.intersection_id,
                "vehicle_count": item.vehicle_count,
                "average_speed": item.average_speed,
                "traffic_light_id": item.traffic_light_id,
                "timestamp": item.timestamp
            })
        
        return {
            "intersection_id": intersection_id,
            "count": len(data),
            "data": response_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get intersection data: {str(e)}")

@app.get("/stats")
async def get_statistics():
    """Get traffic statistics"""
    try:
        stats = await hybrid_db.get_traffic_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# Test endpoint
@app.get("/test-system")
async def test_system():
    """Test the entire system"""
    try:
        # Test data creation
        test_data = TrafficData(
            intersection_id="system_test",
            vehicle_count=99,
            average_speed=55.5,
            traffic_light_id="system_light"
        )
        
        # Convert to internal format
        from .hybrid_database_final import TrafficData as InternalTrafficData
        internal_data = InternalTrafficData(
            intersection_id=test_data.intersection_id,
            vehicle_count=test_data.vehicle_count,
            average_speed=test_data.average_speed,
            traffic_light_id=test_data.traffic_light_id
        )
        
        create_result = await hybrid_db.create_traffic_data(internal_data)
        all_data = await hybrid_db.get_all_traffic_data()
        stats = await hybrid_db.get_traffic_stats()
        status = await hybrid_db.get_database_status()
        
        return {
            "system": "operational",
            "test_data_created": create_result,
            "total_records": len(all_data),
            "statistics": stats,
            "database_status": status,
            "message": "✅ All systems operational"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System test failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)