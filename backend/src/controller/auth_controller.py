"""
Authentication controller for handling HTTP requests related to user authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..service.auth_service import AuthService
from ..schemas.auth import LoginRequest, LoginResponse


# Create router
router = APIRouter()

# Create service instance
auth_service = AuthService()


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.

    Args:
        login_data: Login credentials (username and password)
        db: Database session

    Returns:
        Access token and user information

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        result = auth_service.login(
            db=db,
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
async def verify_token(db: Session = Depends(get_db)):
    """
    Verify current user token (for token validation).
    This endpoint can be used by the frontend to verify if a token is still valid.

    Args:
        db: Database session

    Returns:
        User information if token is valid
    """
    # This would typically require authentication middleware
    # For now, returning a simple verification endpoint
    return {"message": "Token verification endpoint", "status": "available"} 