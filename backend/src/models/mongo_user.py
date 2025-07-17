"""
MongoDB User model using Beanie ODM.
"""

from typing import Optional
from beanie import Document
from pydantic import Field
from datetime import datetime


class MongoUser(Document):
    """
    MongoDB User document model.
    """
    
    username: str = Field(..., unique=True, min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "users"  # Collection name
        use_state_management = True
        
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "securepassword123",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    
    def __str__(self):
        return f"MongoUser(id={self.id}, username='{self.username}')"
    
    async def save_with_timestamp(self):
        """
        Save document with updated timestamp.
        """
        self.updated_at = datetime.utcnow()
        return await self.save() 