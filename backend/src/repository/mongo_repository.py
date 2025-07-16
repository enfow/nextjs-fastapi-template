"""
Generic MongoDB repository for database operations using Beanie ODM.
"""

from typing import Optional, List, TypeVar, Generic, Type, Dict, Any
from beanie import Document, PydanticObjectId


T = TypeVar('T', bound=Document)


class MongoRepository(Generic[T]):
    """
    Generic MongoDB repository with basic CRUD operations for any Beanie document.
    """

    def __init__(self, document_class: Type[T]):
        self.document_class = document_class

    async def create(self, data: dict) -> T:
        """
        Create a new document.

        Args:
            data: Document data dictionary

        Returns:
            Created document
        """
        document = self.document_class(**data)
        await document.insert()
        return document

    async def get_by_id(self, document_id: str) -> Optional[T]:
        """
        Get document by ID.

        Args:
            document_id: Document ID string

        Returns:
            Found document or None
        """
        try:
            return await self.document_class.get(PydanticObjectId(document_id))
        except Exception:
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Get all documents with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of documents
        """
        return await self.document_class.find_all().skip(skip).limit(limit).to_list()

    async def find_by_field(self, field_name: str, field_value: Any) -> Optional[T]:
        """
        Find document by a specific field.

        Args:
            field_name: Name of the field to search
            field_value: Value to search for

        Returns:
            Found document or None
        """
        query = {field_name: field_value}
        return await self.document_class.find_one(query)

    async def find_many_by_field(self, field_name: str, field_value: Any, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Find multiple documents by a specific field.

        Args:
            field_name: Name of the field to search
            field_value: Value to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching documents
        """
        query = {field_name: field_value}
        return await self.document_class.find(query).skip(skip).limit(limit).to_list()

    async def search_by_regex(self, field_name: str, search_term: str, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Search documents using regex pattern on a field.

        Args:
            field_name: Name of the field to search
            search_term: Term to search for (case-insensitive)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching documents
        """
        regex_pattern = {"$regex": search_term, "$options": "i"}
        query = {field_name: regex_pattern}
        return await self.document_class.find(query).skip(skip).limit(limit).to_list()

    async def update(self, document_id: str, update_data: dict) -> Optional[T]:
        """
        Update document by ID.

        Args:
            document_id: Document ID string
            update_data: Data to update

        Returns:
            Updated document or None if not found
        """
        document = await self.get_by_id(document_id)
        if not document:
            return None
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(document, key):
                setattr(document, key, value)
        
        # Update timestamp if the document has the method
        if hasattr(document, 'save_with_timestamp'):
            await document.save_with_timestamp()
        else:
            await document.save()
        
        return document

    async def delete(self, document_id: str) -> bool:
        """
        Delete document by ID.

        Args:
            document_id: Document ID string

        Returns:
            True if deleted, False if not found
        """
        document = await self.get_by_id(document_id)
        if not document:
            return False
        
        await document.delete()
        return True

    async def count(self) -> int:
        """
        Count total number of documents.

        Returns:
            Total document count
        """
        return await self.document_class.count()

    async def exists(self, field_name: str, field_value: Any, exclude_id: Optional[str] = None) -> bool:
        """
        Check if a document exists with a specific field value.

        Args:
            field_name: Name of the field to check
            field_value: Value to check for
            exclude_id: Document ID to exclude from check (for updates)

        Returns:
            True if document exists, False otherwise
        """
        query = {field_name: field_value}
        if exclude_id:
            query["_id"] = {"$ne": PydanticObjectId(exclude_id)}
        
        document = await self.document_class.find_one(query)
        return document is not None

    async def find_with_filter(self, filters: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[T]:
        """
        Find documents with custom filters.

        Args:
            filters: MongoDB query filters
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching documents
        """
        return await self.document_class.find(filters).skip(skip).limit(limit).to_list()

    async def delete_many(self, filters: Dict[str, Any]) -> int:
        """
        Delete multiple documents matching filters.

        Args:
            filters: MongoDB query filters

        Returns:
            Number of deleted documents
        """
        result = await self.document_class.find(filters).delete()
        return result.deleted_count if result else 0 