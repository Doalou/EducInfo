"""Commande installable ``educinfo``."""

import os
import secrets

import click
from flask_migrate import upgrade

from app import create_app, migrations_directory
from app.extensions import db
from app.models import AppSettings, User


@click.group()
def main() -> None:
    """Administration locale d'EducInfo."""


@main.command("init")
def init_command() -> None:
    """Applique les migrations et initialise le premier administrateur."""
    app = create_app(os.getenv("APP_ENV", "production"))
    with app.app_context():
        upgrade(directory=migrations_directory())
        AppSettings.get()
        _ensure_admin()


@main.group("admin")
def admin_group() -> None:
    """Gestion des comptes hors interface web."""


@admin_group.command("ensure")
def ensure_admin_command() -> None:
    """Crée l'administrateur initial lorsqu'aucun compte n'existe."""
    app = create_app(os.getenv("APP_ENV", "production"))
    with app.app_context():
        _ensure_admin()


@admin_group.command("reset-password")
@click.option("--username", default="admin", show_default=True)
def reset_password_command(username: str) -> None:
    """Génère un nouveau mot de passe et invalide les sessions du compte."""
    app = create_app(os.getenv("APP_ENV", "production"))
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise click.ClickException(f"Compte introuvable : {username}")
        password = secrets.token_urlsafe(18)
        user.set_password(password)
        user.invalidate_sessions()
        db.session.commit()
        click.echo(f"Nouveau mot de passe pour {username}: {password}")
        click.echo("Ce mot de passe ne sera plus affiché.")


def _ensure_admin() -> None:
    if User.query.first() is not None:
        click.echo("Un compte existe déjà, aucune création nécessaire.")
        return
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD") or secrets.token_urlsafe(18)
    user = User(username=username, role=User.ROLE_ADMIN)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"Administrateur créé : {username}")
    if not os.getenv("ADMIN_PASSWORD"):
        click.echo(f"Mot de passe initial : {password}")
        click.echo("Ce mot de passe ne sera plus affiché.")
