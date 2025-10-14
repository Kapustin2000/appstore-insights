"""
Main FastAPI application.
"""

from fastapi import FastAPI

from .api.routes import router
from .core.config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="API for fetching Apple App Store app information and reviews",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include API routes
app.include_router(router, prefix="/app", tags=["app"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
