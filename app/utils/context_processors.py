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
    """Context processor qui fournit les variables communes a tous les templates."""
    try:
        site_config = SiteConfig.get_config()
        weather_config = WeatherConfig.get_config()
        widget_config = WidgetConfig.get_config()

        weather_data = None
        if weather_config and weather_config.show_weather:
            try:
                weather_data = get_weather_service().get_weather_for_display()
            except Exception as e:
                logger.warning(f"Erreur meteo dans le contexte: {e}")

        return {
            'current_datetime': datetime.now(),
            'site_config': site_config,
            'weather_config': weather_config,
            'widget_config': widget_config,
            'weather': weather_data,
            'app_version': current_app.config.get('APP_VERSION', '2.0.0'),
        }
    except Exception as e:
        logger.error(f"Erreur dans common_context: {e}")
        return {
            'current_datetime': datetime.now(),
            'site_config': {'site_name': 'EducInfo'},
            'weather_config': None,
            'widget_config': None,
            'weather': None,
            'app_version': current_app.config.get('APP_VERSION', '2.0.0'),
        }

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
        except Exception:
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