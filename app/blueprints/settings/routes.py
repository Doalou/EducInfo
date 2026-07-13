from flask import current_app, flash, redirect, render_template, url_for
from flask_login import current_user

from app.blueprints.settings import bp
from app.blueprints.settings.forms import SettingsForm, UserForm, UserPasswordForm, UserUpdateForm
from app.extensions import db
from app.models import AppSettings, User
from app.utils.decorators import admin_required


@bp.route("", methods=["GET", "POST"])
@admin_required
def index():
    settings = AppSettings.get()
    form = SettingsForm(obj=settings)
    if form.validate_on_submit():
        form.populate_obj(settings)
        db.session.commit()
        current_app.extensions["external_cache"].clear()
        flash("Paramètres enregistrés.", "success")
        return redirect(url_for("settings.index"))
    return render_template(
        "admin/settings.html",
        form=form,
        weather_key_configured=bool(current_app.config.get("WEATHER_API_KEY")),
        cts_token_configured=bool(current_app.config.get("CTS_API_TOKEN")),
    )


@bp.get("/users")
@admin_required
def users():
    return render_template(
        "admin/users.html", users=User.query.order_by(User.username).all(), form=UserForm()
    )


@bp.post("/users")
@admin_required
def create_user():
    form = UserForm()
    if form.validate_on_submit() and not User.query.filter_by(username=form.username.data.strip()).first():
        user = User(username=form.username.data.strip(), role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Compte créé.", "success")
    else:
        flash("Impossible de créer ce compte.", "error")
    return redirect(url_for("settings.users"))


@bp.post("/users/<int:user_id>")
@admin_required
def update_user(user_id):
    user = db.get_or_404(User, user_id)
    form = UserUpdateForm()
    if not form.validate_on_submit():
        flash("Modification de compte invalide.", "error")
    elif user.id == current_user.id and (form.role.data != User.ROLE_ADMIN or not form.is_active.data):
        flash("Vous ne pouvez pas retirer vos propres droits administrateur.", "error")
    elif (
        user.is_admin
        and (form.role.data != User.ROLE_ADMIN or not form.is_active.data)
        and _active_admin_count() <= 1
    ):
        flash("Le dernier administrateur actif doit être conservé.", "error")
    else:
        changed = user.role != form.role.data or user.is_active != form.is_active.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        if changed:
            user.invalidate_sessions()
        db.session.commit()
        flash("Compte mis à jour.", "success")
    return redirect(url_for("settings.users"))


@bp.post("/users/<int:user_id>/password")
@admin_required
def change_user_password(user_id):
    user = db.get_or_404(User, user_id)
    form = UserPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.invalidate_sessions()
        db.session.commit()
        flash("Mot de passe changé ; les sessions du compte ont été invalidées.", "success")
    else:
        flash("Le mot de passe doit contenir au moins 12 caractères et être confirmé.", "error")
    return redirect(url_for("settings.users"))


@bp.post("/users/<int:user_id>/delete")
@admin_required
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash("Vous ne pouvez pas supprimer votre propre compte.", "error")
    elif user.is_admin and user.is_active and _active_admin_count() <= 1:
        flash("Le dernier administrateur ne peut pas être supprimé.", "error")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("Compte supprimé.", "success")
    return redirect(url_for("settings.users"))


@bp.post("/cache/clear")
@admin_required
def clear_cache():
    current_app.extensions["external_cache"].clear()
    flash("Cache des services externes vidé.", "success")
    return redirect(url_for("settings.index"))


def _active_admin_count() -> int:
    return User.query.filter_by(role=User.ROLE_ADMIN, is_active=True).count()
