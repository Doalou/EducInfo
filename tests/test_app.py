from datetime import date

from app.extensions import db
from app.models import Absence, AppSettings, MenuItem, User


def test_display_page_is_local_and_hardened(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"cdn." not in response.data
    assert "unsafe-inline" not in response.headers["Content-Security-Policy"]


def test_internal_display_contract(client):
    response = client.get("/internal/display")
    payload = response.get_json()
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert set(payload) == {
        "generated_at",
        "site",
        "widgets",
        "absences",
        "events",
        "menu",
        "weather",
        "transport",
    }
    assert payload["weather"]["status"] == "unavailable"
    assert payload["transport"]["status"] == "disabled"


def test_health_endpoints(client):
    assert client.get("/health/live").get_json()["version"] == "3.0.0"
    assert client.get("/health/ready").get_json()["database"] == "ok"


def test_login_rejects_bad_credentials(client):
    response = client.post("/auth/login", data={"username": "admin", "password": "wrong"})
    assert b"incorrect" in response.data


def test_login_is_throttled(client):
    for _ in range(5):
        client.post("/auth/login", data={"username": "admin", "password": "wrong"})
    response = client.post("/auth/login", data={"username": "admin", "password": "wrong"})
    assert response.status_code == 429


def test_login_ignores_external_next(client):
    response = client.post(
        "/auth/login?next=https://evil.example",
        data={"username": "admin", "password": "correct-horse-battery-staple"},
    )
    assert response.status_code == 302
    assert response.location.endswith("/admin/content")


def test_logout_requires_post(client, login):
    login()
    assert client.get("/auth/logout").status_code == 405
    assert client.post("/auth/logout").status_code == 302


def test_editor_can_manage_content(client, login, app):
    login("editor")
    response = client.post("/admin/content/absences", data={"professeur": "Mme Martin", "lundi": "y"})
    assert response.status_code == 302
    client.post(
        "/admin/content/events",
        data={"title": "Conseil", "date": date.today().isoformat(), "description": "Salle 2"},
    )
    client.post(
        "/admin/content/menu",
        data={
            "name": "Lasagnes",
            "category": "2",
            "date": date.today().isoformat(),
            "description": "",
            "icons": "🌱",
        },
    )
    with app.app_context():
        assert Absence.query.filter_by(professeur="Mme Martin").one().lundi
        assert MenuItem.query.filter_by(name="Lasagnes").one().category_label == "Plat principal"


def test_absence_requires_a_day(client, login, app):
    login("editor")
    client.post("/admin/content/absences", data={"professeur": "Sans jour"})
    with app.app_context():
        assert Absence.query.filter_by(professeur="Sans jour").first() is None


def test_editor_cannot_access_settings(client, login):
    login("editor")
    assert client.get("/admin/settings").status_code == 403
    assert client.get("/admin/settings/users").status_code == 403


def test_admin_updates_settings(client, login, app):
    login()
    response = client.post(
        "/admin/settings",
        data={
            "site_name": "Collège",
            "weather_city": "Colmar",
            "show_menu": "y",
            "dark_mode": "y",
            "cts_vehicle_mode": "undefined",
        },
    )
    assert response.status_code == 302
    with app.app_context():
        settings = AppSettings.get()
        assert settings.site_name == "Collège" and settings.dark_mode
    assert client.get("/internal/display").get_json()["site"]["theme"] == "dark"
    assert b"theme-dark" in client.get("/").data


def test_admin_creates_and_deletes_editor(client, login, app):
    login()
    client.post(
        "/admin/settings/users",
        data={
            "username": "news",
            "role": "editor",
            "password": "a-very-long-password",
            "password_confirm": "a-very-long-password",
        },
    )
    with app.app_context():
        user_id = User.query.filter_by(username="news").one().id
    client.post(f"/admin/settings/users/{user_id}/delete")
    with app.app_context():
        assert db.session.get(User, user_id) is None


def test_admin_updates_role_status_and_password(client, login, app):
    login()
    with app.app_context():
        editor = User.query.filter_by(username="editor").one()
        user_id = editor.id
        previous_version = editor.session_version
    client.post(
        f"/admin/settings/users/{user_id}",
        data={"role": "admin", "is_active": "y"},
    )
    client.post(
        f"/admin/settings/users/{user_id}/password",
        data={"password": "a-new-long-password", "password_confirm": "a-new-long-password"},
    )
    with app.app_context():
        editor = db.session.get(User, user_id)
        assert editor.role == "admin" and editor.is_active
        assert editor.check_password("a-new-long-password")
        assert editor.session_version == previous_version + 2


def test_last_active_admin_cannot_disable_self(client, login, app):
    login()
    with app.app_context():
        admin_id = User.query.filter_by(username="admin").one().id
    client.post(
        f"/admin/settings/users/{admin_id}",
        data={"role": "editor"},
    )
    with app.app_context():
        admin = db.session.get(User, admin_id)
        assert admin.role == "admin" and admin.is_active


def test_user_session_version_and_roles(app):
    with app.app_context():
        user = User.query.filter_by(username="editor").one()
        identity = user.get_id()
        user.invalidate_sessions()
        assert user.get_id() != identity
        assert user.is_editor and not user.is_admin


def test_not_found_uses_shared_error_page(client):
    response = client.get("/missing")
    assert response.status_code == 404
    assert b"404" in response.data
