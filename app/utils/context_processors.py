"""
Processeurs de contexte pour les templates.
Ce module définit les variables globales disponibles dans tous les templates.
"""
from datetime import datetime, timedelta
from flask import current_app, request, g
from app.extensions import cache, logger
from app.models import SiteConfig, MenuItem, WeatherConfig, WidgetConfig
from app.services import get_weather_service

def common_context():
    """
    Context processor optimisé qui fournit les variables communes à tous les templates.
    Utilise un système de cache intelligent pour réduire les requêtes de base de données.
    
    Returns:
        dict: Variables disponibles dans tous les templates
    """
    # Cache les configurations pour éviter les requêtes répétées
    cache_key = f"{current_app.config.get('CACHE_KEY_PREFIX', 'educinfo')}:common_context"
    cached_context = cache.get(cache_key)
    
    if cached_context:
        # Mettre à jour seulement les données qui changent (comme l'heure et la météo si besoin)
        cached_context['current_datetime'] = datetime.now()
        # Forcer la récupération de nouvelles données météo si le cache est expiré
        if cached_context.get('weather_config') and cached_context['weather_config'].show_weather:
            try:
                fresh_weather = get_weather_service().get_weather_data()
                if fresh_weather and 'error' not in fresh_weather:
                    cached_context['weather'] = fresh_weather
                    # Ajouter l'emoji d'icône météo
                    if 'icon' in fresh_weather:
                        cached_context['weather']['icon_emoji'] = get_weather_emoji(fresh_weather['icon'])
            except Exception as e:
                logger.warning(f"Erreur lors de la mise à jour météo dans le cache: {e}")
        return cached_context
    
    try:
        # Récupérer toutes les configurations en parallèle pour optimiser
        site_config = SiteConfig.get_config()
        weather_config = WeatherConfig.get_config()
        widget_config = WidgetConfig.get_config()
        
        weather_data = None
        
        # Récupérer les données météo seulement si activées
        if weather_config and weather_config.show_weather:
            try:
                logger.info(f"Récupération des données météo pour {weather_config.city}")
                weather_data = get_weather_service().get_weather_data()
                
                if weather_data:
                    if 'error' in weather_data or not weather_data.get('success'):
                        error_msg = weather_data.get('error', 'Service indisponible')
                        logger.warning(f"Erreur météo: {error_msg}")
                        # En cas d'erreur, utiliser des données par défaut
                        weather_data = {
                            'temp': None,
                            'temperature': None,
                            'description': 'Service indisponible',
                            'icon': '01d',
                            'icon_emoji': '🌡️',
                            'city': weather_config.city,
                            'status': 'error'
                        }
                    else:
                        # Normaliser les données - le service retourne 'temperature' mais les templates attendent 'temp'
                        if 'temperature' in weather_data and 'temp' not in weather_data:
                            weather_data['temp'] = weather_data['temperature']
                        
                        # Ajouter l'emoji d'icône météo si pas déjà présent
                        if 'icon_emoji' not in weather_data:
                            weather_data['icon_emoji'] = get_weather_emoji(weather_data.get('icon', '01d'))
                        
                        temp_display = weather_data.get('temp') or weather_data.get('temperature', 'N/A')
                        desc_display = weather_data.get('description', 'N/A')
                        logger.info(f"Données météo récupérées avec succès: {temp_display}°C, {desc_display}")
                else:
                    logger.warning("Aucune donnée météo retournée par le service")
                    
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des données météo: {e}")
                weather_data = {
                    'temp': None,
                    'temperature': None,
                    'description': 'Erreur de connexion',
                    'icon': '01d',
                    'icon_emoji': '❌',
                    'emoji': '❌',  # Pour compatibilité avec différents templates
                    'city': weather_config.city if weather_config else 'Inconnue',
                    'status': 'error',
                    'success': False
                }
        else:
            logger.debug("Widget météo désactivé")
        
        context = {
            'current_datetime': datetime.now(),
            'site_config': site_config,
            'weather_config': weather_config,
            'widget_config': widget_config,
            'weather': weather_data,
            'app_version': current_app.config.get('APP_VERSION', '1.2.0'),
        }
        
        # Mettre en cache pour les prochaines requêtes (mais pas trop longtemps pour la météo)
        cache_timeout = current_app.config.get('CACHE_TIMEOUTS', {}).get('config', 180)  # 3 minutes par défaut
        cache.set(cache_key, context, timeout=cache_timeout)
        
        logger.debug(f"Context généré avec météo: {weather_data is not None}")
        return context
        
    except Exception as e:
        logger.error(f"Erreur dans common_context: {e}")
        # Retourner un contexte minimal en cas d'erreur
        return {
            'current_datetime': datetime.now(),
            'site_config': {'site_name': 'EducInfo'},
            'weather_config': None,
            'widget_config': None,
            'weather': None,
            'app_version': current_app.config.get('APP_VERSION', '1.2.0'),
        }

