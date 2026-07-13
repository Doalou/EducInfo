from flask import Blueprint

bp = Blueprint("display", __name__)

from app.blueprints.display import routes  # noqa: E402,F401
