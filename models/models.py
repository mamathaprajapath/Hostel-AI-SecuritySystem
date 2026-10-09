from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship as relationship_orm
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="warden")
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    outing_approvals = relationship_orm("OutingRequest", back_populates="approver")
    unknown_reviews = relationship_orm("UnknownEvent", back_populates="reviewer")


class Resident(Base):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    room_no = Column(String(20), nullable=False)
    department = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    photo_path = Column(String(255), nullable=True)
    face_enrolled = Column(Boolean, default=False)
    status = Column(String(20), default="active")  # active, inactive
    current_state = Column(String(20), default="INSIDE")  # INSIDE, OUTSIDE
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parents = relationship_orm("Parent", back_populates="resident", cascade="all, delete-orphan")
    face_profile = relationship_orm("FaceProfile", back_populates="resident", uselist=False, cascade="all, delete-orphan")
    access_logs = relationship_orm("AccessLog", back_populates="resident", cascade="all, delete-orphan")
    outing_requests = relationship_orm("OutingRequest", back_populates="resident", cascade="all, delete-orphan")
    notifications = relationship_orm("NotificationRecord", back_populates="resident")


class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    hosteler_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    relationship = Column(String(50), nullable=False)  # Father, Mother, Guardian
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    whatsapp_number = Column(String(20), nullable=True)
    notification_preference = Column(String(20), default="both")  # email, whatsapp, both, none
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resident = relationship_orm("Resident", back_populates="parents")


class FaceProfile(Base):
    __tablename__ = "face_profiles"

    id = Column(Integer, primary_key=True, index=True)
    hosteler_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), unique=True, nullable=False)
    embedding_data = Column(Text, nullable=False)  # JSON formatted feature vector
    sample_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resident = relationship_orm("Resident", back_populates="face_profile")


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    hosteler_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(20), nullable=False, index=True)  # ENTRY, EXIT
    event_time = Column(DateTime, default=datetime.utcnow, index=True)
    gate = Column(String(50), default="Main Gate")
    confidence = Column(Float, default=0.0)
    source = Column(String(50), default="Camera 1")
    image_snapshot = Column(String(255), nullable=True)

    resident = relationship_orm("Resident", back_populates="access_logs")


class OutingRequest(Base):
    __tablename__ = "outing_requests"

    id = Column(Integer, primary_key=True, index=True)
    hosteler_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False)
    request_type = Column(String(20), default="OUTING")  # OUTING, HOME
    reason = Column(Text, nullable=False)
    destination = Column(String(255), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    expected_return = Column(DateTime, nullable=False)
    actual_exit_time = Column(DateTime, nullable=True)
    actual_return_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="PENDING", index=True)  # PENDING, APPROVED, REJECTED, EXITED, RETURNED
    remarks = Column(Text, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resident = relationship_orm("Resident", back_populates="outing_requests")
    approver = relationship_orm("User", back_populates="outing_approvals")


class UnknownEvent(Base):
    __tablename__ = "unknown_events"

    id = Column(Integer, primary_key=True, index=True)
    captured_at = Column(DateTime, default=datetime.utcnow)
    gate = Column(String(50), default="Main Gate")
    image_path = Column(String(255), nullable=False)
    review_status = Column(String(20), default="PENDING", index=True)  # PENDING, REVIEWED, RESOLVED, DISMISSED
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    remarks = Column(Text, nullable=True)

    reviewer = relationship_orm("User", back_populates="unknown_reviews")


class NotificationRecord(Base):
    __tablename__ = "notification_records"

    id = Column(Integer, primary_key=True, index=True)
    hosteler_id = Column(Integer, ForeignKey("residents.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(50), nullable=False)  # OUTING_APPROVED, OUTING_REJECTED, EXIT_DETECTED, RETURN_DETECTED
    channel = Column(String(20), nullable=False)  # EMAIL, WHATSAPP
    recipient = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="SENT", index=True)  # SENT, FAILED, PENDING
    error_message = Column(Text, nullable=True)

    resident = relationship_orm("Resident", back_populates="notifications")
