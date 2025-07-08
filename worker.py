# worker.py

from celery import Celery
from utils import detect_and_draw_contours

# Configure Celery app
celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Background task for contour detection
@celery_app.task
def process_image_task(image_path: str):
    result = detect_and_draw_contours(image_path)
    return {"status": "done", "output_file": result}
