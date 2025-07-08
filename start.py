#!/usr/bin/env python3
"""
Startup script for the Background Image Processor application
"""

import uvicorn
from config import settings

def main():
    """Start the FastAPI application"""
    print(f"Starting {settings.app_name} v{settings.version}")
    print(f"Server will run on http://{settings.host}:{settings.port}")
    print(f"API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"Health Check: http://{settings.host}:{settings.port}/api/v1/health")
    print(f"Upload Directory: {settings.upload_dir}")
    print(f"Results Directory: {settings.result_dir}")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info" if settings.debug else "warning"
    )

if __name__ == "__main__":
    main() 