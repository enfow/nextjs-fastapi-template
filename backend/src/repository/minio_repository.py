"""
Generic MinIO repository for object storage operations.
"""

import io
import os
from typing import List, Dict, Optional, BinaryIO
from datetime import datetime, timedelta
from minio import Minio
from minio.error import S3Error
from src.minio_client import get_minio_client, get_bucket_name


class MinIORepository:
    """
    Generic MinIO repository for object storage operations.
    """

    def __init__(self):
        self.bucket_name = get_bucket_name()

    def get_client(self) -> Minio:
        """Get MinIO client."""
        return get_minio_client()

    def upload_object(
        self, 
        object_name: str, 
        data: BinaryIO, 
        length: int, 
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Upload an object to MinIO.

        Args:
            object_name: Name of the object (includes path)
            data: Binary data to upload
            length: Size of the data
            content_type: MIME type of the object
            metadata: Optional metadata dictionary

        Returns:
            True if upload successful, False otherwise
        """
        try:
            client = self.get_client()
            client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=data,
                length=length,
                content_type=content_type,
                metadata=metadata or {}
            )
            return True
        except S3Error as e:
            print(f"Failed to upload object {object_name}: {e}")
            return False

    def download_object(self, object_name: str) -> Optional[bytes]:
        """
        Download an object from MinIO.

        Args:
            object_name: Name of the object to download

        Returns:
            Object data as bytes or None if not found
        """
        try:
            client = self.get_client()
            response = client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"Failed to download object {object_name}: {e}")
            return None

    def delete_object(self, object_name: str) -> bool:
        """
        Delete an object from MinIO.

        Args:
            object_name: Name of the object to delete

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            client = self.get_client()
            client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"Failed to delete object {object_name}: {e}")
            return False

    def object_exists(self, object_name: str) -> bool:
        """
        Check if an object exists in MinIO.

        Args:
            object_name: Name of the object to check

        Returns:
            True if object exists, False otherwise
        """
        try:
            client = self.get_client()
            client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False

    def list_objects(self, prefix: str = "", recursive: bool = True) -> List[Dict]:
        """
        List objects in MinIO with optional prefix filter.

        Args:
            prefix: Object name prefix to filter by
            recursive: Whether to list recursively

        Returns:
            List of object information dictionaries
        """
        try:
            client = self.get_client()
            objects = client.list_objects(
                self.bucket_name, 
                prefix=prefix, 
                recursive=recursive
            )
            
            result = []
            for obj in objects:
                result.append({
                    "object_name": obj.object_name,
                    "size": obj.size,
                    "etag": obj.etag,
                    "last_modified": obj.last_modified,
                    "content_type": obj.content_type,
                    "is_dir": obj.is_dir
                })
            
            return result
        except S3Error as e:
            print(f"Failed to list objects with prefix {prefix}: {e}")
            return []

    def get_object_info(self, object_name: str) -> Optional[Dict]:
        """
        Get detailed information about an object.

        Args:
            object_name: Name of the object

        Returns:
            Object information dictionary or None if not found
        """
        try:
            client = self.get_client()
            stat = client.stat_object(self.bucket_name, object_name)
            
            return {
                "object_name": stat.object_name,
                "size": stat.size,
                "etag": stat.etag,
                "last_modified": stat.last_modified,
                "content_type": stat.content_type,
                "metadata": stat.metadata,
                "version_id": stat.version_id
            }
        except S3Error as e:
            print(f"Failed to get object info for {object_name}: {e}")
            return None

    def generate_presigned_url(
        self, 
        object_name: str, 
        expires: timedelta = timedelta(hours=1),
        method: str = "GET"
    ) -> Optional[str]:
        """
        Generate a presigned URL for object access.

        Args:
            object_name: Name of the object
            expires: URL expiration time
            method: HTTP method (GET, PUT, etc.)

        Returns:
            Presigned URL or None if failed
        """
        try:
            client = self.get_client()
            
            # Use the correct MinIO client method based on HTTP method
            if method.upper() == "GET":
                url = client.presigned_get_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    expires=expires
                )
            elif method.upper() == "PUT":
                url = client.presigned_put_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    expires=expires
                )
            else:
                # For other methods, use the generic presigned_get_object as fallback
                url = client.presigned_get_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    expires=expires
                )
            
            return url
        except S3Error as e:
            print(f"Failed to generate presigned URL for {object_name}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error generating presigned URL for {object_name}: {e}")
            return None

    def copy_object(self, source_object: str, dest_object: str) -> bool:
        """
        Copy an object within MinIO.

        Args:
            source_object: Source object name
            dest_object: Destination object name

        Returns:
            True if copy successful, False otherwise
        """
        try:
            client = self.get_client()
            from minio.commonconfig import CopySource
            
            copy_source = CopySource(self.bucket_name, source_object)
            client.copy_object(self.bucket_name, dest_object, copy_source)
            return True
        except S3Error as e:
            print(f"Failed to copy object from {source_object} to {dest_object}: {e}")
            return False

    def get_bucket_policy(self) -> Optional[str]:
        """
        Get bucket policy.

        Returns:
            Bucket policy as JSON string or None
        """
        try:
            client = self.get_client()
            policy = client.get_bucket_policy(self.bucket_name)
            return policy
        except S3Error:
            return None

    def list_directories(self, prefix: str = "") -> List[str]:
        """
        List directories (common prefixes) in the bucket.

        Args:
            prefix: Prefix to filter by

        Returns:
            List of directory names
        """
        try:
            client = self.get_client()
            objects = client.list_objects(
                self.bucket_name, 
                prefix=prefix, 
                recursive=False
            )
            
            directories = set()
            for obj in objects:
                if obj.is_dir:
                    directories.add(obj.object_name.rstrip('/'))
                else:
                    # Extract directory from object path
                    parts = obj.object_name.split('/')
                    if len(parts) > 1:
                        directories.add(parts[0])
            
            return sorted(list(directories))
        except S3Error as e:
            print(f"Failed to list directories: {e}")
            return [] 