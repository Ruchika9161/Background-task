from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import os
from typing import Dict, Any, List
from config import settings

router = APIRouter(
    prefix="/api/v1/images",
    tags=["image-processing"],
    responses={404: {"description": "Not found"}},
)

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not allowed. Allowed types: {settings.allowed_extensions}"
        )

def process_image_sync(file_path: str) -> Dict[str, Any]:
    """Process image synchronously (fallback when Redis/Celery unavailable)"""
    try:
        from utils import detect_and_draw_contours
        
        # Process the image using the correct function
        output_path = detect_and_draw_contours(str(file_path), settings.result_dir)
        
        return {
            "status": "completed",
            "input_file": str(file_path),
            "output_file": output_path,
            "message": "Image processed successfully (synchronous mode)"
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "message": "Failed to process image"
        }

@router.post(
    "/upload", 
    response_model=Dict[str, Any],
    responses={
        200: {"description": "Image uploaded successfully"},
        400: {"description": "Invalid file format"},
        413: {"description": "File too large"},
        500: {"description": "Upload failed"}
    }
)
async def upload_image(
    file: UploadFile = File(..., description="Image file to process (jpg, jpeg, png, bmp, tiff)")
):
    """
    Upload an image for background processing
    
    **Parameters:**
    - **file**: Image file to upload (multipart/form-data)
    
    **Supported formats:** jpg, jpeg, png, bmp, tiff
    
    **Returns:** Task ID and processing status
    """
    try:
        # Validate the uploaded file
        validate_file(file)
        
        # Create unique filename to avoid conflicts
        file_extension = Path(file.filename).suffix
        safe_filename = f"{file.filename.replace(' ', '_').replace(file_extension, '')}{file_extension}"
        file_path = Path(settings.upload_dir) / safe_filename
        
        # Save the uploaded image to disk
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Try background processing first, fallback to sync processing
        try:
            from worker import process_image_task
            task = process_image_task.delay(str(file_path))
            
            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content={
                    "message": "Image uploaded successfully",
                    "status": "Contour detection started in background",
                    "task_id": task.id,
                    "filename": safe_filename,
                    "file_path": str(file_path),
                    "mode": "background"
                }
            )
        except Exception as redis_error:
            # Fallback to synchronous processing
            print(f"Redis/Celery unavailable: {redis_error}")
            print("Switching to synchronous processing...")
            
            result = process_image_sync(str(file_path))
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Image uploaded and processed successfully",
                    "filename": safe_filename,
                    "file_path": str(file_path),
                    "processing_result": result,
                    "mode": "synchronous",
                    "note": "Redis/Celery unavailable, processed immediately"
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process upload: {str(e)}"
        )

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a background task
    
    - **task_id**: The task ID returned from upload endpoint
    """
    try:
        from worker import celery_app
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': 'Task is waiting to be processed'
            }
        elif task.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', '')
            }
        elif task.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'state': task.state,
                'result': task.result
            }
        else:  # FAILURE
            response = {
                'task_id': task_id,
                'state': task.state,
                'error': str(task.info)
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Task status service unavailable (Redis/Celery not running): {str(e)}"
        )

@router.get("/results")
async def list_processed_images():
    """
    List all processed images in the results directory
    """
    try:
        result_dir = Path(settings.result_dir)
        if not result_dir.exists():
            return {"processed_images": []}
        
        processed_files = []
        for file_path in result_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in settings.allowed_extensions:
                processed_files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "created": file_path.stat().st_ctime
                })
        
        return {
            "processed_images": processed_files,
            "count": len(processed_files)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list processed images: {str(e)}"
        ) 