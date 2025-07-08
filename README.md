# Background Image Processor

A FastAPI-based web service for background image processing with contour detection using Celery and Redis.

## Features

- **File Upload**: Upload images for background processing
- **Background Processing**: Uses Celery for asynchronous image processing
- **Contour Detection**: OpenCV-based contour detection on uploaded images
- **Health Monitoring**: Comprehensive health checks for all components
- **REST API**: Well-documented REST API with automatic documentation
- **Configuration Management**: Environment-based configuration
- **Static File Serving**: Access processed images via HTTP

## Project Structure

```
backgroundTasks/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── worker.py            # Celery worker for background tasks
├── utils.py             # Image processing utilities
├── start.py             # Application startup script
├── requirements.txt     # Python dependencies
├── routers/
│   ├── __init__.py
│   ├── upload.py        # Image upload endpoints
│   └── health.py        # Health check endpoints
├── uploads/             # Uploaded images directory
└── result_images/       # Processed images directory
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis Server

Make sure Redis is running on your system:

```bash
# On Windows (if Redis is installed)
redis-server

# On Linux/Mac
redis-server
```

### 3. Start Celery Worker

In a separate terminal:

```bash
celery -A worker worker --loglevel=info
```

### 4. Start the Application

```bash
python start.py
```

Or directly:

```bash
python main.py
```

## API Endpoints

### Image Processing

- `POST /api/v1/images/upload` - Upload an image for processing
- `GET /api/v1/images/status/{task_id}` - Get processing status
- `GET /api/v1/images/results` - List processed images

### Health Checks

- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/redis` - Redis connection health
- `GET /api/v1/health/celery` - Celery worker health
- `GET /api/v1/health/full` - Comprehensive health check

### Application Info

- `GET /` - Redirects to API documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)
- `GET /info` - Application information

### Static Files

- `GET /static/results/{filename}` - Access processed images

## Configuration

The application uses environment variables for configuration. Create a `.env` file or set environment variables:

```env
# Application Settings
APP_NAME=Background Image Processor
VERSION=1.0.0
DEBUG=false

# Server Settings
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Directory Settings
UPLOAD_DIR=uploads
RESULT_DIR=result_images

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB in bytes
```

## Usage Examples

### Upload an Image

```bash
curl -X POST "http://localhost:8000/api/v1/images/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_image.jpg"
```

Response:
```json
{
  "message": "Image uploaded successfully",
  "status": "Contour detection started in background",
  "task_id": "abc123-def456-ghi789",
  "filename": "your_image.jpg",
  "file_path": "uploads/your_image.jpg"
}
```

### Check Processing Status

```bash
curl "http://localhost:8000/api/v1/images/status/abc123-def456-ghi789"
```

### Health Check

```bash
curl "http://localhost:8000/api/v1/health/full"
```

## Supported File Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

## Error Handling

The API provides detailed error messages and appropriate HTTP status codes:

- `400 Bad Request` - Invalid file format or size
- `413 Request Entity Too Large` - File size exceeds limit
- `500 Internal Server Error` - Processing errors
- `503 Service Unavailable` - Service health issues

## Development

### Running in Development Mode

Set `DEBUG=true` in your environment or `.env` file for:
- Detailed error messages
- Auto-reload on code changes
- Verbose logging

### Adding New Endpoints

1. Create or modify routers in the `routers/` directory
2. Import and include the router in `main.py`
3. Update this documentation

### Custom Configuration

Modify `config.py` to add new configuration options and update the `Settings` class.

## Production Deployment

1. Set `DEBUG=false`
2. Configure appropriate CORS origins
3. Use a production WSGI server like Gunicorn
4. Set up proper Redis configuration
5. Configure file upload limits and security
6. Set up monitoring and logging

## Troubleshooting

### Redis Connection Issues
- Ensure Redis server is running
- Check Redis host/port configuration
- Use health check endpoint: `/api/v1/health/redis`

### Celery Worker Issues
- Ensure Celery worker is running
- Check worker logs for errors
- Use health check endpoint: `/api/v1/health/celery`

### File Upload Issues
- Check file size and format restrictions
- Verify upload directory permissions
- Check disk space availability

## License

This project is available for educational and commercial use.
