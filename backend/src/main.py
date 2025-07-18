"""
FastAPI Main Application

This is the entry point for the FastAPI backend application.
It uses a controller-service-repository architecture pattern.
Supports SQLite, MongoDB, and MinIO object storage.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os

from src.database import create_tables
from src.mongodb import mongodb_manager
from src.minio_client import minio_manager
from src.controller.sqlite_user_controller import router as sqlite_user_router
from src.controller.mongo_user_controller import router as mongo_user_router
from src.controller.image_controller import router as image_router
from src.controller.auth_controller import router as auth_router
from src.logging_config import setup_logging, get_app_logger


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="NextJS FastAPI Template API",
        description="A modern API backend using controller-service-repository pattern with SQLite, MongoDB, and MinIO support",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Configure CORS
    cors_origins = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
    ).split(",")
    cors_origins.extend(
        [
            "http://frontend-dev:3000",  # Docker container name for dev
            "http://frontend-prod:3000",  # Docker container name for prod
        ]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint that tests all services."""
        sqlite_status = "healthy"
        mongodb_status = "healthy"
        minio_status = "healthy"
        
        try:
            # Test MongoDB connection
            mongodb_healthy = await mongodb_manager.ping()
            if not mongodb_healthy:
                mongodb_status = "unhealthy"
        except Exception:
            mongodb_status = "unhealthy"
        
        try:
            # Test MinIO connection
            minio_healthy = minio_manager.ping()
            if not minio_healthy:
                minio_status = "unhealthy"
        except Exception:
            minio_status = "unhealthy"
            
        unhealthy_services = [
            service for service, status in {
                "mongodb": mongodb_status,
                "minio": minio_status
            }.items() if status == "unhealthy"
        ]
        
        overall_status = "healthy" if not unhealthy_services else "degraded"
        
        return JSONResponse(
            status_code=200,
            content={
                "status": overall_status,
                "message": "FastAPI backend is running",
                "version": "1.0.0",
                "services": {
                    "sqlite": sqlite_status,
                    "mongodb": mongodb_status,
                    "minio": minio_status
                },
                "unhealthy_services": unhealthy_services
            },
        )

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Welcome to NextJS FastAPI Template API",
            "docs": "/api/docs",
            "health": "/api/health",
            "services": ["SQLite", "MongoDB", "MinIO"],
            "endpoints": {
                "sqlite_users": "/api/sqlite-users",
                "mongodb_users": "/api/mongo-users",
                "images": "/api/images"
            },
            "features": [
                "User management (SQLite & MongoDB)",
                "Image upload and storage (MinIO)",
                "RESTful API with OpenAPI docs",
                "Health monitoring"
            ]
        }

    # Authentication
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

    # SQLite users
    app.include_router(sqlite_user_router, prefix="/api/sqlite-users", tags=["SQLite Users"])
    
    # MongoDB users
    app.include_router(mongo_user_router, prefix="/api/mongo-users", tags=["MongoDB Users"])
    
    # Images (MinIO)
    app.include_router(image_router, prefix="/api/images", tags=["Images"])

    return app


# Create the app instance
app = create_app()

# Initialize logging system
environment = os.getenv("NODE_ENV", "development")
setup_logging(environment)
logger = get_app_logger()

# Service initialization events
@app.on_event("startup")
async def startup_event():
    """Initialize all services on application startup."""
    logger.info("🚀 Starting FastAPI application...")
    
    # Initialize SQLite
    try:
        create_tables()
        logger.info("✅ SQLite database initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize SQLite: {e}")
    
    # Initialize MongoDB
    try:
        await mongodb_manager.connect()
        logger.info("✅ MongoDB database initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MongoDB: {e}")
        logger.warning("⚠️  Application will continue without MongoDB")
    
    # Initialize MinIO
    try:
        minio_manager.connect()
        logger.info("✅ MinIO object storage initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MinIO: {e}")
        logger.warning("⚠️  Application will continue without MinIO")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up services on application shutdown."""
    logger.info("🛑 Shutting down FastAPI application...")
    
    try:
        await mongodb_manager.disconnect()
        logger.info("✅ MongoDB disconnected successfully!")
    except Exception as e:
        logger.error(f"❌ Error disconnecting from MongoDB: {e}")
    
    # MinIO doesn't require explicit disconnection
    logger.info("✅ All services shut down successfully!")


if __name__ == "__main__":
    """
    Run the application with uvicorn when executed directly.
    For production, use: uvicorn main:app --host 0.0.0.0 --port 8000
    """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info",
    )
