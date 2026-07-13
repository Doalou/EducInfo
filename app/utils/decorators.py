"""Decorateurs personnalises pour EducInfo."""
from functools import wraps
from flask import flash, abort
from flask_login import current_user, login_required


def admin_required(f):
    """Restreint l'acces aux administrateurs uniquement."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("Acces reserve aux administrateurs.", "danger")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
