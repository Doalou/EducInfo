"""
Blueprint pour l'API REST.
Ce blueprint gère les routes et la logique de l'API REST.
"""
from flask import Blueprint

# Création du blueprint
bp = Blueprint('api', __name__)

# Import des routes (doit être après la création du blueprint pour éviter les imports circulaires)
from app.blueprints.api import routes 