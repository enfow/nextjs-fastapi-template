"""
SQLite User service for business logic operations.
"""

from typing import Optional
from sqlalchemy.orm import Session
from ..models.user import User
from ..repository.user_repository import UserRepository
from .base_service import BaseService


class SQLiteUserService(BaseService[User, UserRepository]):
    """
    SQLite User service with user-specific business logic.
    """

    def __init__(self):
        super().__init__(UserRepository())

    def create_user(self, db: Session, user_data: dict) -> User:
        """
        Create a new user with validation.

        Args:
            db: Database session
            user_data: User data dictionary

        Returns:
            Created user

        Raises:
            ValueError: If validation fails
        """
        return self.create_item(db, user_data)

    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            db: Database session
            username: Username to search for

        Returns:
            Found user or None
        """
        return self.repository.get_by_username(db, username)

    def search_users(
        self, db: Session, search_term: str, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """
        Search users.

        Args:
            db: Database session
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching users
        """
        return self.repository.search_users(db, search_term, skip, limit)

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