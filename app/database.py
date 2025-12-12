from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from .config import get_settings

settings = get_settings()


class Database:
    client: Optional[AsyncIOMotorClient] = None

    @classmethod
    async def connect_db(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        print("Connected to MongoDB")

    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()
            print("Closed MongoDB connection")

    @classmethod
    def get_master_db(cls):
        return cls.client[settings.MASTER_DB_NAME]

    @classmethod
    def get_org_collection(cls, collection_name: str):
        return cls.client[settings.MASTER_DB_NAME][collection_name]


db = Database()
