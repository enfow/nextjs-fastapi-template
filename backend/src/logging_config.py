"""
Logging configuration for the FastAPI application.
"""

import logging
import sys
import os
from typing import Dict, Any


def setup_logging(environment: str = "development") -> None:
    """
    Configure logging for the application.
    
    Args:
        environment: Environment type ("development" or "production")
    """
    # Determine log level based on environment
    if environment.lower() == "production":
        log_level = logging.WARNING
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        log_level = logging.INFO
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    
    # Override with environment variable if set
    env_log_level = os.getenv("LOG_LEVEL", "").upper()
    if env_log_level:
        log_level = getattr(logging, env_log_level, log_level)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True  # Override any existing configuration
    )
    
    # Configure specific loggers
    configure_logger_levels(environment)


def configure_logger_levels(environment: str) -> None:
    """
    Configure specific logger levels.
    
    Args:
        environment: Environment type
    """
    if environment.lower() == "production":
        # Production: Reduce noise from external libraries
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("fastapi").setLevel(logging.WARNING)
        logging.getLogger("multipart").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("minio").setLevel(logging.WARNING)
        logging.getLogger("pymongo").setLevel(logging.WARNING)
        logging.getLogger("motor").setLevel(logging.WARNING)
    else:
        # Development: Show more detailed logs
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)
        logging.getLogger("fastapi").setLevel(logging.INFO)
        logging.getLogger("multipart").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("minio").setLevel(logging.INFO)
        logging.getLogger("pymongo").setLevel(logging.INFO)
        logging.getLogger("motor").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Application-specific loggers
def get_app_logger() -> logging.Logger:
    """Get the main application logger."""
    return get_logger("fastapi_app")


def get_auth_logger() -> logging.Logger:
    """Get the authentication logger."""
    return get_logger("fastapi_app.auth")


def get_image_logger() -> logging.Logger:
    """Get the image operations logger."""
    return get_logger("fastapi_app.images")


def get_database_logger() -> logging.Logger:
    """Get the database logger."""
    return get_logger("fastapi_app.database")


def get_minio_logger() -> logging.Logger:
    """Get the MinIO logger."""
    return get_logger("fastapi_app.minio") 