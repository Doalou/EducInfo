"""
Blueprint pour la gestion des erreurs.
Ce blueprint gère les pages d'erreur HTTP.
"""
from flask import Blueprint

# Création du blueprint
bp = Blueprint('errors', __name__)

# Import des gestionnaires (doit être après la création du blueprint pour éviter les imports circulaires)
from app.blueprints.errors import handlers 