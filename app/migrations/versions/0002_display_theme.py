"""Ajoute le thème de l'écran public."""

import sqlalchemy as sa
from alembic import op

revision = "0002_display_theme"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("app_settings") as batch_op:
        batch_op.add_column(sa.Column("dark_mode", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table("app_settings") as batch_op:
        batch_op.drop_column("dark_mode")
