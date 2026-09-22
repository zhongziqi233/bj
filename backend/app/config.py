import os
from datetime import timedelta


def _parse_origins(value):
    value = (value or "").strip()
    if value == "*":
        return "*"
    return [item.strip() for item in value.split(",") if item.strip()]


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRES_HOURS", "24")))
    JWT_TOKEN_LOCATION = ["headers"]

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://bullet:bullet_pass@localhost:3306/bullet_journal?charset=utf8mb4",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    CORS_ORIGINS = _parse_origins(
        os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost")
    )

    AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "true").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin123456")

