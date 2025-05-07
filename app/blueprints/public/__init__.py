"""
Blueprint pour les routes publiques de l'application.
Ce blueprint gère les pages accessibles à tous les utilisateurs.
"""
from flask import Blueprint

# Création du blueprint
bp = Blueprint('public', __name__)

# Import des routes (doit être après la création du blueprint pour éviter les imports circulaires)
from app.blueprints.public import routes 