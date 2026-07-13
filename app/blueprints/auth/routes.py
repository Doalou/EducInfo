from urllib.parse import urljoin, urlsplit

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.blueprints.auth import bp
from app.blueprints.auth.forms import LoginForm
from app.extensions import db
from app.models import User


def _safe_next(target: str | None) -> bool:
    if not target:
        return False
    host = urlsplit(request.host_url)
    candidate = urlsplit(urljoin(request.host_url, target))
    return candidate.scheme in {"http", "https"} and candidate.netloc == host.netloc


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("content.index"))
    form = LoginForm()
    if form.validate_on_submit():
        throttle = current_app.extensions["login_throttle"]
        client_key = request.remote_addr or "unknown"
        if not throttle.allowed(client_key):
            flash("Trop de tentatives. Réessayez dans une minute.", "error")
            return render_template("auth/login.html", form=form), 429
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.is_active and user.check_password(form.password.data):
            throttle.succeeded(client_key)
            login_user(user, remember=form.remember.data)
            user.update_last_login()
            db.session.commit()
            target = request.args.get("next")
            return redirect(target if _safe_next(target) else url_for("content.index"))
        current_app.logger.warning("Échec de connexion pour %s", form.username.data)
        throttle.failed(client_key)
        flash("Identifiant ou mot de passe incorrect.", "error")
    return render_template("auth/login.html", form=form)


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("display.index"))
