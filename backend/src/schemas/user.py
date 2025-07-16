"""
User Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    """
    Base User schema with common fields.
    """

    username: str


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """

    password: str


class UserUpdate(BaseModel):
    """
    Schema for updating a user.
    """

    username: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """
    Schema for user response data.
    """

    id: int

    class Config:
        from_attributes = True  # For Pydantic v2


class UserListResponse(BaseModel):
    """
    Schema for paginated user list response.
    """

    users: list[UserResponse]
    total: int
    skip: int
    limit: int
