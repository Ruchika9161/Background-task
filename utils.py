# utils.py

import cv2
import uuid
from pathlib import Path


def detect_and_draw_contours(image_path: str, output_dir: str = "result_images") -> str:
    # Read the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect edges
    edges = cv2.Canny(gray, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours
    cv2.drawContours(image, contours, -1, (0, 255, 0), 2)

    # Save result
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = f"{output_dir}/contour_{uuid.uuid4().hex}.jpg"
    cv2.imwrite(output_path, image)

    return output_path