def get_weather_emoji(icon_code):
    """
    Convertit un code d'icône OpenWeather en emoji.
    
    Args:
        icon_code (str): Code d'icône OpenWeather (ex: '01d', '02n', etc.)
        
    Returns:
        str: Emoji correspondant
    """
    icon_map = {
        '01d': '☀️',   # clear sky day
        '01n': '🌙',   # clear sky night
        '02d': '⛅',   # few clouds day
        '02n': '☁️',   # few clouds night
        '03d': '☁️',   # scattered clouds
        '03n': '☁️',   # scattered clouds
        '04d': '☁️',   # broken clouds
        '04n': '☁️',   # broken clouds
        '09d': '🌦️',   # shower rain
        '09n': '🌧️',   # shower rain
        '10d': '🌦️',   # rain day
        '10n': '🌧️',   # rain night
        '11d': '⛈️',   # thunderstorm
        '11n': '⛈️',   # thunderstorm
        '13d': '❄️',   # snow
        '13n': '❄️',   # snow
        '50d': '🌫️',   # mist
        '50n': '🌫️',   # mist
    }
    return icon_map.get(icon_code, '🌡️')

def absence_context():
    """
    Fournit des fonctions utilitaires pour la gestion des absences dans les templates.
    
    Returns:
        dict: Dictionnaire de fonctions utilitaires
    """
    def get_absence_status(absence, jour):
        """
        Vérifie si un professeur est absent pour un jour donné.
        
        Args:
            absence (Absence): Objet Absence
            jour (str): Jour de la semaine (lundi, mardi, etc.)
            
        Returns:
            bool: True si le professeur est absent ce jour-là
        """
        return getattr(absence, jour, False)
    
    return {'get_absence_status': get_absence_status}

def menu_context():
    """
    Fournit la classe MenuItem pour les templates.
    
    Returns:
        dict: Dictionnaire avec le modèle MenuItem
    """
    return {'MenuItem': MenuItem}

def format_time(date_string):
    """
    Filtre Jinja2 pour formater les heures.
    
    Args:
        date_string (str): Chaîne de date ISO 8601
        
    Returns:
        str: Heure formatée en HH:MM
    """
    if not date_string:
        return '--:--'
    
    try:
        # Parser la date ISO 8601
        if 'T' in date_string:
            # Format ISO complet avec timezone
            if '+' in date_string or 'Z' in date_string:
                from dateutil import parser
                dt = parser.parse(date_string)
            else:
                dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            # Format simple
            dt = datetime.fromisoformat(date_string)
        
        # Formater en HH:MM
        return dt.strftime('%H:%M')
    except (ValueError, ImportError) as e:
        # Fallback si erreur de parsing
        try:
            # Tentative avec strptime pour formats standards
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%H:%M:%S']:
                try:
                    dt = datetime.strptime(date_string, fmt)
                    return dt.strftime('%H:%M')
                except ValueError:
                    continue
        except:
            pass
        
        return '--:--'

def format_date(date_string):
    """
    Filtre Jinja2 pour formater les dates.
    
    Args:
        date_string (str): Chaîne de date ISO 8601
        
    Returns:
        str: Date formatée en DD/MM/YYYY
    """
    if not date_string:
        return '--/--/----'
    
    try:
        if 'T' in date_string:
            # Format ISO complet
            if '+' in date_string or 'Z' in date_string:
                from dateutil import parser
                dt = parser.parse(date_string)
            else:
                dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(date_string)
        
        return dt.strftime('%d/%m/%Y')
    except (ValueError, ImportError):
        return '--/--/----'

def format_datetime(date_string):
    """
    Filtre Jinja2 pour formater les dates et heures.
    
    Args:
        date_string (str): Chaîne de date ISO 8601
        
    Returns:
        str: Date et heure formatées en DD/MM/YYYY HH:MM
    """
    if not date_string:
        return '--/--/---- --:--'
    
    try:
        if 'T' in date_string:
            if '+' in date_string or 'Z' in date_string:
                from dateutil import parser
                dt = parser.parse(date_string)
            else:
                dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(date_string)
        
        return dt.strftime('%d/%m/%Y %H:%M')
    except (ValueError, ImportError):
        return '--/--/---- --:--'

def register_template_filters(app):
    """
    Enregistre les filtres Jinja2 personnalisés.
    
    Args:
        app: L'application Flask
    """
    app.jinja_env.filters['format_time'] = format_time
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_datetime'] = format_datetime 