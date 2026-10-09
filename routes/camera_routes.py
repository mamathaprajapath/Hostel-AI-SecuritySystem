from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from backend.services.camera_service import camera_service

router = APIRouter(prefix="/api/camera", tags=["Smart Camera Engine"])

@router.get("/stream")
def video_feed():
    """Returns real-time MJPEG live camera stream with AI recognition overlay."""
    return StreamingResponse(
        camera_service.generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.post("/mode")
def set_camera_mode(mode: str = Body(..., embed=True)):
    """Toggles gate mode: ENTRY or EXIT."""
    if mode.upper() not in ["ENTRY", "EXIT"]:
        raise HTTPException(status_code=400, detail="Invalid camera mode. Must be 'ENTRY' or 'EXIT'.")
    camera_service.set_mode(mode.upper())
    return {"message": f"Camera gate mode changed to {mode.upper()}", "mode": camera_service.mode}

@router.get("/status")
def get_camera_status():
    """Returns current real-time detection & recognition metadata."""
    return camera_service.current_frame_info
