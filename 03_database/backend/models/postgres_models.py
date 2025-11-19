from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from backend.database.postgres_db import PostgresBase

class TrafficData(PostgresBase):
    __tablename__ = "traffic_data"
    
    id = Column(Integer, primary_key=True, index=True)
    intersection_id = Column(String, index=True)
    vehicle_count = Column(Integer)
    average_speed = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    traffic_light_id = Column(String)