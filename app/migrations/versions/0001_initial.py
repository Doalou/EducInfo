"""Schéma initial EducInfo 3."""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(80), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("session_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True)),
        sa.CheckConstraint("role IN ('admin', 'editor')", name="valid_user_role"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])
    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_name", sa.String(100), nullable=False),
        sa.Column("weather_city", sa.String(100), nullable=False),
        sa.Column("show_weather", sa.Boolean(), nullable=False),
        sa.Column("show_menu", sa.Boolean(), nullable=False),
        sa.Column("show_transport", sa.Boolean(), nullable=False),
        sa.Column("cts_stop_code", sa.String(20), nullable=False),
        sa.Column("cts_stop_label", sa.String(100), nullable=False),
        sa.Column("cts_vehicle_mode", sa.String(20), nullable=False),
        sa.CheckConstraint("id = 1", name="settings_singleton"),
    )
    op.create_table(
        "absences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("professeur", sa.String(100), nullable=False),
        *[
            sa.Column(day, sa.Boolean(), nullable=True)
            for day in ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi")
        ],
        sa.UniqueConstraint("professeur"),
    )
    op.create_index("ix_absences_professeur", "absences", ["professeur"], unique=True)
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_table(
        "menu_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("icons", sa.String(32), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.CheckConstraint("category BETWEEN 1 AND 5", name="valid_menu_category"),
    )
    op.create_index("idx_menu_date_category", "menu_items", ["date", "category", "order"])


def downgrade():
    for table in ("menu_items", "events", "absences", "app_settings", "users"):
        op.drop_table(table)
