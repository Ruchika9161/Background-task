# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import uvicorn
from pathlib import Path

from config import settings
from routers import upload, health

# Create FastAPI application with configuration
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    description="Background image processing service with contour detection using Celery",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(health.router)

# Serve static files (for accessing processed images)
# Ensure result directory exists before mounting
result_path = Path(settings.result_dir)
if not result_path.exists():
    result_path.mkdir(exist_ok=True)

app.mount(
    "/static/results",
    StaticFiles(directory=settings.result_dir),
    name="results"
)

# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/info")
async def app_info():
    """Get application information"""
    return {
        "app_name": settings.app_name,
        "version": settings.version,
        "debug": settings.debug,
        "upload_dir": settings.upload_dir,
        "result_dir": settings.result_dir,
        "max_file_size_mb": settings.max_file_size / (1024 * 1024),
        "allowed_extensions": settings.allowed_extensions,
        "docs_url": "/docs",
        "health_check": "/api/v1/health",
        "upload_endpoint": "/api/v1/images/upload"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info" if settings.debug else "warning"
    )
