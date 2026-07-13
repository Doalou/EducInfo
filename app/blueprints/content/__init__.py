from flask import Blueprint

bp = Blueprint("content", __name__, url_prefix="/admin/content")

from app.blueprints.content import routes  # noqa: E402,F401
