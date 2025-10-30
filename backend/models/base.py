from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Union
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class TrafficDataBase(BaseModel):
    intersection_id: str
    vehicle_count: int
    average_speed: float
    traffic_light_id: str
    timestamp: datetime = Field(default_factory=datetime.now)

class TrafficDataMongo(TrafficDataBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}