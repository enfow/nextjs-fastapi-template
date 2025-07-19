"""
MongoDB database configuration and connection management.
"""

import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import asyncio
from contextlib import asynccontextmanager

from src.models.mongo_user import MongoUser
from src.logging_config import get_database_logger


class MongoDBManager:
    """
    MongoDB connection and database manager.
    """
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.logger = get_database_logger()
        
    async def connect(self):
        """
        Connect to MongoDB database.
        """
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://admin:password123@localhost:27017/fastapi_db?authSource=admin")
        
        try:
            # Create client
            self.client = AsyncIOMotorClient(mongodb_url)
            
            # Get database
            self.database = self.client.fastapi_db
            
            # Test connection
            await self.client.admin.command('ping')
            self.logger.info("✅ Connected to MongoDB successfully!")
            
            # Initialize Beanie with document models
            await init_beanie(
                database=self.database,
                document_models=[MongoUser]
            )
            self.logger.info("✅ Beanie ODM initialized successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """
        Disconnect from MongoDB.
        """
        if self.client:
            self.client.close()
            self.logger.info("✅ Disconnected from MongoDB")
    
    async def ping(self):
        """
        Test MongoDB connection.
        """
        try:
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False


# Global MongoDB manager instance
mongodb_manager = MongoDBManager()


async def get_mongodb_client():
    """
    Get MongoDB client.
    """
    return mongodb_manager.client


async def get_mongodb_database():
    """
    Get MongoDB database.
    """
    return mongodb_manager.database


@asynccontextmanager
async def mongodb_lifespan():
    """
    Context manager for MongoDB lifecycle.
    """
    await mongodb_manager.connect()
    try:
        yield mongodb_manager
    finally:
        await mongodb_manager.disconnect() 