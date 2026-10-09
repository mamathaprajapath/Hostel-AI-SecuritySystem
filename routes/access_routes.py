from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import AccessLog, Resident
from backend.schemas.schemas import AccessLogOut, AccessLogCreate
from backend.services.notification_service import send_parent_notification

router = APIRouter(prefix="/api/access", tags=["Access Logs"])

@router.get("/logs", response_model=List[AccessLogOut])
def get_access_logs(
    hosteler_id: Optional[int] = None,
    event_type: Optional[str] = None,
    date_filter: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(AccessLog)
    if hosteler_id:
        query = query.filter(AccessLog.hosteler_id == hosteler_id)
    if event_type:
        query = query.filter(AccessLog.event_type == event_type.upper())
    if date_filter:
        try:
            target_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            query = query.filter(AccessLog.event_time >= target_date, AccessLog.event_time < target_date.replace(day=target_date.day+1))
        except Exception:
            pass

    return query.order_by(AccessLog.event_time.desc()).limit(limit).all()

@router.post("/log", response_model=AccessLogOut, status_code=status.HTTP_201_CREATED)
def create_manual_log(log_in: AccessLogCreate, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == log_in.hosteler_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    now_dt = datetime.now()
    log = AccessLog(
        hosteler_id=resident.id,
        event_type=log_in.event_type.upper(),
        event_time=now_dt,
        gate=log_in.gate or "Main Gate",
        confidence=log_in.confidence or 100.0,
        source=log_in.source or "Manual Entry"
    )

    resident.current_state = "INSIDE" if log_in.event_type.upper() == "ENTRY" else "OUTSIDE"
    db.add(log)
    db.commit()
    db.refresh(log)

    notif_msg = f"Hostel Gate Alert: Manual {log_in.event_type.upper()} recorded for {resident.name} ({resident.student_id}) at {now_dt.strftime('%I:%M %p')}."
    send_parent_notification(db, resident.id, f"{log_in.event_type.upper()}_DETECTED", notif_msg)

    return log
