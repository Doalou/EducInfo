"""
Blueprint pour l'authentification.
Ce blueprint gère les routes et la logique liées à l'authentification des utilisateurs.
"""

from flask import Blueprint

# Création du blueprint
bp = Blueprint("auth", __name__)

# Import des routes (doit être après la création du blueprint pour éviter les imports circulaires)
from app.blueprints.auth import routes as routes  # noqa: E402
