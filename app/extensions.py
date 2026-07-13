"""Extensions Flask optimisées pour EducInfo."""
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler
import os

# Extensions principales
db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
migrate = Migrate()
cache = Cache()
limiter = Limiter(key_func=get_remote_address, default_limits=[])

# Configuration Flask-Login optimisée
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'warning'
login_manager.session_protection = 'strong'


def setup_logger(app=None):
    """Configuration optimisée du système de logging."""
    logger = logging.getLogger('educinfo')
    
    if logger.handlers:
        return logger
        
    log_level = getattr(app.config, 'LOG_LEVEL', 'INFO') if app else 'INFO'
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # File handler avec rotation
    try:
        log_dir = 'logs'
        if app and hasattr(app.config, 'LOG_FILE'):
            log_dir = os.path.dirname(app.config['LOG_FILE'])
        
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'educinfo.log')
        if app and hasattr(app.config, 'LOG_FILE'):
            log_file = app.config['LOG_FILE']
        
        max_bytes = getattr(app.config, 'LOG_MAX_BYTES', 10 * 1024 * 1024) if app else 10 * 1024 * 1024
        backup_count = getattr(app.config, 'LOG_BACKUP_COUNT', 5) if app else 5
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            delay=True,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging configuré: {log_file}")
        
    except Exception as e:
        console_handler.setLevel(logging.WARNING)
        logger.warning(f"Erreur lors de la configuration du fichier de log: {e}")
        logger.warning("Utilisation du logging console uniquement")

    return logger

# Logger principal
logger = setup_logger()


def init_cache(app):
    """Initialise le cache avec fallback intelligent et optimisations."""
    cache_type = app.config.get('CACHE_TYPE', 'simple')
    
    try:
        if cache_type == 'redis':
            import redis
            redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            
            # Configuration Redis optimisée
            redis_config = {
                'decode_responses': app.config.get('REDIS_DECODE_RESPONSES', True),
                'socket_connect_timeout': app.config.get('REDIS_SOCKET_CONNECT_TIMEOUT', 5),
                'socket_timeout': app.config.get('REDIS_SOCKET_TIMEOUT', 5),
                'retry_on_timeout': True,
                'health_check_interval': 30
            }
            
            # Test de connexion
            redis_client = redis.from_url(redis_url, **redis_config)
            redis_client.ping()
            
            cache.init_app(app, config={
                'CACHE_TYPE': 'redis',
                'CACHE_REDIS_URL': redis_url,
                'CACHE_KEY_PREFIX': app.config.get('CACHE_KEY_PREFIX', 'educinfo'),
                'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
            })
            
            app.logger.info("Cache Redis initialisé avec succès")
            
        else:
            cache.init_app(app, config={
                'CACHE_TYPE': 'simple',
                'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
            })
            app.logger.info("Cache simple initialisé")
            
    except Exception as e:
        app.logger.warning(f"Erreur cache {cache_type}: {e}, fallback vers cache simple")
        
        cache.init_app(app, config={
            'CACHE_TYPE': 'simple',
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        })
    
    @app.context_processor
    def cache_utils():
        return {
            'cache_get': cache.get,
            'cache_set': cache.set,
            'cache_delete': cache.delete
        }


def init_monitoring(app):
    """Initialise le monitoring Prometheus si activé."""
    if not app.config.get('PROMETHEUS_ENABLED', False):
        return
        
    try:
        from prometheus_client import Counter, Histogram, Gauge, generate_latest
        from flask import Response, request
        import time
        
        # Métriques optimisées
        REQUEST_COUNT = Counter(
            'educinfo_requests_total',
            'Total requests',
            ['method', 'endpoint', 'status']
        )
        
        REQUEST_DURATION = Histogram(
            'educinfo_request_duration_seconds',
            'Request duration',
            ['method', 'endpoint']
        )
        
        @app.before_request
        def before_request():
            request.start_time = time.time()
        
        @app.after_request
        def after_request(response):
            if hasattr(request, 'start_time'):
                duration = time.time() - request.start_time
                endpoint = request.endpoint or 'unknown'
                
                REQUEST_DURATION.labels(
                    method=request.method,
                    endpoint=endpoint
                ).observe(duration)
            
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=endpoint,
                    status=response.status_code
                ).inc()
            
            return response
        
        @app.route('/metrics')
        def metrics():
            return Response(generate_latest(), mimetype='text/plain')
        
        logger.info("Monitoring Prometheus activé")
        
    except ImportError:
        logger.warning("prometheus_client non disponible, monitoring désactivé")
    except Exception as e:
        logger.error(f"Erreur initialisation monitoring: {e}")


def init_health_check(app):
    """Initialise le health check endpoint optimisé."""
    @app.route(app.config.get('HEALTH_CHECK_PATH', '/health'))
    def health_check():
        from flask import jsonify
        import time
        
        health_data = {
            'status': 'healthy',
            'version': app.config.get('APP_VERSION', '2.0.0'),
            'timestamp': int(time.time())
        }
        
        try:
            db.session.execute(text('SELECT 1'))
            health_data['database'] = 'ok'
        except Exception:
            health_data['database'] = 'error'
            health_data['status'] = 'unhealthy'
        
        try:
            cache.get('health_check_test')
            health_data['cache'] = 'ok'
        except Exception:
            health_data['cache'] = 'error'
        
        try:
            import psutil
            health_data['metrics'] = 'available'
        except ImportError:
            health_data['metrics'] = 'unavailable'
        
        status_code = 200 if health_data['status'] == 'healthy' else 503
        return jsonify(health_data), status_code


def configure_security_headers(app):
    """Configure les en-têtes de sécurité optimisés."""
    @app.after_request
    def security_headers(response):
        # Protection CSRF renforcée
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # CSP optimisé pour l'application
        if not app.debug:
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.tailwindcss.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.tailwindcss.com https://fonts.googleapis.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com; "
                "connect-src 'self' https://api.openweathermap.org https://api.cts-strasbourg.eu"
            )
            response.headers['Content-Security-Policy'] = csp
        
        return response
