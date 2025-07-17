"""
Authentication Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    """
    Schema for user login request.
    """
    username: str
    password: str


class LoginResponse(BaseModel):
    """
    Schema for login response.
    """
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserAuthInfo(BaseModel):
    """
    Schema for authenticated user information.
    """
    id: int
    username: str
    name: Optional[str] = None
    email: Optional[str] = None 