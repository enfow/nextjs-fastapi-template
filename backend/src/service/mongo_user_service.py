"""
MongoDB User service for business logic operations.
"""

from typing import Optional, List
from passlib.context import CryptContext
from src.models.mongo_user import MongoUser
from src.repository.mongo_repository import MongoRepository


class MongoUserService:
    """
    MongoDB User service with user-specific business logic.
    """

    def __init__(self):
        self.repository = MongoRepository(MongoUser)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create_user(self, user_data: dict) -> MongoUser:
        """
        Create a new user with validation and password hashing.

        Args:
            user_data: User data dictionary

        Returns:
            Created user

        Raises:
            ValueError: If validation fails
        """
        self._validate_create_data(user_data)
        
        # Check if username already exists
        if await self.repository.exists("username", user_data["username"]):
            raise ValueError("Username already exists")
        
        # Hash password before storing
        if "password" in user_data:
            user_data = user_data.copy()  # Don't modify original dict
            user_data["password"] = self.pwd_context.hash(user_data["password"])
        
        return await self.repository.create(user_data)

    async def get_user_by_id(self, user_id: str) -> Optional[MongoUser]:
        """
        Get user by ID.

        Args:
            user_id: User ID string

        Returns:
            Found user or None
        """
        return await self.repository.get_by_id(user_id)

    async def get_user_by_username(self, username: str) -> Optional[MongoUser]:
        """
        Get user by username.

        Args:
            username: Username to search for

        Returns:
            Found user or None
        """
        return await self.repository.find_by_field("username", username)

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[MongoUser]:
        """
        Get all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of users
        """
        return await self.repository.get_all(skip, limit)

    async def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> List[MongoUser]:
        """
        Search users.

        Args:
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching users
        """
        return await self.repository.search_by_regex("username", search_term, skip, limit)

    async def update_user(self, user_id: str, update_data: dict) -> Optional[MongoUser]:
        """
        Update user by ID.

        Args:
            user_id: User ID string
            update_data: Data to update

        Returns:
            Updated user or None if not found

        Raises:
            ValueError: If validation fails
        """
        self._validate_update_data(update_data)
        
        # Check if username already exists (for another user)
        if "username" in update_data:
            if await self.repository.exists("username", update_data["username"], exclude_id=user_id):
                raise ValueError("Username already exists")
        
        return await self.repository.update(user_id, update_data)

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete user by ID.

        Args:
            user_id: User ID string

        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(user_id)

    async def count_users(self) -> int:
        """
        Count total number of users.

        Returns:
            Total user count
        """
        return await self.repository.count()

    def _validate_create_data(self, data: dict) -> None:
        """
        Validate user creation data.

        Args:
            data: User data to validate

        Raises:
            ValueError: If validation fails
        """
        if not data.get("username"):
            raise ValueError("Username is required")

        if not data.get("password"):
            raise ValueError("Password is required")

        if len(data.get("username", "")) < 3:
            raise ValueError("Username must be at least 3 characters long")

        if len(data.get("password", "")) < 6:
            raise ValueError("Password must be at least 6 characters long")

    def _validate_update_data(self, data: dict) -> None:
        """
        Validate user update data.

        Args:
            data: User data to validate

        Raises:
            ValueError: If validation fails
        """
        if "username" in data and len(data["username"]) < 3:
            raise ValueError("Username must be at least 3 characters long")

        if "password" in data and len(data["password"]) < 6:
            raise ValueError("Password must be at least 6 characters long") 