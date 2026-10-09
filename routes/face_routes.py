from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.face_service import enroll_resident_face

router = APIRouter(prefix="/api/faces", tags=["Face Enrollment"])

@router.post("/enroll/{resident_id}")
async def enroll_face(
    resident_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image file (JPG, PNG).")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    success, message = enroll_resident_face(db, resident_id, image_bytes)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"message": message, "resident_id": resident_id}
