import cv2
import numpy as np
from typing import Tuple, List, Optional

# Load default OpenCV Haar Cascade for frontal face detection
FACE_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)

def detect_faces(image: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    Detects faces in an OpenCV BGR image.
    Returns a list of bounding boxes (x, y, w, h).
    """
    if image is None or image.size == 0:
        return []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]

def crop_face(image: np.ndarray, bbox: Tuple[int, int, int, int], target_size: Tuple[int, int] = (200, 200)) -> np.ndarray:
    """
    Crops the face from image and resizes to target_size.
    """
    x, y, w, h = bbox
    # Add a small padding margin
    margin_w = int(w * 0.1)
    margin_h = int(h * 0.1)
    
    h_img, w_img = image.shape[:2]
    x1 = max(0, x - margin_w)
    y1 = max(0, y - margin_h)
    x2 = min(w_img, x + w + margin_w)
    y2 = min(h_img, y + h + margin_h)
    
    face_crop = image[y1:y2, x1:x2]
    if face_crop.size == 0:
        face_crop = image[y:y+h, x:x+w]
        
    resized = cv2.resize(face_crop, target_size)
    return resized

def validate_enrollment_image(image_bytes: bytes, max_size_mb: float = 5.0) -> Tuple[bool, Optional[np.ndarray], Optional[Tuple[int, int, int, int]], str]:
    """
    Validates uploaded resident image for face enrollment.
    - Must be valid image
    - Max size 5MB
    - Exactly 1 face must be present
    Returns (is_valid, bgr_image, bbox, message)
    """
    if len(image_bytes) > max_size_mb * 1024 * 1024:
        return False, None, None, f"File size exceeds maximum limit of {max_size_mb}MB."

    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        return False, None, None, "Could not decode image. Please upload a valid JPG or PNG file."

    faces = detect_faces(img)

    if len(faces) == 0:
        return False, img, None, "No face detected in the uploaded image. Please provide a clear front-facing photo."

    if len(faces) > 1:
        return False, img, None, f"Multiple faces ({len(faces)}) detected. Enrollment photo must contain exactly one face."

    bbox = faces[0]
    return True, img, bbox, "Face detected and validated successfully."
