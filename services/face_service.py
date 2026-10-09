import os
import json
import cv2
import numpy as np
from sqlalchemy.orm import Session
from backend.models.models import Resident, FaceProfile
from ai.face_detection import validate_enrollment_image, crop_face
from ai.face_recognition import ai_engine
from backend.config import settings

def enroll_resident_face(db: Session, hosteler_id: int, image_bytes: bytes) -> tuple[bool, str]:
    """
    Validates, crops, saves, and registers a resident's face profile in DB and AI engine.
    """
    resident = db.query(Resident).filter(Resident.id == hosteler_id).first()
    if not resident:
        return False, "Resident not found."

    is_valid, img, bbox, msg = validate_enrollment_image(image_bytes)
    if not is_valid or img is None or bbox is None:
        return False, msg

    # Crop and resize face
    face_crop = crop_face(img, bbox, target_size=(200, 200))

    # Save original image and face crop to disk
    filename = f"resident_{resident.id}_{resident.student_id}.jpg"
    photo_path = os.path.join(settings.FACES_DIR, filename)
    cv2.imwrite(photo_path, img)

    crop_filename = f"resident_{resident.id}_crop.jpg"
    crop_path = os.path.join(settings.FACES_DIR, crop_filename)
    cv2.imwrite(crop_path, face_crop)

    # Convert grayscale crop to JSON feature vector representation
    gray_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray_crop], [0], None, [256], [0, 256]).flatten().tolist()

    # Update or create FaceProfile entity
    face_profile = db.query(FaceProfile).filter(FaceProfile.hosteler_id == hosteler_id).first()
    if face_profile:
        face_profile.embedding_data = json.dumps(hist)
        face_profile.sample_count += 1
    else:
        face_profile = FaceProfile(
            hosteler_id=hosteler_id,
            embedding_data=json.dumps(hist),
            sample_count=1
        )
        db.add(face_profile)

    # Update Resident record
    resident.photo_path = f"/static/uploads/faces/{filename}"
    resident.face_enrolled = True
    db.commit()

    # Retrain AI engine with all enrolled faces from database
    reload_all_face_profiles(db)

    return True, "Face profile enrolled and trained successfully."

def reload_all_face_profiles(db: Session):
    """
    Loads all enrolled face crops from disk and retrains the AI recognition engine.
    """
    residents = db.query(Resident).filter(Resident.face_enrolled == True).all()
    profiles = []

    for r in residents:
        crop_path = os.path.join(settings.FACES_DIR, f"resident_{r.id}_crop.jpg")
        if os.path.exists(crop_path):
            face_img = cv2.imread(crop_path, cv2.IMREAD_GRAYSCALE)
            if face_img is not None:
                profiles.append((r.id, face_img))

    ai_engine.train_profiles(profiles)
    print(f"[Face Service] Reloaded {len(profiles)} face profiles into AI Recognition Engine.")
