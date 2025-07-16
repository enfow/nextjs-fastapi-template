"""
MongoDB User controller for handling HTTP requests.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ..service.mongo_user_service import MongoUserService
from ..schemas.user import UserCreate, UserUpdate
from ..schemas.mongo_user import MongoUserResponse, MongoUserListResponse

# Create router
router = APIRouter()

# Create service instance
mongo_user_service = MongoUserService()


@router.post("/", response_model=MongoUserResponse, status_code=201)
async def create_user(user_data: UserCreate):
    """
    Create a new user in MongoDB.

    Args:
        user_data: User creation data

    Returns:
        Created user data

    Raises:
        HTTPException: If user already exists or validation fails
    """
    try:
        # Create user
        user = await mongo_user_service.create_user(user_data.dict())
        return MongoUserResponse(
            id=str(user.id),
            username=user.username,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=MongoUserListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of users to return"
    ),
    search: Optional[str] = Query(None, description="Search term for users"),
):
    """
    Get list of users from MongoDB with pagination and optional search.

    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        search: Optional search term

    Returns:
        Paginated list of users
    """
    try:
        if search:
            users = await mongo_user_service.search_users(search, skip, limit)
        else:
            users = await mongo_user_service.get_all_users(skip, limit)

        # Convert to response models
        user_responses = [
            MongoUserResponse(
                id=str(user.id),
                username=user.username,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]

        return MongoUserListResponse(
            users=user_responses, total=len(user_responses), skip=skip, limit=limit
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{user_id}", response_model=MongoUserResponse)
async def get_user(user_id: str):
    """
    Get user by ID from MongoDB.

    Args:
        user_id: User ID

    Returns:
        User data

    Raises:
        HTTPException: If user not found
    """
    user = await mongo_user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return MongoUserResponse(
        id=str(user.id),
        username=user.username,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.put("/{user_id}", response_model=MongoUserResponse)
async def update_user(user_id: str, user_data: UserUpdate):
    """
    Update user by ID in MongoDB.

    Args:
        user_id: User ID
        user_data: User update data

    Returns:
        Updated user data

    Raises:
        HTTPException: If user not found or validation fails
    """
    try:
        # Update user
        update_data = user_data.dict(exclude_unset=True)
        updated_user = await mongo_user_service.update_user(user_id, update_data)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")

        return MongoUserResponse(
            id=str(updated_user.id),
            username=updated_user.username,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str):
    """
    Delete user by ID from MongoDB.

    Args:
        user_id: User ID

    Raises:
        HTTPException: If user not found
    """
    success = await mongo_user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/username/{username}", response_model=MongoUserResponse)
async def get_user_by_username(username: str):
    """
    Get user by username from MongoDB.

    Args:
        username: Username

    Returns:
        User data

    Raises:
        HTTPException: If user not found
    """
    user = await mongo_user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return MongoUserResponse(
        id=str(user.id),
        username=user.username,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.get("/stats/count")
async def get_user_count():
    """
    Get total user count from MongoDB.

    Returns:
        Total user count
    """
    try:
        count = await mongo_user_service.count_users()
        return {"total_users": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") 