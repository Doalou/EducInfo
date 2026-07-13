"""Extensions Flask, sans initialisation ni effets de bord à l'import."""

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = "Connectez-vous pour accéder à cette page."
login_manager.login_message_category = "warning"
login_manager.session_protection = "strong"


@event.listens_for(Engine, "connect")
def configure_sqlite(connection, _record) -> None:
    """Active l'intégrité référentielle et WAL pour les bases SQLite."""
    if connection.__class__.__module__.startswith("sqlite3"):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()
