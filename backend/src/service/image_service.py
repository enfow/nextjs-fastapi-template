"""
Image service for business logic operations.
"""

import io
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from fastapi import UploadFile
from PIL import Image
import os

from src.repository.minio_repository import MinIORepository


class ImageService:
    """
    Image service with image-specific business logic.
    """

    def __init__(self):
        self.repository = MinIORepository()
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    async def upload_image(
        self, 
        file: UploadFile, 
        directory_name: str, 
        description: Optional[str] = None
    ) -> Dict:
        """
        Upload an image with validation and duplicate checking.

        Args:
            file: Uploaded file
            directory_name: Directory to store the image
            description: Optional description

        Returns:
            Upload result dictionary

        Raises:
            ValueError: If validation fails
        """
        # Validate file
        self._validate_file(file)
        
        # Sanitize directory name
        directory_name = self._sanitize_directory_name(directory_name)
        
        # Generate unique filename
        original_name = file.filename
        file_extension = self._get_file_extension(original_name)
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        object_name = f"{directory_name}/{unique_filename}"
        
        # Check for duplicate original filename in the same directory
        if await self._check_duplicate_name(directory_name, original_name):
            raise ValueError(f"File with name '{original_name}' already exists in directory '{directory_name}'")
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate image and get metadata
        image_info = self._validate_and_process_image(file_content, file.content_type)
        
        # Prepare metadata
        metadata = {
            "original_name": original_name,
            "directory_name": directory_name,
            "description": description or "",
            "uploaded_at": datetime.utcnow().isoformat(),
            "image_width": str(image_info["width"]),
            "image_height": str(image_info["height"]),
            "image_format": image_info["format"]
        }
        
        # Upload to MinIO
        file_stream = io.BytesIO(file_content)
        success = self.repository.upload_object(
            object_name=object_name,
            data=file_stream,
            length=file_size,
            content_type=file.content_type,
            metadata=metadata
        )
        
        if not success:
            raise RuntimeError("Failed to upload image to storage")
        
        # Generate public URL (presigned URL for now)
        url = self.repository.generate_presigned_url(object_name)
        
        return {
            "success": True,
            "message": "Image uploaded successfully",
            "file_name": unique_filename,
            "original_name": original_name,
            "directory_name": directory_name,
            "file_size": file_size,
            "content_type": file.content_type,
            "url": url or f"/api/images/{directory_name}/{unique_filename}",
            "uploaded_at": datetime.utcnow(),
            "image_info": image_info
        }

    async def get_images_in_directory(self, directory_name: str) -> List[Dict]:
        """
        Get all images in a specific directory.

        Args:
            directory_name: Directory name

        Returns:
            List of image information
        """
        directory_name = self._sanitize_directory_name(directory_name)
        prefix = f"{directory_name}/"
        
        objects = self.repository.list_objects(prefix=prefix, recursive=False)
        
        images = []
        for obj in objects:
            if not obj["is_dir"]:
                # Get object metadata
                info = self.repository.get_object_info(obj["object_name"])
                if info:
                    metadata = info.get("metadata", {})
                    url = self.repository.generate_presigned_url(obj["object_name"])
                    
                    images.append({
                        "file_name": os.path.basename(obj["object_name"]),
                        "original_name": metadata.get("original_name", ""),
                        "directory_name": directory_name,
                        "file_size": obj["size"],
                        "content_type": info["content_type"],
                        "url": url or f"/api/images/{obj['object_name']}",
                        "last_modified": obj["last_modified"],
                        "etag": obj["etag"],
                        "description": metadata.get("description", ""),
                        "image_width": metadata.get("image_width", ""),
                        "image_height": metadata.get("image_height", ""),
                        "image_format": metadata.get("image_format", "")
                    })
        
        return sorted(images, key=lambda x: x["last_modified"], reverse=True)

    async def delete_image(self, directory_name: str, file_name: str) -> Dict:
        """
        Delete an image from storage.

        Args:
            directory_name: Directory name
            file_name: File name

        Returns:
            Deletion result dictionary
        """
        directory_name = self._sanitize_directory_name(directory_name)
        object_name = f"{directory_name}/{file_name}"
        
        if not self.repository.object_exists(object_name):
            raise ValueError(f"Image '{file_name}' not found in directory '{directory_name}'")
        
        success = self.repository.delete_object(object_name)
        
        if not success:
            raise RuntimeError("Failed to delete image from storage")
        
        return {
            "success": True,
            "message": "Image deleted successfully",
            "file_name": file_name,
            "directory_name": directory_name
        }

    async def get_image_data(self, directory_name: str, file_name: str) -> Optional[Tuple[bytes, str]]:
        """
        Get image data for direct serving.

        Args:
            directory_name: Directory name
            file_name: File name

        Returns:
            Tuple of (image_data, content_type) or None if not found
        """
        directory_name = self._sanitize_directory_name(directory_name)
        object_name = f"{directory_name}/{file_name}"
        
        # Get object info for content type
        info = self.repository.get_object_info(object_name)
        if not info:
            return None
        
        # Download image data
        data = self.repository.download_object(object_name)
        if not data:
            return None
        
        return data, info["content_type"]

    async def list_directories(self) -> List[Dict]:
        """
        List all directories containing images.

        Returns:
            List of directory information
        """
        directories = self.repository.list_directories()
        
        result = []
        for directory in directories:
            images = await self.get_images_in_directory(directory)
            result.append({
                "name": directory,
                "image_count": len(images),
                "total_size": sum(img["file_size"] for img in images),
                "last_modified": max((img["last_modified"] for img in images), default=datetime.min)
            })
        
        return sorted(result, key=lambda x: x["last_modified"], reverse=True)

    async def _check_duplicate_name(self, directory_name: str, original_name: str) -> bool:
        """
        Check if a file with the same original name exists in the directory.

        Args:
            directory_name: Directory name
            original_name: Original filename to check

        Returns:
            True if duplicate exists, False otherwise
        """
        images = await self.get_images_in_directory(directory_name)
        return any(img["original_name"] == original_name for img in images)

    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file.

        Args:
            file: Uploaded file

        Raises:
            ValueError: If validation fails
        """
        if not file.filename:
            raise ValueError("No filename provided")
        
        # Check file extension
        file_extension = self._get_file_extension(file.filename)
        if file_extension.lower() not in self.allowed_extensions:
            raise ValueError(f"File type not allowed. Allowed types: {', '.join(self.allowed_extensions)}")
        
        # Check content type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise ValueError("File must be an image")

    def _validate_and_process_image(self, file_content: bytes, content_type: str) -> Dict:
        """
        Validate image content and extract metadata.

        Args:
            file_content: Image file content
            content_type: MIME type

        Returns:
            Image information dictionary

        Raises:
            ValueError: If image is invalid
        """
        try:
            # Validate file size
            if len(file_content) > self.max_file_size:
                raise ValueError(f"File size too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB")
            
            # Open and validate image
            image = Image.open(io.BytesIO(file_content))
            image.verify()  # Verify it's a valid image
            
            # Reopen for metadata (verify() closes the image)
            image = Image.open(io.BytesIO(file_content))
            
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "has_transparency": image.mode in ('RGBA', 'LA') or 'transparency' in image.info
            }
            
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")

    def _get_file_extension(self, filename: str) -> str:
        """
        Get file extension from filename.

        Args:
            filename: Original filename

        Returns:
            File extension including the dot
        """
        return os.path.splitext(filename)[1].lower()

    def _sanitize_directory_name(self, directory_name: str) -> str:
        """
        Sanitize directory name for safe storage.

        Args:
            directory_name: Original directory name

        Returns:
            Sanitized directory name
        """
        # Remove/replace invalid characters
        sanitized = "".join(c for c in directory_name if c.isalnum() or c in ('-', '_'))
        
        # Ensure it's not empty and not too long
        if not sanitized:
            raise ValueError("Invalid directory name")
        
        return sanitized[:50]  # Limit length 