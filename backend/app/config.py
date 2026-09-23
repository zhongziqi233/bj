import os
from datetime import timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_SQLITE_PATH = DEFAULT_DATA_DIR / "bullet_journal.db"


def _resolve_database_url():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    configured_path = os.getenv("SQLITE_PATH")
    sqlite_path = Path(configured_path).expanduser() if configured_path else DEFAULT_SQLITE_PATH
    return f"sqlite:///{sqlite_path.as_posix()}"


def ensure_database_directory(database_url):
    if not database_url.startswith("sqlite:///"):
        return
    sqlite_path = database_url[len("sqlite:///"):]
    if sqlite_path and sqlite_path != ":memory:":
        Path(sqlite_path).expanduser().parent.mkdir(parents=True, exist_ok=True)


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

    SQLALCHEMY_DATABASE_URI = _resolve_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = (
        {
            "connect_args": {
                "check_same_thread": False,
                "timeout": 30,
            }
        }
        if SQLALCHEMY_DATABASE_URI.startswith("sqlite")
        else {
            "pool_pre_ping": True,
            "pool_recycle": 280,
        }
    )

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
