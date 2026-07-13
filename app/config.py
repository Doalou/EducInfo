"""Configuration de l'application EducInfo 3."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

INSTANCE_DIR = Path(os.getenv("INSTANCE_PATH", Path.cwd() / "instance")).resolve()


def _as_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    APP_NAME = "EducInfo"
    APP_VERSION = "3.0.0"
    APP_SCHEMA_REVISION = "0002_display_theme"
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{(INSTANCE_DIR / 'educinfo.db').as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "connect_args": {"check_same_thread": False, "timeout": 30},
    }
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _as_bool("SESSION_COOKIE_SECURE", True)
    WTF_CSRF_TIME_LIMIT = 3600
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    WEATHER_CITY = os.getenv("WEATHER_CITY", "Strasbourg")
    CTS_API_TOKEN = os.getenv("CTS_API_TOKEN", "")
    CTS_BASE_URL = os.getenv("CTS_BASE_URL", "https://api.cts-strasbourg.eu")
    DEMO_MODE = _as_bool("DEMO_MODE")

    @classmethod
    def init_app(cls, app) -> None:
        INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
        if app.config.get("ENVIRONMENT") == "production" and not app.config.get("SECRET_KEY"):
            raise RuntimeError("SECRET_KEY doit être définie en production")


class DevelopmentConfig(Config):
    ENVIRONMENT = "development"
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")


class TestingConfig(Config):
    ENVIRONMENT = "testing"
    TESTING = True
    SECRET_KEY = "testing-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    ENVIRONMENT = "production"
    DEBUG = False


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
