"""
MinIO client configuration and connection management.
"""

import os
from typing import Optional
from minio import Minio
from minio.error import S3Error
import asyncio
from contextlib import asynccontextmanager


class MinIOManager:
    """
    MinIO connection and client manager.
    """
    
    def __init__(self):
        self.client: Optional[Minio] = None
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "fastapi-images")
        
    def connect(self):
        """
        Connect to MinIO server.
        """
        endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
        secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        
        try:
            # Create MinIO client
            self.client = Minio(
                endpoint=endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )
            
            # Test connection
            self.client.list_buckets()
            print("✅ Connected to MinIO successfully!")
            
            # Create bucket if it doesn't exist
            self._ensure_bucket_exists()
            
        except Exception as e:
            print(f"❌ Failed to connect to MinIO: {e}")
            raise
    
    def _ensure_bucket_exists(self):
        """
        Ensure the default bucket exists.
        """
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"✅ Created bucket '{self.bucket_name}' successfully!")
            else:
                print(f"✅ Bucket '{self.bucket_name}' already exists")
        except S3Error as e:
            print(f"❌ Failed to create/check bucket: {e}")
            raise
    
    def get_client(self) -> Minio:
        """
        Get MinIO client.
        """
        if not self.client:
            raise RuntimeError("MinIO client not initialized. Call connect() first.")
        return self.client
    
    def ping(self) -> bool:
        """
        Test MinIO connection.
        """
        try:
            if self.client:
                self.client.list_buckets()
                return True
            return False
        except Exception:
            return False


# Global MinIO manager instance
minio_manager = MinIOManager()


def get_minio_client() -> Minio:
    """
    Get MinIO client.
    """
    return minio_manager.get_client()


def get_bucket_name() -> str:
    """
    Get the default bucket name.
    """
    return minio_manager.bucket_name


@asynccontextmanager
async def minio_lifespan():
    """
    Context manager for MinIO lifecycle.
    """
    minio_manager.connect()
    try:
        yield minio_manager
    finally:
        # MinIO client doesn't need explicit disconnection
        pass 