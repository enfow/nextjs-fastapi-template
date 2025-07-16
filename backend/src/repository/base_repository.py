"""
Base Repository class providing common CRUD operations.
"""

from typing import Type, TypeVar, Generic, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta

# Generic type for database models
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class BaseRepository(Generic[ModelType]):
    """
    Base repository class with common CRUD operations.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize repository with model class.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    def create(self, db: Session, obj_data: dict) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            obj_data: Dictionary containing object data

        Returns:
            Created object
        """
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Get record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Found object or None
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get all records with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of objects
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def update(self, db: Session, id: int, obj_data: dict) -> Optional[ModelType]:
        """
        Update record by ID.

        Args:
            db: Database session
            id: Record ID
            obj_data: Dictionary containing updated data

        Returns:
            Updated object or None if not found
        """
        db_obj = self.get_by_id(db, id)
        if db_obj:
            for field, value in obj_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> bool:
        """
        Delete record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        db_obj = self.get_by_id(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False
