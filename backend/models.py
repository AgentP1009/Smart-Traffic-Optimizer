"""
Data models for Smart Traffic Optimizer - Pydantic v2 Compatible
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class TrafficData(BaseModel):
    id: Optional[int] = None
    intersection_id: str
    vehicle_count: int
    average_speed: float
    traffic_light_id: str
    timestamp: datetime = Field(default_factory=datetime.now)

    # Pydantic v2 config
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "intersection_id": "main_street_1",
                "vehicle_count": 25,
                "average_speed": 45.5,
                "traffic_light_id": "light_001"
            }
        }
    )

class TrafficDataResponse(TrafficData):
    """Response model with ID"""
    id: int

class DatabaseStatus(BaseModel):
    active_database: str
    sqlite: dict
    mongodb: dict
    config: dict

if __name__ == "__main__":
    # Test the model
    test_data = TrafficData(
        intersection_id="test_intersection",
        vehicle_count=10,
        average_speed=35.5,
        traffic_light_id="test_light"
    )
    print("✅ Model test passed")
    print(f"Sample data: {test_data.model_dump()}")