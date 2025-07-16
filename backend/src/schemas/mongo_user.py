"""
MongoDB User Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MongoUserResponse(BaseModel):
    """
    Schema for MongoDB user response data.
    """

    id: str  # MongoDB ObjectId as string
    username: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # For Pydantic v2


class MongoUserListResponse(BaseModel):
    """
    Schema for paginated MongoDB user list response.
    """

    users: list[MongoUserResponse]
    total: int
    skip: int
    limit: int 