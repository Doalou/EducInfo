"""
Gestionnaires d'erreurs HTTP pour l'application.
Ce module définit les réponses aux différentes erreurs HTTP.
"""
from flask import render_template, request, current_app
from flask_login import current_user
from app.blueprints.errors import bp
from app.extensions import db, logger

@bp.app_errorhandler(404)
def not_found_error(error):
    """Gestionnaire pour l'erreur 404 (Page non trouvée)."""
    logger.warning(f'Page non trouvée: {request.url}')
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    """Gestionnaire pour l'erreur 500 (Erreur interne du serveur)."""
    logger.error(f'Erreur serveur: {error}')
    db.session.rollback()
    return render_template('errors/500.html'), 500

@bp.app_errorhandler(403)
def forbidden_error(error):
    """Gestionnaire pour l'erreur 403 (Accès interdit)."""
    user_info = current_user.username if not current_user.is_anonymous else "anonyme"
    logger.warning(f'Accès interdit: {request.url} par {user_info}')
    return render_template('errors/403.html'), 403

@bp.app_errorhandler(401)
def unauthorized_error(error):
    """Gestionnaire pour l'erreur 401 (Non autorisé)."""
    logger.warning(f'Accès non autorisé: {request.url}')
    return render_template('errors/401.html'), 401

@bp.app_errorhandler(405)
def method_not_allowed_error(error):
    """Gestionnaire pour l'erreur 405 (Méthode non autorisée)."""
    logger.warning(f'Méthode non autorisée: {request.method} {request.url}')
    return render_template('errors/405.html'), 405

@bp.app_errorhandler(Exception)
def handle_unhandled_error(error):
    """Gestionnaire pour les erreurs non gérées."""
    logger.error(f'Erreur non gérée: {error}', exc_info=True)
    return render_template('errors/500.html'), 500 