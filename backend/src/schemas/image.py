"""
Image Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ImageUploadRequest(BaseModel):
    """
    Schema for image upload request.
    """
    
    directory_name: str = Field(..., min_length=1, max_length=100, description="Directory name to store the image")
    description: Optional[str] = Field(None, max_length=500, description="Optional image description")


class ImageUploadResponse(BaseModel):
    """
    Schema for image upload response.
    """
    
    success: bool
    message: str
    file_name: str
    original_name: str
    directory_name: str
    file_size: int
    content_type: str
    url: str
    uploaded_at: datetime


class ImageListResponse(BaseModel):
    """
    Schema for image list response.
    """
    
    images: List[dict]
    total: int
    directory_name: str


class ImageDeleteResponse(BaseModel):
    """
    Schema for image deletion response.
    """
    
    success: bool
    message: str
    file_name: str
    directory_name: str


class DirectoryListResponse(BaseModel):
    """
    Schema for directory list response.
    """
    
    directories: List[dict]
    total: int


class ImageInfoResponse(BaseModel):
    """
    Schema for individual image information.
    """
    
    file_name: str
    original_name: str
    directory_name: str
    file_size: int
    content_type: str
    url: str
    last_modified: datetime
    etag: str 