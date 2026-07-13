from alembic import context
from flask import current_app

config = context.config
config.set_main_option(
    "sqlalchemy.url", str(current_app.extensions["migrate"].db.engine.url).replace("%", "%%")
)
target_metadata = current_app.extensions["migrate"].db.metadata


def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with current_app.extensions["migrate"].db.engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_offline() if context.is_offline_mode() else run_migrations_online()
