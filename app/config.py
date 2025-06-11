"""Configuration optimisée de l'application EducInfo."""
import os
from datetime import timedelta
import secrets

# Chemins de base
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
INSTANCE_DIR = os.path.join(ROOT_DIR, 'instance')


class Config:
    """Configuration de base, commune à tous les environnements."""
    
    APP_VERSION = "1.2.0"
    APP_NAME = "EducInfo"
    
    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    BCRYPT_LOG_ROUNDS = 12
    
    # Base de données optimisée
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(INSTANCE_DIR, "educinfo.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'check_same_thread': False,
            'timeout': 30
        } if 'sqlite' in os.environ.get('DATABASE_URL', 'sqlite') else {}
    }
    
    # Sessions
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF Protection
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_SSL_STRICT = True
    
    # Application
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(INSTANCE_DIR, 'uploads')
    
    # Logging optimisé
    LOG_FILE = os.path.join(ROOT_DIR, 'logs', 'educinfo.log')
    LOG_LEVEL = 'INFO'
    LOG_MAX_BYTES = 10 * 1024 * 1024
    LOG_BACKUP_COUNT = 5
    
    # Cache configuration optimisée
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
    CACHE_KEY_PREFIX = 'educinfo'
    
    # Timeouts de cache spécialisés
    CACHE_TIMEOUTS = {
        'weather': int(os.environ.get('WEATHER_CACHE_TIMEOUT', '1800')),
        'transport': int(os.environ.get('CTS_CACHE_TIMEOUT', '60')),
        'menu': int(os.environ.get('MENU_CACHE_TIMEOUT', '3600')),
        'config': int(os.environ.get('CONFIG_CACHE_TIMEOUT', '7200')),
        'stats': int(os.environ.get('STATS_CACHE_TIMEOUT', '300'))
    }
    
    # Redis optimisé
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_DECODE_RESPONSES = True
    REDIS_SOCKET_CONNECT_TIMEOUT = 5
    REDIS_SOCKET_TIMEOUT = 5
    REDIS_CONNECTION_POOL_KWARGS = {
        'max_connections': 20,
        'retry_on_timeout': True,
        'health_check_interval': 30
    }
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'redis://localhost:6379/1')
    RATELIMIT_DEFAULT = "100 per hour"
    
    # API externes
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', '')
    WEATHER_CITY = os.environ.get('WEATHER_CITY', 'Strasbourg')
    CTS_BASE_URL = os.environ.get('CTS_BASE_URL', 'https://api.cts-strasbourg.eu')
    CTS_API_TOKEN = os.environ.get('CTS_API_TOKEN', '')
    
    # Admin par défaut
    DEFAULT_ADMIN_USERNAME = os.environ.get('DEFAULT_ADMIN_USERNAME', 'admin')
    DEFAULT_ADMIN_PASSWORD = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123')
    
    # JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Monitoring
    PROMETHEUS_ENABLED = os.environ.get('PROMETHEUS_ENABLED', 'false').lower() == 'true'
    HEALTH_CHECK_PATH = '/health'
    
    @staticmethod
    def init_app(app):
        """Initialisation spécifique à la configuration."""
        os.makedirs(INSTANCE_DIR, exist_ok=True)
        os.makedirs(os.path.join(ROOT_DIR, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(INSTANCE_DIR, 'uploads'), exist_ok=True)
        
        # Test Redis et fallback automatique
        try:
            import redis
            redis_client = redis.from_url(app.config['REDIS_URL'])
            redis_client.ping()
            app.config['CACHE_TYPE'] = 'redis'
            app.config['CACHE_REDIS_URL'] = app.config['REDIS_URL']
        except (ImportError, Exception):
            app.config['CACHE_TYPE'] = 'simple'


class DevelopmentConfig(Config):
    """Configuration développement optimisée."""
    DEBUG = True
    DEVELOPMENT = True
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_SSL_STRICT = False
    TEMPLATES_AUTO_RELOAD = True
    
    # Cache plus court en développement
    WEATHER_CACHE_TIMEOUT = 300
    CTS_CACHE_TIMEOUT = 30
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        app.config['EXPLAIN_TEMPLATE_LOADING'] = False
        
        import logging
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.info('Application lancée en mode développement')


class TestingConfig(Config):
    """Configuration tests optimisée."""
    TESTING = True
    DEBUG = True
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    CACHE_TYPE = 'simple'
    
    WEATHER_CACHE_TIMEOUT = 1
    CTS_CACHE_TIMEOUT = 1
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class ProductionConfig(Config):
    """Configuration production optimisée."""
    DEBUG = False
    
    BCRYPT_LOG_ROUNDS = 15
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_SSL_STRICT = True
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        import logging
        from logging.handlers import RotatingFileHandler, SysLogHandler
        
        # Logger avec rotation
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=app.config['LOG_MAX_BYTES'],
            backupCount=app.config['LOG_BACKUP_COUNT']
        )
        file_handler.setLevel(logging.WARNING)
        
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] [%(pathname)s:%(lineno)d] %(message)s'
        )
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        
        # Syslog optionnel
        if os.environ.get('SYSLOG_ENABLED', 'false').lower() == 'true':
            syslog_handler = SysLogHandler()
            syslog_handler.setLevel(logging.ERROR)
            syslog_handler.setFormatter(formatter)
            app.logger.addHandler(syslog_handler)
        
        app.logger.setLevel(logging.WARNING)
        app.logger.info('EducInfo démarré en mode production')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}