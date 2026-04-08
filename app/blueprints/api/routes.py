"""
API REST pour EducInfo - Endpoints optimisés pour l'affichage temps réel.
Gestion avancée des erreurs, cache intelligent et validation des données.
"""
import logging
from flask import jsonify, request, current_app
from datetime import datetime, timedelta
from sqlalchemy import text
import pytz
from app.services.weather import WeatherService
from app.services.transport import TransportService
from app.services.menu import MenuService
from app.models.absence import Absence
from app.models.event import Event
from app.models.menu import MenuItem
from app.blueprints.api import bp
from app.extensions import cache

logger = logging.getLogger(__name__)

def safe_cache_get(key):
    """Helper pour récupérer depuis le cache avec gestion défensive."""
    try:
        if hasattr(cache, 'get'):
            return cache.get(key)
        elif isinstance(cache, dict):
            return cache.get(key)
        else:
            return None
    except Exception as e:
        logger.warning(f"Erreur cache get {key}: {e}")
        return None

def safe_cache_set(key, value, timeout=None):
    """Helper pour mettre en cache avec gestion défensive."""
    try:
        if hasattr(cache, 'set'):
            if timeout:
                cache.set(key, value, timeout=timeout)
            else:
                cache.set(key, value)
        elif isinstance(cache, dict):
            cache[key] = value
        else:
            logger.warning(f"Type de cache non supporté: {type(cache)}")
    except Exception as e:
        logger.warning(f"Erreur cache set {key}: {e}")

