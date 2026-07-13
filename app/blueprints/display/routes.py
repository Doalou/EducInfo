from flask import current_app, jsonify, render_template

from app.blueprints.display import bp
from app.models import AppSettings


@bp.get("/")
def index():
    return render_template("display/index.html", dark_mode=AppSettings.get().dark_mode)


@bp.get("/internal/display")
def data():
    response = jsonify(current_app.extensions["display_service"].snapshot())
    response.headers["Cache-Control"] = "no-store"
    return response
