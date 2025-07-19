"""
Base Service class providing common business logic operations.
"""

from typing import Type, TypeVar, Generic, Optional, List
from sqlalchemy.orm import Session
from src.repository.base_repository import BaseRepository, ModelType

# Generic type for repositories
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[ModelType, RepositoryType]):
    """
    Base service class with common business logic operations.
    """

    def __init__(self, repository: RepositoryType):
        """
        Initialize service with repository.

        Args:
            repository: Repository instance
        """
        self.repository = repository

    def create_item(self, db: Session, item_data: dict) -> ModelType:
        """
        Create a new item with business logic validation.

        Args:
            db: Database session
            item_data: Dictionary containing item data

        Returns:
            Created item

        Raises:
            ValueError: If validation fails
        """
        # Add business logic validation here
        self._validate_create_data(item_data)
        return self.repository.create(db, item_data)

    def get_item_by_id(self, db: Session, item_id: int) -> Optional[ModelType]:
        """
        Get item by ID.

        Args:
            db: Database session
            item_id: Item ID

        Returns:
            Found item or None
        """
        return self.repository.get_by_id(db, item_id)

    def get_all_items(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get all items with pagination.

        Args:
            db: Database session
            skip: Number of items to skip
            limit: Maximum number of items to return

        Returns:
            List of items
        """
        return self.repository.get_all(db, skip, limit)

    def update_item(
        self, db: Session, item_id: int, item_data: dict
    ) -> Optional[ModelType]:
        """
        Update item with business logic validation.

        Args:
            db: Database session
            item_id: Item ID
            item_data: Dictionary containing updated data

        Returns:
            Updated item or None if not found

        Raises:
            ValueError: If validation fails
        """
        # Add business logic validation here
        self._validate_update_data(item_data)
        return self.repository.update(db, item_id, item_data)

    def delete_item(self, db: Session, item_id: int) -> bool:
        """
        Delete item.

        Args:
            db: Database session
            item_id: Item ID

        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(db, item_id)

    def _validate_create_data(self, data: dict) -> None:
        """
        Validate data for creation. Override in subclasses.

        Args:
            data: Data to validate

        Raises:
            ValueError: If validation fails
        """
        pass

    def _validate_update_data(self, data: dict) -> None:
        """
        Validate data for update. Override in subclasses.

        Args:
            data: Data to validate

        Raises:
            ValueError: If validation fails
        """
        pass
