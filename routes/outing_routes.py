from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import OutingRequest, Resident
from backend.schemas.schemas import OutingCreate, OutingStatusUpdate, OutingOut
from backend.services.notification_service import send_parent_notification

router = APIRouter(prefix="/api/outing", tags=["Outing & Home Requests"])

@router.get("/requests", response_model=List[OutingOut])
def get_outing_requests(
    hosteler_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(OutingRequest)
    if hosteler_id:
        query = query.filter(OutingRequest.hosteler_id == hosteler_id)
    if status_filter:
        query = query.filter(OutingRequest.status == status_filter.upper())
    return query.order_by(OutingRequest.created_at.desc()).all()

@router.post("/request", response_model=OutingOut, status_code=status.HTTP_201_CREATED)
def create_outing_request(request_in: OutingCreate, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == request_in.hosteler_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Hosteler/Resident not found")

    outing = OutingRequest(
        hosteler_id=request_in.hosteler_id,
        request_type=request_in.request_type.upper(),
        reason=request_in.reason,
        destination=request_in.destination,
        departure_time=request_in.departure_time,
        expected_return=request_in.expected_return,
        status="PENDING"
    )
    db.add(outing)
    db.commit()
    db.refresh(outing)
    return outing

@router.put("/request/{request_id}/status", response_model=OutingOut)
def update_outing_status(
    request_id: int,
    status_in: OutingStatusUpdate,
    approved_by_id: Optional[int] = 1, # Default warden user ID
    db: Session = Depends(get_db)
):
    outing = db.query(OutingRequest).filter(OutingRequest.id == request_id).first()
    if not outing:
        raise HTTPException(status_code=404, detail="Outing request not found")

    new_status = status_in.status.upper()
    if new_status not in ["APPROVED", "REJECTED", "EXITED", "RETURNED"]:
        raise HTTPException(status_code=400, detail="Invalid status option.")

    outing.status = new_status
    outing.remarks = status_in.remarks
    outing.approved_by = approved_by_id

    db.commit()
    db.refresh(outing)

    # Trigger Parent Notification
    resident = db.query(Resident).filter(Resident.id == outing.hosteler_id).first()
    if resident:
        event_name = f"OUTING_{new_status}"
        dep_str = outing.departure_time.strftime("%d %b %Y %I:%M %p")
        ret_str = outing.expected_return.strftime("%d %b %Y %I:%M %p")
        msg = f"Hostel Outing Update: {outing.request_type} request for {resident.name} has been {new_status}.\nDestination: {outing.destination}\nDeparture: {dep_str}\nExpected Return: {ret_str}"
        if outing.remarks:
            msg += f"\nWarden Remarks: {outing.remarks}"

        send_parent_notification(db, resident.id, event_name, msg)

    return outing
