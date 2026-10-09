import os
import time
import cv2
import numpy as np
from datetime import datetime
from threading import Lock
from sqlalchemy.orm import Session
from backend.config import settings
from backend.database import SessionLocal
from backend.models.models import Resident, AccessLog, UnknownEvent, OutingRequest
from ai.face_detection import detect_faces, crop_face
from ai.face_recognition import ai_engine
from backend.services.notification_service import send_parent_notification

class CameraService:
    def __init__(self):
        self.camera_index = settings.CAMERA_INDEX
        self.mode = "ENTRY"  # ENTRY or EXIT
        self.cap = None
        self.lock = Lock()
        self.last_access_times = {}  # hosteler_id -> timestamp
        self.last_unknown_time = 0
        self.current_frame_info = {
            "mode": "ENTRY",
            "active": False,
            "recognized_resident": None,
            "confidence": 0.0,
            "status": "IDLE",
            "timestamp": ""
        }

    def set_mode(self, mode: str):
        """Sets gate monitoring mode: ENTRY or EXIT."""
        if mode.upper() in ["ENTRY", "EXIT"]:
            self.mode = mode.upper()
            self.current_frame_info["mode"] = self.mode
            print(f"[Camera Service] Gate mode updated to: {self.mode}")

    def get_camera(self):
        """Initializes or returns active video capture."""
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW) # DSHOW for fast Windows camera init
            if not self.cap.isOpened():
                # Try fallback index 0 without DSHOW if failed
                self.cap = cv2.VideoCapture(0)
        return self.cap

    def release_camera(self):
        """Releases video capture."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def process_frame(self, frame: np.ndarray, db: Session) -> np.ndarray:
        """
        Runs AI detection & recognition on the frame, draws UI bounding boxes,
        and triggers DB logging / parent notifications.
        """
        if frame is None:
            return frame

        faces = detect_faces(frame)
        now_ts = time.time()
        time_str = datetime.now().strftime("%I:%M:%S %p")
        self.current_frame_info["timestamp"] = time_str
        self.current_frame_info["active"] = True

        # Draw Mode Banner on Video
        mode_color = (0, 255, 0) if self.mode == "ENTRY" else (0, 0, 255)
        cv2.rectangle(frame, (10, 10), (280, 50), (0, 0, 0), -1)
        cv2.putText(frame, f"GATE MODE: {self.mode}", (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)

        if len(faces) == 0:
            self.current_frame_info["status"] = "SEARCHING"
            self.current_frame_info["recognized_resident"] = None
            self.current_frame_info["confidence"] = 0.0
            return frame

        for bbox in faces:
            x, y, w, h = bbox
            face_crop = crop_face(frame, bbox)

            hosteler_id, confidence, is_known = ai_engine.predict(face_crop)

            if is_known and hosteler_id is not None:
                resident = db.query(Resident).filter(Resident.id == hosteler_id).first()
                if resident:
                    label = f"{resident.name} ({confidence:.0f}%)"
                    box_color = (0, 255, 0) # Green for known

                    self.current_frame_info["recognized_resident"] = {
                        "id": resident.id,
                        "student_id": resident.student_id,
                        "name": resident.name,
                        "room_no": resident.room_no,
                        "department": resident.department
                    }
                    self.current_frame_info["confidence"] = confidence
                    self.current_frame_info["status"] = f"KNOWN: {resident.name}"

                    # Prevent duplicate logging within 15 seconds for the same resident
                    last_logged = self.last_access_times.get(resident.id, 0)
                    if now_ts - last_logged > 15:
                        self.last_access_times[resident.id] = now_ts
                        self.handle_access_event(db, resident, confidence)

                    cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
                    cv2.rectangle(frame, (x, y - 30), (x + w, y), box_color, -1)
                    cv2.putText(frame, label, (x + 5, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            else:
                # Unknown Person detected
                box_color = (0, 165, 255) # Orange for Unknown
                label = f"UNKNOWN ({confidence:.0f}%)"

                self.current_frame_info["recognized_resident"] = None
                self.current_frame_info["confidence"] = confidence
                self.current_frame_info["status"] = "UNKNOWN PERSON DETECTED"

                # Trigger Unknown Event Alert (debounce 30 seconds)
                if now_ts - self.last_unknown_time > 30:
                    self.last_unknown_time = now_ts
                    self.handle_unknown_event(db, frame, bbox)

                cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
                cv2.rectangle(frame, (x, y - 30), (x + w, y), box_color, -1)
                cv2.putText(frame, label, (x + 5, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        return frame

    def handle_access_event(self, db: Session, resident: Resident, confidence: float):
        """Creates access log, updates resident state, checks outing approvals, and notifies parents."""
        try:
            event_type = self.mode  # ENTRY or EXIT
            now_dt = datetime.now()

            log = AccessLog(
                hosteler_id=resident.id,
                event_type=event_type,
                event_time=now_dt,
                gate="Main Gate",
                confidence=confidence,
                source="Smart Surveillance Camera"
            )
            db.add(log)

            # Update resident state inside/outside
            resident.current_state = "INSIDE" if event_type == "ENTRY" else "OUTSIDE"

            # Check active outing requests for this resident
            outing = db.query(OutingRequest).filter(
                OutingRequest.hosteler_id == resident.id,
                OutingRequest.status.in_(["APPROVED", "EXITED"])
            ).order_by(OutingRequest.created_at.desc()).first()

            if outing:
                if event_type == "EXIT" and outing.status == "APPROVED":
                    outing.status = "EXITED"
                    outing.actual_exit_time = now_dt
                elif event_type == "ENTRY" and outing.status == "EXITED":
                    outing.status = "RETURNED"
                    outing.actual_return_time = now_dt

            db.commit()

            # Send Notification to Parent
            notif_msg = f"Hostel Gate Alert: Student {resident.name} ({resident.student_id}) recorded {event_type} at {now_dt.strftime('%I:%M %p on %d %b %Y')}."
            send_parent_notification(db, resident.id, f"{event_type}_DETECTED", notif_msg)

            print(f"[Access Event] Registered {event_type} for resident {resident.name} ({resident.student_id}).")
        except Exception as e:
            db.rollback()
            print(f"[Camera Service Error] Access log processing failed: {e}")

    def handle_unknown_event(self, db: Session, frame: np.ndarray, bbox: tuple):
        """Saves unknown person snapshot and creates DB event record."""
        try:
            x, y, w, h = bbox
            now_dt = datetime.now()
            timestamp_str = now_dt.strftime("%Y%m%d_%H%M%S")
            filename = f"unknown_{timestamp_str}.jpg"
            save_path = os.path.join(settings.UNKNOWN_DIR, filename)

            # Save frame snapshot
            cv2.imwrite(save_path, frame)

            unknown_rec = UnknownEvent(
                captured_at=now_dt,
                gate="Main Gate",
                image_path=f"/static/uploads/unknown/{filename}",
                review_status="PENDING",
                remarks="Unrecognized face detected at hostel main gate."
            )
            db.add(unknown_rec)
            db.commit()
            print(f"[Unknown Event] Created unknown alert snapshot: {filename}")
        except Exception as e:
            db.rollback()
            print(f"[Camera Service Error] Unknown event logging failed: {e}")

    def generate_mjpeg_stream(self):
        """Yields MJPEG stream frames for browser rendering."""
        cap = self.get_camera()
        fallback_frame_count = 0

        while True:
            db = SessionLocal()
            try:
                success, frame = cap.read()
                if not success or frame is None:
                    # Synthetic fallback frame if webcam hardware is occupied or unavailable
                    fallback_frame_count += 1
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(frame, "WEBCAM OFFLINE OR BUSY", (120, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv2.putText(frame, f"Simulating Stream ({self.mode})...", (160, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    time.sleep(0.1)

                processed_frame = self.process_frame(frame, db)

                # Encode frame to JPEG
                ret, buffer = cv2.imencode('.jpg', processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if not ret:
                    continue

                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            except Exception as e:
                print(f"[Camera Stream Error] {e}")
                time.sleep(0.1)
            finally:
                db.close()

camera_service = CameraService()
