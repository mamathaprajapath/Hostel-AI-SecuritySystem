from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import NotificationRecord

router = APIRouter(prefix="/api/notifications", tags=["Notification Logs"])

@router.get("/logs")
def get_notification_logs(
    hosteler_id: Optional[int] = None,
    channel: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(NotificationRecord)
    if hosteler_id:
        query = query.filter(NotificationRecord.hosteler_id == hosteler_id)
    if channel:
        query = query.filter(NotificationRecord.channel == channel.upper())

    records = query.order_by(NotificationRecord.sent_at.desc()).limit(100).all()
    return records
