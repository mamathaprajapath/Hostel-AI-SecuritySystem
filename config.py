import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AI Hostel Security System")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hostel_security.db")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "ai-hostel-security-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

    CAMERA_INDEX: int = int(os.getenv("CAMERA_INDEX", 0))

    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
    ENABLE_EMAIL: bool = os.getenv("ENABLE_EMAIL", "False").lower() == "true"

    WHATSAPP_API_URL: str = os.getenv("WHATSAPP_API_URL", "")
    WHATSAPP_API_TOKEN: str = os.getenv("WHATSAPP_API_TOKEN", "")
    ENABLE_WHATSAPP: bool = os.getenv("ENABLE_WHATSAPP", "False").lower() == "true"

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
    FACES_DIR = os.path.join(UPLOADS_DIR, "faces")
    UNKNOWN_DIR = os.path.join(UPLOADS_DIR, "unknown")

settings = Settings()

os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.FACES_DIR, exist_ok=True)
os.makedirs(settings.UNKNOWN_DIR, exist_ok=True)
