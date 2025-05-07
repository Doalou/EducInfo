"""
Configuration de l'application EducInfo.
Ce module définit les différentes configurations possibles pour l'application.
"""
import os
from datetime import timedelta

# Chemin de base de l'application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Chemin du dossier parent (racine du projet)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
# Chemin du dossier instance pour les données spécifiques à une instance
INSTANCE_DIR = os.path.join(ROOT_DIR, 'instance')


class Config:
    """Configuration de base, commune à tous les environnements."""
    
    # Clé secrète pour les sessions et protection CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'
    
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(INSTANCE_DIR, 'educinfo.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Application configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Mo max pour les uploads
    UPLOAD_FOLDER = os.path.join(INSTANCE_DIR, 'uploads')
    
    # Logging
    LOG_FILE = os.path.join(ROOT_DIR, 'logs', 'educinfo.log')
    LOG_LEVEL = 'INFO'
    
    # Admin par défaut
    DEFAULT_ADMIN_PASSWORD = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123')
    
    # OpenWeather API configuration
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', '')  # Clé vide par défaut
    WEATHER_CITY = os.environ.get('WEATHER_CITY', 'Strasbourg')
    
    # CTS API configuration
    CTS_BASE_URL = os.environ.get('CTS_BASE_URL', 'https://api.cts-strasbourg.eu')
    CTS_API_TOKEN = os.environ.get('CTS_API_TOKEN', 'default_token')
    
    @staticmethod
    def init_app(app):
        """Initialisation spécifique à la configuration."""
        # Création des dossiers nécessaires s'ils n'existent pas
        os.makedirs(INSTANCE_DIR, exist_ok=True)
        os.makedirs(os.path.join(ROOT_DIR, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(INSTANCE_DIR, 'uploads'), exist_ok=True)


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement."""
    DEBUG = True
    DEVELOPMENT = True
    SESSION_COOKIE_SECURE = False
    TEMPLATES_AUTO_RELOAD = True
    
    @classmethod
    def init_app(cls, app):
        """Initialisation spécifique au développement."""
        Config.init_app(app)
        
        # Configuration pour le débogage
        app.config['EXPLAIN_TEMPLATE_LOADING'] = True
        
        # Messages de débogage
        import logging
        logging.info('Application lancée en mode développement')


class TestingConfig(Config):
    """Configuration pour les tests."""
    TESTING = True
    DEBUG = True
    
    # Base de données en mémoire pour les tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Désactivation de la protection CSRF pour faciliter les tests
    WTF_CSRF_ENABLED = False
    
    @classmethod
    def init_app(cls, app):
        """Initialisation spécifique aux tests."""
        Config.init_app(app)


class ProductionConfig(Config):
    """Configuration pour l'environnement de production."""
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        """Initialisation spécifique à la production."""
        Config.init_app(app)
        
        # Configuration du logging pour la production
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Création du logger pour les erreurs
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10485760,  # 10 Mo
            backupCount=10
        )
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}