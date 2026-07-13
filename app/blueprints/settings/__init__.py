from flask import Blueprint

bp = Blueprint("settings", __name__, url_prefix="/admin/settings")

from app.blueprints.settings import routes  # noqa: E402,F401
