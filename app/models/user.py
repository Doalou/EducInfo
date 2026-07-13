"""Comptes et rôles de l'administration."""

from datetime import UTC, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    ROLE_ADMIN = "admin"
    ROLE_EDITOR = "editor"
    ROLES = (ROLE_ADMIN, ROLE_EDITOR)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(16), nullable=False, default=ROLE_EDITOR, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    session_version = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    last_login = db.Column(db.DateTime(timezone=True))

    __table_args__ = (db.CheckConstraint("role IN ('admin', 'editor')", name="valid_user_role"),)

    @property
    def is_admin(self) -> bool:
        return self.role == self.ROLE_ADMIN

    @is_admin.setter
    def is_admin(self, value: bool) -> None:
        self.role = self.ROLE_ADMIN if value else self.ROLE_EDITOR

    @property
    def is_editor(self) -> bool:
        return self.role in self.ROLES

    def get_id(self) -> str:
        return f"{self.id}:{self.session_version}"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def invalidate_sessions(self) -> None:
        self.session_version += 1

    def update_last_login(self) -> None:
        self.last_login = datetime.now(UTC)

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"
