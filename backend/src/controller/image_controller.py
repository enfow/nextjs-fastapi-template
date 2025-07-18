"""
Image controller for handling HTTP requests related to image management.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from ..service.image_service import ImageService
from ..schemas.image import (
    ImageUploadResponse, 
    ImageListResponse, 
    ImageDeleteResponse, 
    DirectoryListResponse,
    ImageInfoResponse
)
from ..logging_config import get_image_logger

# Create router
router = APIRouter()

# Create service instance
image_service = ImageService()

# Create logger
logger = get_image_logger()


@router.post("/upload", response_model=ImageUploadResponse, status_code=201)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    directory_name: str = Form(..., description="Directory name to store the image"),
    description: Optional[str] = Form(None, description="Optional image description")
):
    """
    Upload an image to MinIO storage.

    Args:
        file: Image file to upload
        directory_name: Directory name to organize images
        description: Optional description for the image

    Returns:
        Upload result with file information

    Raises:
        HTTPException: If upload fails or validation errors occur
    """
    logger.info(f"Starting image upload: {file.filename} to directory '{directory_name}'")
    
    try:
        result = await image_service.upload_image(
            file=file,
            directory_name=directory_name,
            description=description
        )
        
        logger.info(f"Successfully uploaded image: {result.get('file_name', 'unknown')}")
        return ImageUploadResponse(**result)

    except ValueError as e:
        logger.warning(f"Image upload validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Image upload runtime error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during image upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/directories", response_model=DirectoryListResponse)
async def list_directories():
    """
    List all directories containing images.

    Returns:
        List of directories with metadata
    """
    try:
        directories = await image_service.list_directories()
        
        return DirectoryListResponse(
            directories=directories,
            total=len(directories)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{directory_name}", response_model=ImageListResponse)
async def list_images_in_directory(directory_name: str):
    """
    List all images in a specific directory.

    Args:
        directory_name: Name of the directory

    Returns:
        List of images in the directory

    Raises:
        HTTPException: If directory access fails
    """
    try:
        images = await image_service.get_images_in_directory(directory_name)
        
        return ImageListResponse(
            images=images,
            total=len(images),
            directory_name=directory_name
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{directory_name}/{file_name}")
async def get_image(directory_name: str, file_name: str):
    """
    Get/download an image file.

    Args:
        directory_name: Directory name
        file_name: Image file name

    Returns:
        Image file as streaming response

    Raises:
        HTTPException: If image not found
    """
    try:
        result = await image_service.get_image_data(directory_name, file_name)
        
        if not result:
            raise HTTPException(status_code=404, detail="Image not found")
        
        image_data, content_type = result
        
        return StreamingResponse(
            io.BytesIO(image_data),
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename={file_name}",
                "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{directory_name}/{file_name}/info", response_model=ImageInfoResponse)
async def get_image_info(directory_name: str, file_name: str):
    """
    Get detailed information about an image.

    Args:
        directory_name: Directory name
        file_name: Image file name

    Returns:
        Detailed image information

    Raises:
        HTTPException: If image not found
    """
    try:
        images = await image_service.get_images_in_directory(directory_name)
        image_info = next((img for img in images if img["file_name"] == file_name), None)
        
        if not image_info:
            raise HTTPException(status_code=404, detail="Image not found")
        
        return ImageInfoResponse(
            file_name=image_info["file_name"],
            original_name=image_info["original_name"],
            directory_name=image_info["directory_name"],
            file_size=image_info["file_size"],
            content_type=image_info["content_type"],
            url=image_info["url"],
            last_modified=image_info["last_modified"],
            etag=image_info["etag"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{directory_name}/{file_name}", response_model=ImageDeleteResponse)
async def delete_image(directory_name: str, file_name: str):
    """
    Delete an image from storage.

    Args:
        directory_name: Directory name
        file_name: Image file name

    Returns:
        Deletion result

    Raises:
        HTTPException: If image not found or deletion fails
    """
    try:
        result = await image_service.delete_image(directory_name, file_name)
        
        return ImageDeleteResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{directory_name}/bulk-upload")
async def bulk_upload_images(
    directory_name: str,
    files: list[UploadFile] = File(..., description="Multiple image files to upload"),
    description: Optional[str] = Form(None, description="Optional description for all images")
):
    """
    Upload multiple images to the same directory.

    Args:
        directory_name: Directory name to store images
        files: List of image files to upload
        description: Optional description for all images

    Returns:
        List of upload results

    Raises:
        HTTPException: If any upload fails
    """
    logger.info(f"Starting bulk upload: {len(files)} files to directory '{directory_name}'")
    
    try:
        results = []
        errors = []

        for i, file in enumerate(files):
            try:
                logger.debug(f"Processing file {i+1}/{len(files)}: {file.filename}")
                result = await image_service.upload_image(
                    file=file,
                    directory_name=directory_name,
                    description=description
                )
                results.append(result)
                logger.debug(f"File {i+1} uploaded successfully: {result.get('file_name', 'unknown')}")
            except Exception as e:
                logger.warning(f"File {i+1} ({file.filename}) failed to upload: {str(e)}")
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })

        logger.info(f"Bulk upload complete: {len(results)} success, {len(errors)} errors")
        
        return {
            "success": len(errors) == 0,
            "message": f"Uploaded {len(results)} images successfully" + (f", {len(errors)} failed" if errors else ""),
            "results": results,
            "errors": errors,
            "total_uploaded": len(results),
            "total_errors": len(errors)
        }

    except Exception as e:
        logger.error(f"Unexpected error during bulk upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{directory_name}")
async def delete_directory(directory_name: str):
    """
    Delete all images in a directory.

    Args:
        directory_name: Directory name to delete

    Returns:
        Deletion summary

    Raises:
        HTTPException: If deletion fails
    """
    try:
        # Get all images in the directory
        images = await image_service.get_images_in_directory(directory_name)
        
        if not images:
            raise HTTPException(status_code=404, detail="Directory not found or empty")
        
        deleted_count = 0
        errors = []

        for image in images:
            try:
                await image_service.delete_image(directory_name, image["file_name"])
                deleted_count += 1
            except Exception as e:
                errors.append({
                    "filename": image["file_name"],
                    "error": str(e)
                })

        return {
            "success": len(errors) == 0,
            "message": f"Deleted {deleted_count} images from directory '{directory_name}'" + (f", {len(errors)} failed" if errors else ""),
            "directory_name": directory_name,
            "deleted_count": deleted_count,
            "errors": errors
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") 