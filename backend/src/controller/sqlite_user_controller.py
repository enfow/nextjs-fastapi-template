"""
SQLite User controller for handling HTTP requests.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.database import get_db
from src.service.sqlite_user_service import SQLiteUserService
from src.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse

# Create router
router = APIRouter()

# Create service instance
sqlite_user_service = SQLiteUserService()


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    Args:
        user_data: User creation data
        db: Database session

    Returns:
        Created user data

    Raises:
        HTTPException: If user already exists or validation fails
    """
    try:
        # Check if user already exists
        existing_user = sqlite_user_service.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        # Create user
        user = sqlite_user_service.create_user(db, user_data.dict())
        return UserResponse.from_orm(user)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of users to return"
    ),
    search: Optional[str] = Query(None, description="Search term for users"),
    db: Session = Depends(get_db),
):
    """
    Get list of users with pagination and optional search.

    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        search: Optional search term
        db: Database session

    Returns:
        Paginated list of users
    """
    try:
        if search:
            users = sqlite_user_service.search_users(db, search, skip, limit)
        else:
            users = sqlite_user_service.get_all_items(db, skip, limit)

        # Convert to response models
        user_responses = [UserResponse.from_orm(user) for user in users]

        return UserListResponse(
            users=user_responses, total=len(user_responses), skip=skip, limit=limit
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        User data

    Raises:
        HTTPException: If user not found
    """
    user = sqlite_user_service.get_item_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)
):
    """
    Update user by ID.

    Args:
        user_id: User ID
        user_data: User update data
        db: Database session

    Returns:
        Updated user data

    Raises:
        HTTPException: If user not found or validation fails
    """
    try:
        # Check if user exists
        existing_user = sqlite_user_service.get_item_by_id(db, user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check for username conflicts if updating it
        update_data = user_data.dict(exclude_unset=True)

        if "username" in update_data:
            username_exists = sqlite_user_service.get_user_by_username(
                db, update_data["username"]
            )
            if username_exists and username_exists.id != user_id:
                raise HTTPException(status_code=400, detail="Username already exists")

        # Update user
        updated_user = sqlite_user_service.update_item(db, user_id, update_data)
        return UserResponse.from_orm(updated_user)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete user by ID.

    Args:
        user_id: User ID
        db: Database session

    Raises:
        HTTPException: If user not found
    """
    success = sqlite_user_service.delete_item(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """
    Get user by username.

    Args:
        username: Username
        db: Database session

    Returns:
        User data

    Raises:
        HTTPException: If user not found
    """
    user = sqlite_user_service.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.from_orm(user) 