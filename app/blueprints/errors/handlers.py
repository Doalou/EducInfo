"""Gestionnaires d'erreurs HTTP pour l'application."""
from flask import render_template, request, url_for
from flask_login import current_user
from app.blueprints.errors import bp
from app.extensions import db, logger


# Configuration des pages d'erreur
ERROR_PAGES = {
    401: {
        'color_primary': '#3b82f6', 'color_hover': '#2563eb',
        'icon_path': 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
        'error_title': 'Authentification requise',
        'error_description': 'Vous devez etre connecte pour acceder a cette page.',
        'suggestions': [
            'Authentification requise pour continuer',
            'Utilisez vos identifiants de connexion',
            "Contactez l'administrateur si necessaire",
        ],
        'primary_label': 'Se connecter',
        'secondary_label': "Page d'accueil",
        'secondary_action': "window.location.href='/'",
    },
    403: {
        'color_primary': '#f59e0b', 'color_hover': '#d97706',
        'icon_path': 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
        'error_title': "Zone d'acces restreint",
        'error_description': "Vous n'avez pas les permissions necessaires pour acceder a cette ressource.",
        'suggestions': [
            'Permissions insuffisantes pour cette ressource',
            'Contactez votre administrateur systeme',
            "Verifiez vos droits d'acces",
        ],
        'primary_label': "Page d'accueil",
        'secondary_label': 'Retour',
        'secondary_action': 'history.back()',
    },
    404: {
        'color_primary': '#6366f1', 'color_hover': '#4f46e5',
        'icon_path': 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
        'error_title': 'Page introuvable',
        'error_description': "La page que vous recherchez n'existe pas ou a ete deplacee.",
        'suggestions': [
            "Verifiez l'orthographe de l'URL",
            'Utilisez le menu de navigation',
            "Retournez a la page d'accueil",
        ],
        'primary_label': "Page d'accueil",
        'secondary_label': 'Retour',
        'secondary_action': 'history.back()',
    },
    405: {
        'color_primary': '#8b5cf6', 'color_hover': '#7c3aed',
        'icon_path': 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636',
        'error_title': 'Methode non supportee',
        'error_description': "La methode HTTP utilisee n'est pas supportee pour cette ressource.",
        'suggestions': [
            "La methode HTTP n'est pas supportee",
            'Verifiez les parametres de la requete',
            "Consultez la documentation de l'API",
        ],
        'primary_label': "Page d'accueil",
        'secondary_label': 'Retour',
        'secondary_action': 'history.back()',
    },
    500: {
        'color_primary': '#ef4444', 'color_hover': '#dc2626',
        'icon_path': 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
        'error_title': 'Erreur interne du serveur',
        'error_description': "Une erreur inattendue s'est produite. Notre equipe a ete notifiee.",
        'suggestions': [
            'Equipe technique notifiee automatiquement',
            'Resolution en cours de traitement',
            'Veuillez reessayer dans quelques instants',
        ],
        'primary_label': "Page d'accueil",
        'secondary_label': 'Recharger',
        'secondary_action': 'window.location.reload()',
    },
}


def _render_error(code):
    """Rend une page d'erreur avec le template partage."""
    config = ERROR_PAGES[code]
    if code == 401:
        try:
            config['primary_url'] = url_for('auth.login')
        except Exception:
            config['primary_url'] = '/auth/login'
    else:
        try:
            config['primary_url'] = url_for('public.home')
        except Exception:
            config['primary_url'] = '/'
    return render_template('errors/_error_base.html', error_code=code, **config), code


@bp.app_errorhandler(404)
def not_found_error(error):
    logger.warning(f'Page non trouvee: {request.url}')
    return _render_error(404)

@bp.app_errorhandler(500)
def internal_error(error):
    logger.error(f'Erreur serveur: {error}')
    db.session.rollback()
    return _render_error(500)

@bp.app_errorhandler(403)
def forbidden_error(error):
    user_info = current_user.username if not current_user.is_anonymous else "anonyme"
    logger.warning(f'Acces interdit: {request.url} par {user_info}')
    return _render_error(403)

@bp.app_errorhandler(401)
def unauthorized_error(error):
    logger.warning(f'Acces non autorise: {request.url}')
    return _render_error(401)

@bp.app_errorhandler(405)
def method_not_allowed_error(error):
    logger.warning(f'Methode non autorisee: {request.method} {request.url}')
    return _render_error(405)

@bp.app_errorhandler(Exception)
def handle_unhandled_error(error):
    logger.error(f'Erreur non geree: {error}', exc_info=True)
    return _render_error(500)
