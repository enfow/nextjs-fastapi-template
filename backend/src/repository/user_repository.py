"""
User repository for database operations.
"""

from typing import Optional
from sqlalchemy.orm import Session
from src.models.user import User
from src.repository.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    User repository with user-specific database operations.
    """

    def __init__(self):
        super().__init__(User)

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            db: Database session
            username: Username to search for

        Returns:
            Found user or None
        """
        return db.query(User).filter(User.username == username).first()

    def search_users(
        self, db: Session, search_term: str, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """
        Search users by username.

        Args:
            db: Database session
            search_term: Term to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching users
        """
        search_pattern = f"%{search_term}%"
        return (
            db.query(User)
            .filter(User.username.ilike(search_pattern))
            .offset(skip)
            .limit(limit)
            .all()
        )
