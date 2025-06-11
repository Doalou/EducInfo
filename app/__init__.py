"""Application principale EducInfo - Factory pattern Flask optimisé."""
import os
from flask import Flask
from app.extensions import (
    db, login_manager, logger, migrate, cache, csrf,
    init_cache, init_monitoring, init_health_check, 
    configure_security_headers, setup_logger
)
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig


def create_app(config_name=None, test_config=None):
    """Factory pour créer l'application Flask configurée."""
    app = Flask(__name__, instance_relative_config=True)
    
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    
    # Configuration
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
    
    app.config.from_prefixed_env()
    app.config.from_pyfile('config.py', silent=True)
    
    # Initialisation optimisée
    global logger
    logger = setup_logger(app)
    
    initialize_extensions(app)
    configure_security_headers(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_context_processors(app)
    register_cli_commands(app)
    
    init_monitoring(app)
    init_health_check(app)
    init_metrics_heartbeat(app)
    
    logger.info(f"EducInfo {app.config.get('APP_VERSION', '1.2.0')} initialisé en mode {config_name}")
    
    return app


def init_metrics_heartbeat(app):
    """Initialise le système de heartbeat pour les métriques en mode cluster."""
    if not app.config.get('TESTING', False):  # Pas de heartbeat en mode test
        import threading
        import time
        
        def heartbeat_worker():
            """Worker thread pour envoyer périodiquement les métriques au cache partagé."""
            while True:
                try:
                    with app.app_context():
                        from app.services.metrics import store_current_instance_metrics
                        success = store_current_instance_metrics()
                        if success:
                            app.logger.debug("Heartbeat métriques envoyé")
                        else:
                            app.logger.warning("Échec heartbeat métriques")
                except Exception as e:
                    app.logger.error(f"Erreur heartbeat métriques: {e}")
                
                # Attendre avant le prochain heartbeat
                update_interval = int(os.environ.get('METRICS_UPDATE_INTERVAL', 60))
                time.sleep(update_interval)
        
        # Démarrer le thread de heartbeat uniquement si Redis est configuré
        redis_url = app.config.get('REDIS_URL') or os.environ.get('REDIS_URL')
        if redis_url:
            heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True)
            heartbeat_thread.start()
            app.logger.info(f"Heartbeat métriques démarré (intervalle: {os.environ.get('METRICS_UPDATE_INTERVAL', 60)}s)")
        else:
            app.logger.info("Pas de Redis configuré, heartbeat métriques désactivé")


def initialize_extensions(app):
    """Initialise les extensions Flask de manière optimisée."""
    db.init_app(app)
    migrate.init_app(app, db)
    init_cache(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None
    
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import flash, redirect, url_for, request
        flash('Vous devez être connecté pour accéder à cette page.', 'warning')
        return redirect(url_for('auth.login', next=request.url))
    
    logger.info("Extensions Flask initialisées")


def register_blueprints(app):
    """Enregistre les blueprints."""
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
    
    logger.info("Blueprints enregistrés")


def register_error_handlers(app):
    """Enregistre les gestionnaires d'erreurs globaux."""
    from flask import jsonify, request
    from flask_wtf.csrf import CSRFError
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': str(e.description)
            }), 429
        return "Trop de requêtes. Veuillez réessayer plus tard.", 429
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'CSRF token missing or invalid',
                'message': str(e.description)
            }), 400
        from flask import flash, redirect, url_for
        flash('Erreur de sécurité. Veuillez réessayer.', 'error')
        return redirect(url_for('public.home'))
    
    logger.info("Gestionnaires d'erreurs configurés")


def register_context_processors(app):
    """Enregistre les processeurs de contexte."""
    from app.utils.context_processors import (
        common_context, absence_context, menu_context, register_template_filters
    )
    
    app.context_processor(common_context)
    app.context_processor(absence_context)
    app.context_processor(menu_context)
    register_template_filters(app)
    
    @app.context_processor
    def app_context():
        return {
            'app_name': app.config.get('APP_NAME', 'EducInfo'),
            'app_version': app.config.get('APP_VERSION', '1.2.0'),
            'debug_mode': app.debug
        }
    
    logger.info("Processeurs de contexte configurés")


def register_cli_commands(app):
    """Enregistre les commandes CLI personnalisées."""
    from app.cli import register_commands
    register_commands(app)
    logger.info("Commandes CLI enregistrées") 