# AI-Enabled Unified Access and Intelligent Surveillance System for Hostelers

A comprehensive, full-stack college major project providing smart hostel security, AI face recognition access control, live gate monitoring, parent notifications, unknown person alert review, and warden administrative controls.

---

## 🌟 Features

* **AI Face Detection & Recognition**: OpenCV Haar Cascade Classifier + LBPH Face Recognizer engine.
* **Resident Registration & Face Enrollment**: Add hostelers, validate facial image format (single-face enforcement, JPG/PNG, 5MB limit), extract features and retrain AI.
* **Parent/Guardian Management**: Register parents, link to resident, set notification channel preferences (Email, WhatsApp, Both).
* **Live Smart Gate Monitor**: Real-time webcam stream (`/api/camera/stream`) with mode switching (`ENTRY` / `EXIT`), live face recognition overlay, confidence score, and automatic DB access logging.
* **Outing & Home Leave Workflow**: Resident request submission, Warden approval/rejection with remarks, and automated parent notification dispatch.
* **Parent Notifications**: Email via SMTP and WhatsApp API integration with delivery status audit logging (`notification_records`).
* **Unknown Person Management**: Automatic snapshot evidence capture for unrecognized faces, alert creation, and Warden review workflow.
* **Warden Dashboard**: Live statistics for total hostelers, inside/outside count, today's entry/exit counts, pending leave requests, and security alerts.

---

## 🏗️ Project Architecture

```text
Major-Project/
├── backend/
│   ├── main.py                  # Main FastAPI Application & Frontend Static Mounting
│   ├── config.py                # Configuration Settings (.env parser)
│   ├── database.py              # SQLAlchemy Engine (MySQL / SQLite fallback)
│   ├── models/
│   │   └── models.py            # Database Entities
│   ├── schemas/
│   │   └── schemas.py           # Pydantic Request/Response Models
│   ├── routes/                  # REST API Route Handlers
│   │   ├── auth_routes.py
│   │   ├── resident_routes.py
│   │   ├── parent_routes.py
│   │   ├── face_routes.py
│   │   ├── access_routes.py
│   │   ├── outing_routes.py
│   │   ├── unknown_routes.py
│   │   ├── camera_routes.py
│   │   ├── notification_routes.py
│   │   └── dashboard_routes.py
│   ├── services/
│   │   ├── face_service.py      # Face Enrollment & Training
│   │   ├── camera_service.py    # Webcam Stream & AI Gate Engine
│   │   └── notification_service.py # Email & WhatsApp Dispatcher
│   └── utils/
│       └── security.py          # Password Hashing & JWT
├── frontend/                    # Web Interface
│   ├── index.html               # Admin Dashboard
│   ├── monitor.html             # Live Camera Gate Monitor
│   ├── residents.html           # Resident Hosteler Management
│   ├── parents.html             # Parent Directory
│   ├── outing_requests.html     # Leave Request Approval Workflow
│   ├── unknown_events.html      # Security Review of Unknown Alerts
│   ├── access_logs.html         # Gate & Notification Logs
│   ├── css/
│   │   └── style.css
│   └── js/
├── ai/
│   ├── face_detection.py        # OpenCV Face Detection
│   └── face_recognition.py      # LBPH Engine
├── database/
│   ├── schema.sql               # MySQL Database Schema
│   └── seed_data.py             # Database Seeding Script
├── uploads/                     # Facial Photos & Unknown Snapshots
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Requirements & Dependencies

- **Python**: 3.10+
- **OpenCV**: `opencv-python` and `opencv-contrib-python`
- **FastAPI**: `fastapi`, `uvicorn`
- **Database**: MySQL Server (or built-in SQLite fallback)

---

## 🚀 Quick Start Guide (Windows 11)

### 1. Open Terminal & Activate Environment

```powershell
# Create & Activate Virtual Environment (if needed)
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Initialize & Start Application

Run single Uvicorn command:

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🌐 Application Endpoints

- **Web Dashboard**: `http://127.0.0.1:8000/`
- **Live Gate Monitor**: `http://127.0.0.1:8000/monitor.html`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`

---

## 🔐 Default Admin Credentials

- **Email**: `admin@hostel.edu`
- **Password**: `admin123`