def create_api_response(data=None, success=True, message=None, error_code=None, meta=None):
    """
    Crée une réponse API standardisée optimisée pour l'affichage TV.
    
    Args:
        data: Données à retourner
        success (bool): Statut de succès
        message (str): Message descriptif
        error_code (str): Code d'erreur pour le debugging
        meta (dict): Métadonnées additionnelles
    
    Returns:
        Response: Réponse JSON formatée
    """
    response = {
        'success': success,
        'timestamp': datetime.now(pytz.timezone('Europe/Paris')).isoformat(),
        'version': current_app.config.get('APP_VERSION', '2.0.0')
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if not success:
        response['error'] = {
            'message': message or 'Une erreur est survenue',
            'code': error_code,
            'timestamp': response['timestamp']
        }
    
    if meta:
        response['meta'] = meta
    
    return jsonify(response)

@bp.route('/version')
def version():
    """
    Retourne les informations de version et statut de l'API.
    Optimisé pour les vérifications de santé système.
    """
    try:
        return create_api_response(
            data={
                'version': current_app.config.get('APP_VERSION', '2.0.0'),
                'name': current_app.config.get('APP_NAME', 'EducInfo'),
                'environment': current_app.config.get('FLASK_ENV', 'production'),
                'features': {
                    'weather': True,
                    'transport': True,
                    'menu': True,
                    'events': True,
                    'tv_mode': True
                }
            },
            message="API EducInfo opérationnelle"
        )
    except Exception as e:
        logger.error(f"Erreur endpoint version: {str(e)}")
        return create_api_response(
            success=False,
            message="Erreur lors de la récupération des informations de version",
            error_code="VERSION_ERROR"
        ), 500

@bp.route('/absences')
def absences():
    """
    Retourne les absences des professeurs formatées pour l'affichage TV.
    Optimisé avec cache et structure adaptée au mode TV.
    """
    try:
        # Récupération avec cache
        cache_key = "api_absences_tv"
        
        cached_data = safe_cache_get(cache_key)
        if cached_data:
            logger.debug("Absences récupérées depuis le cache API")
            return create_api_response(
                data=cached_data,
                message="Absences récupérées (cache)",
                meta={'source': 'cache'}
            )
        
        # Récupération depuis la base de données
        absences = Absence.get_all_active_absences()
        
        # Formatage optimisé pour l'affichage TV
        formatted_absences = []
        jours_semaine = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
        
        for absence in absences:
            for jour in jours_semaine:
                if getattr(absence, jour, False):
                    formatted_absences.append({
                        'id': absence.id,
                        'professeur': absence.professeur,
                        'jour': jour,
                        'jour_display': jour.capitalize(),
                        'jour_index': jours_semaine.index(jour)
                    })
        
        # Tri par jour puis par nom de professeur
        formatted_absences.sort(key=lambda x: (x['jour_index'], x['professeur']))
        
        # Structure pour l'affichage TV par jour
        absences_by_day = {}
        for jour in jours_semaine:
            absences_by_day[jour] = [
                abs for abs in formatted_absences if abs['jour'] == jour
            ]
        
        # Données complètes pour l'API
        api_data = {
            'absences': formatted_absences,
            'by_day': absences_by_day,
            'total_count': len(formatted_absences),
            'days_with_absences': len([jour for jour, abs in absences_by_day.items() if abs]),
            'last_update': datetime.now(pytz.timezone('Europe/Paris')).strftime('%H:%M:%S')
        }
        
        # Mise en cache
        cache_timeout = current_app.config.get('CACHE_TIMEOUTS', {}).get('stats', 300)
        safe_cache_set(cache_key, api_data, timeout=cache_timeout)
        logger.debug(f"Absences mises en cache API pour {cache_timeout}s")
        
        return create_api_response(
            data=api_data,
            message=f"{len(formatted_absences)} absences trouvées",
            meta={
                'source': 'database',
                'cache_duration': current_app.config.get('CACHE_TIMEOUTS', {}).get('stats', 300)
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur endpoint absences: {str(e)}")
        return create_api_response(
            success=False,
            message="Erreur lors de la récupération des absences",
            error_code="ABSENCES_ERROR"
        ), 500

@bp.route('/events')
def events():
    """
    Retourne les événements à venir formatés pour l'affichage TV.
    Optimisé avec anticipation d'un mois selon les spécifications.
    """
    try:
        # Récupération avec cache
        cache_key = "api_events_tv"
        
        cached_data = safe_cache_get(cache_key)
        if cached_data:
            logger.debug("Événements récupérés depuis le cache API")
            return create_api_response(
                data=cached_data,
                message="Événements récupérés (cache)",
                meta={'source': 'cache'}
            )
        
        # Récupération des événements (anticipation 1 mois selon spec)
        upcoming_events = Event.get_upcoming_events(days=30)
        
        # Formatage optimisé pour l'affichage TV
        formatted_events = []
        for event in upcoming_events:
            try:
                event_date = event.date
                now = datetime.now().date()
                days_until = (event_date - now).days
                
                # Formatage de la date pour l'affichage
                if days_until == 0:
                    date_display = "Aujourd'hui"
                elif days_until == 1:
                    date_display = "Demain"
                elif days_until <= 7:
                    date_display = f"Dans {days_until} jours"
                else:
                    date_display = event_date.strftime('%d/%m/%Y')
                
                # Catégorisation de l'urgence
                if days_until <= 1:
                    urgency = 'immediate'
                elif days_until <= 7:
                    urgency = 'soon'
                elif days_until <= 14:
                    urgency = 'upcoming'
                else:
                    urgency = 'future'
                
                formatted_events.append({
                    'id': event.id,
                    'title': event.title,
                    'description': event.description or '',
                    'date': event_date.isoformat(),
                    'date_formatted': date_display,
                    'date_full': event_date.strftime('%A %d %B %Y'),
                    'days_until': days_until,
                    'urgency': urgency,
                    'is_today': days_until == 0,
                    'is_tomorrow': days_until == 1,
                    'is_this_week': days_until <= 7
                })
            except Exception as e:
                logger.warning(f"Erreur formatage événement {event.id}: {str(e)}")
                continue
        
        # Tri par date croissante
        formatted_events.sort(key=lambda x: x['days_until'])
        
        # Statistiques pour l'affichage
        stats = {
            'total_count': len(formatted_events),
            'today_count': len([e for e in formatted_events if e['is_today']]),
            'this_week_count': len([e for e in formatted_events if e['is_this_week']]),
            'upcoming_count': len([e for e in formatted_events if e['urgency'] == 'upcoming'])
        }
        
        api_data = {
            'events': formatted_events,
            'stats': stats,
            'last_update': datetime.now(pytz.timezone('Europe/Paris')).strftime('%H:%M:%S')
        }
        
        # Mise en cache
        cache_timeout = current_app.config.get('CACHE_TIMEOUTS', {}).get('stats', 300)
        safe_cache_set(cache_key, api_data, timeout=cache_timeout)
        logger.debug(f"Événements mis en cache API pour {cache_timeout}s")
        
        return create_api_response(
            data=api_data,
            message=f"{len(formatted_events)} événements trouvés",
            meta={
                'source': 'database',
                'cache_duration': cache_timeout,
                'anticipation_days': 30
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur endpoint events: {str(e)}")
        return create_api_response(
            success=False,
            message="Erreur lors de la récupération des événements",
            error_code="EVENTS_ERROR"
        ), 500

@bp.route('/menu')
def menu():
    """
    Retourne le menu de la cantine formaté pour l'affichage TV.
    Optimisé avec récupération du jour actuel et du lendemain.
    """
    try:
        # Récupération avec cache
        cache_key = "api_menu_tv"
        cache = current_app.extensions.get('cache')
        
        if cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.debug("Menu récupéré depuis le cache API")
                return create_api_response(
                    data=cached_data,
                    message="Menu récupéré (cache)",
                    meta={'source': 'cache'}
                )
        
        # Utiliser le service menu optimisé
        menu_service = MenuService()
        
        # Menu d'aujourd'hui et de demain (selon spec)
        today_menu = menu_service.get_todays_menu()
        tomorrow_menu = menu_service.get_menu_by_date(
            datetime.now().date() + timedelta(days=1)
        )
        
        # Formatage pour l'affichage TV
        def format_menu_for_api(menu_items, date_label):
            if not menu_items:
                return {
                    'date_label': date_label,
                    'items': [],
                    'categories': {},
                    'total_items': 0,
                    'has_menu': False
                }
            
            categories = menu_service.organize_menu_by_category(menu_items)
            formatted_categories = {}
            
            for category_id, items in categories.items():
                category_info = menu_service.get_category_info(category_id)
                formatted_categories[str(category_id)] = {
                    'name': category_info['name'],
                    'icon': category_info['icon'],
                    'items': [
                        {
                            'id': item.id,
                            'name': item.name,
                            'description': item.description or '',
                            'icons': item.icons or '',
                            'order': item.order
                        }
                        for item in items
                    ],
                    'count': len(items)
                }
            
            return {
                'date_label': date_label,
                'items': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'description': item.description or '',
                        'icons': item.icons or '',
                        'category': item.category,
                        'order': item.order
                    }
                    for item in menu_items
                ],
                'categories': formatted_categories,
                'total_items': len(menu_items),
                'has_menu': True
            }
        
        # Formatage des données
        today_data = format_menu_for_api(today_menu, "Aujourd'hui")
        tomorrow_data = format_menu_for_api(tomorrow_menu, "Demain")
        
        api_data = {
            'today': today_data,
            'tomorrow': tomorrow_data,
            'current_date': datetime.now().date().isoformat(),
            'tomorrow_date': (datetime.now().date() + timedelta(days=1)).isoformat(),
            'last_update': datetime.now(pytz.timezone('Europe/Paris')).strftime('%H:%M:%S'),
            'summary': {
                'today_items': today_data['total_items'],
                'tomorrow_items': tomorrow_data['total_items'],
                'has_today_menu': today_data['has_menu'],
                'has_tomorrow_menu': tomorrow_data['has_menu']
            }
        }
        
        # Mise en cache
        if cache:
            cache_timeout = current_app.config.get('CACHE_TIMEOUTS', {}).get('menu', 3600)
            cache.set(cache_key, api_data, timeout=cache_timeout)
            logger.debug(f"Menu mis en cache API pour {cache_timeout}s")
        
        return create_api_response(
            data=api_data,
            message=f"Menu récupéré (aujourd'hui: {today_data['total_items']} plats, demain: {tomorrow_data['total_items']} plats)",
            meta={
                'source': 'database',
                'cache_duration': cache_timeout
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur endpoint menu: {str(e)}")
        return create_api_response(
            success=False,
            message="Erreur lors de la récupération du menu",
            error_code="MENU_ERROR"
        ), 500

@bp.route('/weather')
def weather():
    """
    Retourne les données météo formatées pour l'affichage TV.
    Optimisé avec mise à jour toutes les 5 minutes selon les spécifications.
    """
    try:
        # Paramètres optionnels de la requête
        city = request.args.get('city')
        api_key = request.args.get('api_key')
        
        # Utiliser le service météo optimisé
        weather_service = WeatherService()
        weather_data = weather_service.get_weather_data(city=city, api_key=api_key)
        
        if weather_data.get('success'):
            return create_api_response(
                data=weather_data,
                message="Données météo récupérées avec succès",
                meta={
                    'source': 'openweathermap',
                    'update_frequency': '5 minutes',
                    'cache_duration': current_app.config.get('CACHE_TIMEOUTS', {}).get('weather', 1800)
                }
            )
        else:
            return create_api_response(
                success=False,
                message=weather_data.get('error', 'Erreur lors de la récupération des données météo'),
                error_code="WEATHER_API_ERROR",
                data={'error_details': weather_data}
            ), 503  # Service Unavailable
        
    except Exception as e:
        logger.error(f"Erreur endpoint weather: {str(e)}")
        return create_api_response(
            success=False,
            message="Erreur technique lors de la récupération des données météo",
            error_code="WEATHER_ERROR"
        ), 500

@bp.route('/transports')
def transports():
    """
    Retourne les données de transport formatées pour l'affichage TV.
    Optimisé avec mise à jour toutes les 5 minutes et 8 prochains passages.
    """
    try:
        # Paramètres optionnels de la requête
        stop_code = request.args.get('stop_code')
        vehicle_mode = request.args.get('vehicle_mode')
        api_token = request.args.get('api_token')
        max_visits = request.args.get('max_visits', 8, type=int)
        
        # Validation du nombre de passages
        if max_visits > 15:  # Limite raisonnable
            max_visits = 15
        
        # Utiliser le service transport optimisé
        transport_service = TransportService()
        transport_data = transport_service.get_stop_arrivals(
            stop_code=stop_code,
            vehicle_mode=vehicle_mode,
            api_token=api_token,
            max_visits=max_visits
        )
        
        if transport_data.get('success'):
            return create_api_response(
                data=transport_data,
                message=f"{len(transport_data.get('arrivals', []))} passages trouvés",
                meta={
                    'source': 'cts_api',
                    'update_frequency': '5 minutes',
                    'max_passages': 8,
                    'cache_duration': current_app.config.get('CACHE_TIMEOUTS', {}).get('transport', 60)
                }
            )
        else:
            return create_api_response(
                success=False,
                message=transport_data.get('error', 'Erreur lors de la récupération des données de transport'),
                error_code=transport_data.get('error_type', 'TRANSPORT_API_ERROR'),
                data={'error_details': transport_data}
            ), 503  # Service Unavailable
        
    except Exception as e:
        logger.error(f"Erreur endpoint transports: {str(e)}")
        return create_api_response(
            success=False,
            message="Erreur technique lors de la récupération des données de transport",
            error_code="TRANSPORT_ERROR"
        ), 500

@bp.route('/health')
def health():
    """
    Endpoint de vérification de santé pour le monitoring système.
    Vérifie la disponibilité des services critiques.
    """
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now(pytz.timezone('Europe/Paris')).isoformat(),
            'version': current_app.config.get('APP_VERSION', '2.0.0'),
            'services': {}
        }
        
        # Vérification de la base de données
        try:
            from app.extensions import db
            db.session.execute(text('SELECT 1'))
            health_status['services']['database'] = 'healthy'
        except Exception as e:
            health_status['services']['database'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'degraded'
        
        # Vérification du cache
        try:
            cache = current_app.extensions.get('cache')
            if cache:
                cache.set('health_check', 'ok', timeout=10)
                if cache.get('health_check') == 'ok':
                    health_status['services']['cache'] = 'healthy'
                else:
                    health_status['services']['cache'] = 'unhealthy: cache read failed'
                    health_status['status'] = 'degraded'
            else:
                health_status['services']['cache'] = 'not_configured'
        except Exception as e:
            health_status['services']['cache'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'degraded'
        
        # Déterminer le code de statut HTTP
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return create_api_response(
            data=health_status,
            message=f"Système {health_status['status']}",
            meta={'monitoring': True}
        ), status_code
        
    except Exception as e:
        logger.error(f"Erreur health check: {str(e)}")
        return create_api_response(
            success=False,
            message="Erreur lors de la vérification de santé",
            error_code="HEALTH_CHECK_ERROR"
        ), 500

@bp.route('/stats')
def stats():
    """
    Retourne les statistiques générales du système pour le monitoring.
    """
    try:
        # Récupération avec cache
        cache_key = "api_stats_general"
        
        cached_data = safe_cache_get(cache_key)
        if cached_data:
            return create_api_response(
                data=cached_data,
                message="Statistiques récupérées (cache)",
                meta={'source': 'cache'}
            )
        
        # Calcul des statistiques
        stats_data = {
            'absences': {
                'total': Absence.query.count(),
                'active': len(Absence.get_all_active_absences())
            },
            'events': {
                'total': Event.query.count(),
                'upcoming': len(Event.get_upcoming_events())
            },
            'menu': {
                'total_items': MenuItem.query.count(),
                'today_items': len(MenuService.get_todays_menu())
            },
            'system': {
                'uptime': datetime.now(pytz.timezone('Europe/Paris')).isoformat(),
                'version': current_app.config.get('APP_VERSION', '2.0.0')
            }
        }
        
        # Mise en cache
        cache_timeout = current_app.config.get('CACHE_TIMEOUTS', {}).get('stats', 300)
        safe_cache_set(cache_key, stats_data, timeout=cache_timeout)
        
        return create_api_response(
            data=stats_data,
            message="Statistiques générales",
            meta={'source': 'database'}
        )
        
    except Exception as e:
        logger.error(f"Erreur endpoint stats: {str(e)}")
        return create_api_response(
            success=False,
            message="Erreur lors de la récupération des statistiques",
            error_code="STATS_ERROR"
        ), 500

# Gestionnaire d'erreurs global pour l'API
@bp.errorhandler(404)
def api_not_found(error):
    """Gestionnaire pour les endpoints API non trouvés."""
    return create_api_response(
        success=False,
        message="Endpoint API non trouvé",
        error_code="API_NOT_FOUND"
    ), 404

@bp.errorhandler(405)
def api_method_not_allowed(error):
    """Gestionnaire pour les méthodes HTTP non autorisées."""
    return create_api_response(
        success=False,
        message="Méthode HTTP non autorisée pour cet endpoint",
        error_code="METHOD_NOT_ALLOWED"
    ), 405

@bp.errorhandler(500)
def api_internal_error(error):
    """Gestionnaire pour les erreurs internes de l'API."""
    logger.error(f"Erreur interne API: {str(error)}")
    return create_api_response(
        success=False,
        message="Erreur interne du serveur API",
        error_code="INTERNAL_SERVER_ERROR"
    ), 500