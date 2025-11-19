from typing import List, Optional, Union
from backend.database.config import DatabaseConfig
from backend.models.base import TrafficDataMongo, TrafficDataBase

if DatabaseConfig.DATABASE_TYPE == "mongodb":
    from backend.database.mongo_db import traffic_data_collection
    from bson import ObjectId

class TrafficCRUD:
    async def create_traffic_data(self, data: Union[TrafficDataBase, TrafficDataMongo]):
        if DatabaseConfig.DATABASE_TYPE == "mongodb":
            data_dict = data.dict(by_alias=True) if hasattr(data, 'dict') else data
            result = await traffic_data_collection.insert_one(data_dict)
            return str(result.inserted_id)
        else:
            # PostgreSQL implementation would go here
            pass
    
    async def get_traffic_data(self, data_id: str) -> Optional[TrafficDataMongo]:
        if DatabaseConfig.DATABASE_TYPE == "mongodb":
            if ObjectId.is_valid(data_id):
                data = await traffic_data_collection.find_one({"_id": ObjectId(data_id)})
                return TrafficDataMongo(**data) if data else None
        return None
    
    async def get_all_traffic_data(self) -> List[TrafficDataMongo]:
        if DatabaseConfig.DATABASE_TYPE == "mongodb":
            cursor = traffic_data_collection.find()
            return [TrafficDataMongo(**doc) async for doc in cursor]
        return []
    
    async def get_traffic_by_intersection(self, intersection_id: str) -> List[TrafficDataMongo]:
        if DatabaseConfig.DATABASE_TYPE == "mongodb":
            cursor = traffic_data_collection.find({"intersection_id": intersection_id})
            return [TrafficDataMongo(**doc) async for doc in cursor]
        return []

# Global CRUD instance
traffic_crud = TrafficCRUD()