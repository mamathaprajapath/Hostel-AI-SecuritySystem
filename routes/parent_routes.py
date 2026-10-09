from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import Parent, Resident
from backend.schemas.schemas import ParentCreate, ParentUpdate, ParentOut

router = APIRouter(prefix="/api/parents", tags=["Parents"])

@router.get("", response_model=List[ParentOut])
def get_parents(hosteler_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Parent)
    if hosteler_id:
        query = query.filter(Parent.hosteler_id == hosteler_id)
    return query.order_by(Parent.created_at.desc()).all()

@router.post("", response_model=ParentOut, status_code=status.HTTP_201_CREATED)
def create_parent(parent_in: ParentCreate, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == parent_in.hosteler_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Hosteler/Resident not found")

    parent = Parent(
        hosteler_id=parent_in.hosteler_id,
        name=parent_in.name,
        relationship=parent_in.relationship,
        phone=parent_in.phone,
        email=parent_in.email,
        whatsapp_number=parent_in.whatsapp_number or parent_in.phone,
        notification_preference=parent_in.notification_preference or "both"
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)
    return parent

@router.put("/{parent_id}", response_model=ParentOut)
def update_parent(parent_id: int, parent_in: ParentUpdate, db: Session = Depends(get_db)):
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent record not found")

    update_data = parent_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(parent, field, value)

    db.commit()
    db.refresh(parent)
    return parent

@router.delete("/{parent_id}")
def delete_parent(parent_id: int, db: Session = Depends(get_db)):
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent record not found")

    db.delete(parent)
    db.commit()
    return {"message": "Parent record deleted successfully"}
