"""
Application principale EducInfo.
Ce module initialise l'application Flask avec le pattern Factory.
"""
import os
from flask import Flask
from app.extensions import db, login_manager, logger
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig


def create_app(config_name=None, test_config=None):
    """
    Factory pattern pour créer l'application Flask.
    
    Args:
        config_name: Le nom de la configuration à utiliser (development, production, testing)
        test_config: Configuration de test à utiliser (pour les tests unitaires)
        
    Returns:
        L'application Flask configurée
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuration par défaut
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Chargement de la configuration
    if test_config:
        app.config.from_mapping(test_config)
    elif config_name == 'production':
        app.config.from_object(ProductionConfig)
        ProductionConfig.init_app(app)
    elif config_name == 'testing':
        app.config.from_object(TestingConfig)
        TestingConfig.init_app(app)
    else:
        app.config.from_object(DevelopmentConfig)
        DevelopmentConfig.init_app(app)
    
    # Chargement des variables d'environnement depuis .env
    app.config.from_prefixed_env()
    
    # Chargement de la configuration spécifique à l'instance (si elle existe)
    app.config.from_pyfile('config.py', silent=True)
    
    # Initialisation des extensions
    initialize_extensions(app)
    
    # Enregistrement des blueprints
    register_blueprints(app)
    
    # Configuration des gestionnaires d'erreurs
    register_error_handlers(app)
    
    # Configuration des processeurs de contexte
    register_context_processors(app)
    
    # Enregistrement des commandes CLI
    register_cli_commands(app)
    
    return app


def initialize_extensions(app):
    """
    Initialise les extensions Flask.
    
    Args:
        app: L'application Flask
    """
    # Initialisation de la base de données
    db.init_app(app)
    
    # Initialisation du gestionnaire de login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'warning'
    
    # Configuration du chargeur d'utilisateur pour Flask-Login
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Charge l'utilisateur à partir de son ID pour Flask-Login."""
        return User.query.get(int(user_id))
    
    # Autres extensions à initialiser ici


def register_blueprints(app):
    """
    Enregistre les blueprints.
    
    Args:
        app: L'application Flask
    """
    # Importation ici pour éviter les dépendances circulaires
    from app.blueprints.public import bp as public_bp
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.admin import bp as admin_bp
    from app.blueprints.api import bp as api_bp
    from app.blueprints.errors import bp as errors_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(errors_bp)


def register_error_handlers(app):
    """
    Enregistre les gestionnaires d'erreurs.
    
    Args:
        app: L'application Flask
    """
    # Les erreurs seront gérées par le blueprint errors


def register_context_processors(app):
    """
    Enregistre les processeurs de contexte.
    
    Args:
        app: L'application Flask
    """
    # Importation ici pour éviter les dépendances circulaires
    from app.utils.context_processors import common_context, absence_context, menu_context
    app.context_processor(common_context)
    app.context_processor(absence_context)
    app.context_processor(menu_context)


def register_cli_commands(app):
    """
    Enregistre les commandes CLI.
    
    Args:
        app: L'application Flask
    """
    from app.cli import register_commands
    register_commands(app) 