from datetime import date, timedelta

import pytest
from sqlalchemy import text

from app import create_app
from app.extensions import db
from app.models import AppSettings, Event, User


@pytest.fixture()
def app(tmp_path):
    app = create_app(
        "testing",
        {
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
            "WTF_CSRF_ENABLED": False,
            "WEATHER_API_KEY": "",
            "CTS_API_TOKEN": "",
        },
    )
    with app.app_context():
        db.create_all()
        db.session.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        db.session.execute(text("INSERT INTO alembic_version VALUES ('0002_display_theme')"))
        AppSettings.get()
        admin = User(username="admin", role="admin")
        admin.set_password("correct-horse-battery-staple")
        editor = User(username="editor", role="editor")
        editor.set_password("correct-horse-battery-staple")
        db.session.add_all([admin, editor, Event(title="Réunion", date=date.today() + timedelta(days=2))])
        db.session.commit()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login(client):
    def authenticate(username="admin", password="correct-horse-battery-staple"):
        return client.post("/auth/login", data={"username": username, "password": password})

    return authenticate
