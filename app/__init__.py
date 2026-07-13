"""Factory Flask d'EducInfo 3."""

from __future__ import annotations

import logging
import os
from logging.config import dictConfig

from flask import Flask, jsonify, render_template
from sqlalchemy import text

from app.config import CONFIGS
from app.extensions import csrf, db, login_manager, migrate
from app.integrations import ExternalDataCache, TransportClient, WeatherClient
from app.security import LoginThrottle
from app.services import DisplayService


def migrations_directory() -> str:
    """Retourne le chemin des migrations incluses dans le paquet installé."""
    return os.path.join(os.path.dirname(__file__), "migrations")


def create_app(config_name: str | None = None, test_config: dict | None = None) -> Flask:
    environment = config_name or os.getenv("APP_ENV", "development")
    config_class = CONFIGS.get(environment, CONFIGS["development"])
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    if test_config:
        app.config.update(test_config)
    config_class.init_app(app)
    _configure_logging(app)
    _init_extensions(app)
    _init_services(app)
    _register_blueprints(app)
    _register_health(app)
    _register_errors(app)
    _register_headers(app)
    return app


def _configure_logging(app: Flask) -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"default": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"handlers": ["console"], "level": "INFO"},
        }
    )
    app.logger.setLevel(logging.INFO)


def _init_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db, directory=migrations_directory())
    csrf.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(identity: str):
        try:
            user_id, version = identity.split(":", 1)
            user = db.session.get(User, int(user_id))
            return user if user and user.session_version == int(version) and user.is_active else None
        except (ValueError, TypeError):
            return None


def _init_services(app: Flask) -> None:
    cache = ExternalDataCache()
    weather = WeatherClient(cache, app.config.get("WEATHER_API_KEY", ""), app.config.get("DEMO_MODE", False))
    transport = TransportClient(cache, app.config["CTS_BASE_URL"], app.config.get("CTS_API_TOKEN", ""))
    app.extensions["external_cache"] = cache
    app.extensions["display_service"] = DisplayService(weather, transport)
    app.extensions["login_throttle"] = LoginThrottle()


def _register_blueprints(app: Flask) -> None:
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.content import bp as content_bp
    from app.blueprints.display import bp as display_bp
    from app.blueprints.settings import bp as settings_bp

    app.register_blueprint(display_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(content_bp)
    app.register_blueprint(settings_bp)


def _register_health(app: Flask) -> None:
    @app.get("/health/live")
    def live():
        return jsonify(status="ok", version=app.config["APP_VERSION"])

    @app.get("/health/ready")
    def ready():
        try:
            revision = db.session.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            expected = app.config["APP_SCHEMA_REVISION"]
            if revision != expected:
                return jsonify(status="unavailable", database="migration_required"), 503
            return jsonify(status="ready", database="ok", revision=revision)
        except Exception:
            db.session.rollback()
            app.logger.exception("Readiness check failed")
            return jsonify(status="unavailable", database="error"), 503


def _register_errors(app: Flask) -> None:
    for code in (400, 403, 404, 405):
        app.register_error_handler(
            code, lambda _error, status=code: (render_template("errors/error.html", code=status), status)
        )

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        return render_template("errors/error.html", code=500), 500


def _register_headers(app: Flask) -> None:
    @app.after_request
    def security_headers(response):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        )
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response
