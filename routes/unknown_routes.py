from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import UnknownEvent
from backend.schemas.schemas import UnknownEventOut, UnknownEventUpdate

router = APIRouter(prefix="/api/unknown", tags=["Unknown Person Events"])

@router.get("/events", response_model=List[UnknownEventOut])
def get_unknown_events(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(UnknownEvent)
    if status_filter:
        query = query.filter(UnknownEvent.review_status == status_filter.upper())
    return query.order_by(UnknownEvent.captured_at.desc()).all()

@router.put("/event/{event_id}/review", response_model=UnknownEventOut)
def review_unknown_event(
    event_id: int,
    review_in: UnknownEventUpdate,
    reviewed_by_id: Optional[int] = 1,
    db: Session = Depends(get_db)
):
    event = db.query(UnknownEvent).filter(UnknownEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Unknown event record not found")

    event.review_status = review_in.review_status.upper()
    event.remarks = review_in.remarks
    event.reviewed_by = reviewed_by_id

    db.commit()
    db.refresh(event)
    return event
