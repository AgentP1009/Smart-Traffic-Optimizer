from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import (
    test_connection, create_traffic_data, get_all_traffic_data, 
    get_traffic_by_intersection, get_traffic_stats, TrafficData
)

app = FastAPI(
    title="Smart Traffic Optimizer API",
    description="Real-time traffic data management with SQLite",
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
    connected = await test_connection()
    if connected:
        print("✅ SQLite database connected successfully!")
    else:
        print("❌ Database connection failed!")

@app.get("/")
async def root():
    return {
        "message": "Smart Traffic Optimizer API",
        "status": "running",
        "version": "2.0.0",
        "database": "SQLite",
        "description": "Real-time traffic data management system"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_healthy = await test_connection()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
        "service": "operational"
    }

@app.post("/traffic-data/")
async def add_traffic_data(data: TrafficData):
    """Add new traffic data"""
    try:
        data_id = await create_traffic_data(data)
        return {
            "message": "Traffic data added successfully",
            "id": data_id,
            "intersection_id": data.intersection_id,
            "timestamp": data.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add traffic data: {str(e)}")

@app.get("/traffic-data/")
async def get_traffic_data():
    """Get all traffic data"""
    try:
        data = await get_all_traffic_data()
        stats = await get_traffic_stats()
        return {
            "count": len(data),
            "stats": stats,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get traffic data: {str(e)}")

@app.get("/traffic-data/intersection/{intersection_id}")
async def get_intersection_data(intersection_id: str):
    """Get traffic data for specific intersection"""
    try:
        data = await get_traffic_by_intersection(intersection_id)
        return {
            "intersection_id": intersection_id,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get intersection data: {str(e)}")

@app.get("/stats")
async def get_statistics():
    """Get traffic statistics"""
    try:
        stats = await get_traffic_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.delete("/traffic-data/{data_id}")
async def delete_traffic_data(data_id: int):
    """Delete specific traffic data record"""
    try:
        from backend.database import get_db_connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM traffic_data WHERE id = ?', (data_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Traffic data not found")
                
        return {"message": "Traffic data deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete traffic data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)