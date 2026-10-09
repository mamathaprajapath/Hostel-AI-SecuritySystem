import sys
import os

# Add root folder to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base, SessionLocal
from backend.models.models import User, Resident, Parent, OutingRequest, AccessLog, UnknownEvent
from backend.utils.security import hash_password
from backend.services.face_service import reload_all_face_profiles

def seed_database():
    print("[Seed Data] Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Create Default Warden User if not exists
        admin = db.query(User).filter(User.email == "admin@hostel.edu").first()
        if not admin:
            admin = User(
                name="Chief Warden",
                email="admin@hostel.edu",
                password_hash=hash_password("admin123"),
                role="warden",
                status="active"
            )
            db.add(admin)
            print("[Seed Data] Default Warden user created: admin@hostel.edu / admin123")

        # 2. Create Sample Residents & Parents if empty
        if db.query(Resident).count() == 0:
            r1 = Resident(
                student_id="RES101",
                name="Rahul Kumar",
                room_no="A-102",
                department="Computer Science",
                phone="9876543210",
                email="rahul.k@student.edu",
                status="active",
                current_state="INSIDE"
            )
            r2 = Resident(
                student_id="RES102",
                name="Priya Sharma",
                room_no="B-205",
                department="Electronics & Comm",
                phone="9812345678",
                email="priya.s@student.edu",
                status="active",
                current_state="INSIDE"
            )
            r3 = Resident(
                student_id="RES103",
                name="Amit Patel",
                room_no="C-301",
                department="Information Tech",
                phone="9765432109",
                email="amit.p@student.edu",
                status="active",
                current_state="OUTSIDE"
            )
            db.add_all([r1, r2, r3])
            db.commit()

            # Parents
            p1 = Parent(
                hosteler_id=r1.id,
                name="Suresh Kumar",
                relationship="Father",
                phone="9899887766",
                email="suresh.k@gmail.com",
                whatsapp_number="9899887766",
                notification_preference="both"
            )
            p2 = Parent(
                hosteler_id=r2.id,
                name="Sunita Sharma",
                relationship="Mother",
                phone="9877665544",
                email="sunita.s@gmail.com",
                whatsapp_number="9877665544",
                notification_preference="both"
            )
            p3 = Parent(
                hosteler_id=r3.id,
                name="Ramesh Patel",
                relationship="Father",
                phone="9711223344",
                email="ramesh.p@gmail.com",
                whatsapp_number="9711223344",
                notification_preference="email"
            )
            db.add_all([p1, p2, p3])
            db.commit()

            print("[Seed Data] Sample residents and parents created successfully.")

        # Reload AI Face recognition models
        reload_all_face_profiles(db)

        print("[Seed Data] Database initialization & seeding completed cleanly!")
    except Exception as e:
        db.rollback()
        print(f"[Seed Data Error] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
