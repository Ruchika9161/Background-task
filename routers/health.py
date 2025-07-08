from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import redis
from datetime import datetime
from config import settings
from typing import Dict, Any

router = APIRouter(
    prefix="/api/v1/health",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=Dict[str, Any])
async def health_check():
    """
    Basic health check endpoint
    
    Returns application status and configuration info
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "app_name": settings.app_name,
        "version": settings.version,
        "upload_dir": settings.upload_dir,
        "result_dir": settings.result_dir
    }

@router.get("/redis")
async def redis_health():
    """
    Check Redis connection health
    
    Verifies that Redis (used by Celery) is accessible
    """
    try:
        # Test Redis connection
        r = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True
        )
        
        # Test basic operations
        test_key = "health_check_test"
        r.set(test_key, "test_value", ex=10)  # Expires in 10 seconds
        value = r.get(test_key)
        r.delete(test_key)
        
        if value == "test_value":
            return {
                "status": "healthy",
                "redis_host": settings.redis_host,
                "redis_port": settings.redis_port,
                "redis_db": settings.redis_db,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise Exception("Redis test failed")
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis health check failed: {str(e)}"
        )

@router.get("/celery")
async def celery_health():
    """
    Check Celery worker health
    
    Verifies that Celery workers are running and responsive
    """
    try:
        from worker import celery_app
        
        # Get active workers
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        stats = inspect.stats()
        
        if not active_workers:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No active Celery workers found"
            )
        
        return {
            "status": "healthy",
            "active_workers": list(active_workers.keys()) if active_workers else [],
            "worker_count": len(active_workers) if active_workers else 0,
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Celery health check failed: {str(e)}"
        )

@router.get("/full")
async def full_health_check():
    """
    Comprehensive health check
    
    Tests all system components
    """
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": "healthy",
        "components": {}
    }
    
    # Test basic app health
    try:
        basic_health = await health_check()
        results["components"]["app"] = {"status": "healthy", "details": basic_health}
    except Exception as e:
        results["components"]["app"] = {"status": "unhealthy", "error": str(e)}
        results["overall_status"] = "degraded"
    
    # Test Redis
    try:
        redis_health_result = await redis_health()
        results["components"]["redis"] = {"status": "healthy", "details": redis_health_result}
    except HTTPException as e:
        results["components"]["redis"] = {"status": "unhealthy", "error": e.detail}
        results["overall_status"] = "degraded"
    except Exception as e:
        results["components"]["redis"] = {"status": "unhealthy", "error": str(e)}
        results["overall_status"] = "degraded"
    
    # Test Celery
    try:
        celery_health_result = await celery_health()
        results["components"]["celery"] = {"status": "healthy", "details": celery_health_result}
    except HTTPException as e:
        results["components"]["celery"] = {"status": "unhealthy", "error": e.detail}
        results["overall_status"] = "degraded"
    except Exception as e:
        results["components"]["celery"] = {"status": "unhealthy", "error": str(e)}
        results["overall_status"] = "degraded"
    
    # Return appropriate status code
    if results["overall_status"] == "healthy":
        return JSONResponse(content=results, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content=results, status_code=status.HTTP_503_SERVICE_UNAVAILABLE) 