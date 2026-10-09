from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# User / Auth Schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "warden"

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# Resident Schemas
class ResidentBase(BaseModel):
    student_id: str
    name: str
    room_no: str
    department: str
    phone: str
    email: Optional[EmailStr] = None

class ResidentCreate(ResidentBase):
    pass

class ResidentUpdate(BaseModel):
    name: Optional[str] = None
    room_no: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None

class ResidentOut(ResidentBase):
    id: int
    photo_path: Optional[str] = None
    face_enrolled: bool
    status: str
    current_state: str
    created_at: datetime

    class Config:
        from_attributes = True

# Parent Schemas
class ParentBase(BaseModel):
    hosteler_id: int
    name: str
    relationship: str
    phone: str
    email: EmailStr
    whatsapp_number: Optional[str] = None
    notification_preference: Optional[str] = "both"

class ParentCreate(ParentBase):
    pass

class ParentUpdate(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    whatsapp_number: Optional[str] = None
    notification_preference: Optional[str] = None

class ParentOut(ParentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Outing Request Schemas
class OutingCreate(BaseModel):
    hosteler_id: int
    request_type: str = "OUTING"  # OUTING or HOME
    reason: str
    destination: str
    departure_time: datetime
    expected_return: datetime

class OutingStatusUpdate(BaseModel):
    status: str  # APPROVED, REJECTED
    remarks: Optional[str] = None

class OutingOut(BaseModel):
    id: int
    hosteler_id: int
    request_type: str
    reason: str
    destination: str
    departure_time: datetime
    expected_return: datetime
    actual_exit_time: Optional[datetime] = None
    actual_return_time: Optional[datetime] = None
    status: str
    remarks: Optional[str] = None
    approved_by: Optional[int] = None
    created_at: datetime
    resident: Optional[ResidentOut] = None

    class Config:
        from_attributes = True

# Access Log Schemas
class AccessLogCreate(BaseModel):
    hosteler_id: int
    event_type: str  # ENTRY, EXIT
    gate: Optional[str] = "Main Gate"
    confidence: Optional[float] = 0.0
    source: Optional[str] = "Manual/AI"

class AccessLogOut(BaseModel):
    id: int
    hosteler_id: int
    event_type: str
    event_time: datetime
    gate: str
    confidence: float
    source: str
    image_snapshot: Optional[str] = None
    resident: Optional[ResidentOut] = None

    class Config:
        from_attributes = True

# Unknown Event Schemas
class UnknownEventUpdate(BaseModel):
    review_status: str  # REVIEWED, RESOLVED, DISMISSED
    remarks: Optional[str] = None

class UnknownEventOut(BaseModel):
    id: int
    captured_at: datetime
    gate: str
    image_path: str
    review_status: str
    reviewed_by: Optional[int] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True

# Dashboard Stats Schema
class DashboardStats(BaseModel):
    total_residents: int
    residents_inside: int
    residents_outside: int
    today_entries: int
    today_exits: int
    pending_outings: int
    unknown_alerts: int
