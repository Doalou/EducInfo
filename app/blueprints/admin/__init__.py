"""
Blueprint pour l'administration.
Ce blueprint gère les routes et la logique liées à l'administration du site.
"""
from flask import Blueprint

# Création du blueprint
bp = Blueprint('admin', __name__)

# Import des routes (doit être après la création du blueprint pour éviter les imports circulaires)
from app.blueprints.admin import routes 