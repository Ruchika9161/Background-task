import os
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Background Image Processor"
    version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Directory settings
    upload_dir: str = "uploads"
    result_dir: str = "result_images"
    
    # Redis settings for Celery
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_url: str ="redis://localhost:6379/0"
    
    # Celery settings
    celery_broker_url: str = redis_url
    celery_result_backend: str = redis_url
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Ensure directories exist
try:
    Path(settings.upload_dir).mkdir(exist_ok=True)
except FileExistsError:
    pass  # Directory already exists
try:
    Path(settings.result_dir).mkdir(exist_ok=True)
except FileExistsError:
    pass  # Directory already exists 