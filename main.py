import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings
from backend.database import engine, Base
from database.seed_data import seed_database

# Import All Route Modules
from backend.routes.auth_routes import router as auth_router
from backend.routes.resident_routes import router as resident_router
from backend.routes.parent_routes import router as parent_router
from backend.routes.face_routes import router as face_router
from backend.routes.access_routes import router as access_router
from backend.routes.outing_routes import router as outing_router
from backend.routes.unknown_routes import router as unknown_router
from backend.routes.camera_routes import router as camera_router
from backend.routes.notification_routes import router as notification_router
from backend.routes.dashboard_routes import router as dashboard_router

# Initialize Database Schema & Initial Data
seed_database()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Enabled Unified Access and Intelligent Surveillance System for Hostelers API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router)
app.include_router(resident_router)
app.include_router(parent_router)
app.include_router(face_router)
app.include_router(access_router)
app.include_router(outing_router)
app.include_router(unknown_router)
app.include_router(camera_router)
app.include_router(notification_router)
app.include_router(dashboard_router)

# Mount Uploads directory
app.mount("/static/uploads", StaticFiles(directory=settings.UPLOADS_DIR), name="uploads")

# Frontend Directory path
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{page_name}.html", include_in_schema=False)
    async def serve_page(page_name: str):
        page_path = os.path.join(FRONTEND_DIR, f"{page_name}.html")
        if os.path.exists(page_path):
            return FileResponse(page_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
