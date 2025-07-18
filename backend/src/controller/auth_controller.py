"""
Authentication controller for handling HTTP requests related to user authentication.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import Optional

from src.service.mongo_auth_service import MongoAuthService
from src.schemas.auth import LoginRequest, LoginResponse


# Create router
router = APIRouter()

# Create service instance
auth_service = MongoAuthService()


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """
    Authenticate user and return access token.

    Args:
        login_data: Login credentials (username and password)

    Returns:
        Access token and user information

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        result = await auth_service.login(
            username=login_data.username,
            password=login_data.password
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return LoginResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/verify")
async def verify_token(authorization: Optional[str] = Header(None)):
    """
    Verify current user token (for token validation).
    This endpoint can be used by the frontend to verify if a token is still valid.

    Args:
        authorization: Authorization header with Bearer token

    Returns:
        User information if token is valid

    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    user = await auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {
        "user": {
            "id": str(user.id),
            "username": user.username,
            "name": user.username,
            "email": f"{user.username}@example.com"
        },
        "valid": True
    } 