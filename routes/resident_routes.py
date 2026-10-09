from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import Resident
from backend.schemas.schemas import ResidentCreate, ResidentUpdate, ResidentOut

router = APIRouter(prefix="/api/residents", tags=["Residents"])

@router.get("", response_model=List[ResidentOut])
def get_residents(
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    state_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Resident)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Resident.name.like(search_term)) |
            (Resident.student_id.like(search_term)) |
            (Resident.room_no.like(search_term)) |
            (Resident.department.like(search_term))
        )
    if status_filter:
        query = query.filter(Resident.status == status_filter)
    if state_filter:
        query = query.filter(Resident.current_state == state_filter)

    return query.order_by(Resident.created_at.desc()).all()

@router.post("", response_model=ResidentOut, status_code=status.HTTP_201_CREATED)
def create_resident(resident_in: ResidentCreate, db: Session = Depends(get_db)):
    existing = db.query(Resident).filter(Resident.student_id == resident_in.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Student ID '{resident_in.student_id}' is already registered.")

    resident = Resident(
        student_id=resident_in.student_id,
        name=resident_in.name,
        room_no=resident_in.room_no,
        department=resident_in.department,
        phone=resident_in.phone,
        email=resident_in.email,
        status="active",
        current_state="INSIDE"
    )
    db.add(resident)
    db.commit()
    db.refresh(resident)
    return resident

@router.get("/{resident_id}", response_model=ResidentOut)
def get_resident(resident_id: int, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    return resident

@router.put("/{resident_id}", response_model=ResidentOut)
def update_resident(resident_id: int, resident_in: ResidentUpdate, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    update_data = resident_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resident, field, value)

    db.commit()
    db.refresh(resident)
    return resident

@router.delete("/{resident_id}")
def delete_resident(resident_id: int, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    db.delete(resident)
    db.commit()
    return {"message": "Resident deleted successfully"}
