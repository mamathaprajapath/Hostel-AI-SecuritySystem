from datetime import datetime, date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import Resident, AccessLog, OutingRequest, UnknownEvent, NotificationRecord

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard Statistics"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    today_start = datetime.combine(date.today(), datetime.min.time())

    total_residents = db.query(Resident).filter(Resident.status == "active").count()
    residents_inside = db.query(Resident).filter(Resident.status == "active", Resident.current_state == "INSIDE").count()
    residents_outside = db.query(Resident).filter(Resident.status == "active", Resident.current_state == "OUTSIDE").count()

    today_entries = db.query(AccessLog).filter(
        AccessLog.event_type == "ENTRY",
        AccessLog.event_time >= today_start
    ).count()

    today_exits = db.query(AccessLog).filter(
        AccessLog.event_type == "EXIT",
        AccessLog.event_time >= today_start
    ).count()

    pending_outings = db.query(OutingRequest).filter(OutingRequest.status == "PENDING").count()
    unknown_alerts = db.query(UnknownEvent).filter(UnknownEvent.review_status == "PENDING").count()

    # Recent Access Activity (top 5)
    recent_logs = db.query(AccessLog).order_by(AccessLog.event_time.desc()).limit(5).all()
    recent_activities = []
    for log in recent_logs:
        res = db.query(Resident).filter(Resident.id == log.hosteler_id).first()
        recent_activities.append({
            "id": log.id,
            "student_name": res.name if res else "Unknown",
            "student_id": res.student_id if res else "",
            "room_no": res.room_no if res else "",
            "event_type": log.event_type,
            "time": log.event_time.strftime("%I:%M:%S %p"),
            "confidence": f"{log.confidence:.0f}%"
        })

    return {
        "total_residents": total_residents,
        "residents_inside": residents_inside,
        "residents_outside": residents_outside,
        "today_entries": today_entries,
        "today_exits": today_exits,
        "pending_outings": pending_outings,
        "unknown_alerts": unknown_alerts,
        "recent_activities": recent_activities
    }
