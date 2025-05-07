"""
Processeurs de contexte pour les templates.
Ce module définit les variables globales disponibles dans tous les templates.
"""
from datetime import datetime
from app.models import SiteConfig, MenuItem, WeatherConfig
from app.services.weather import WeatherService

def common_context():
    """
    Définit des variables disponibles dans tous les templates.
    
    Returns:
        dict: Dictionnaire de variables pour le contexte des templates
    """
    weather_data = None
    weather_config = WeatherConfig.get_config()
    if weather_config and weather_config.show_weather:
        service = WeatherService()
        weather_data = service.get_weather_data()
        
    return {
        'site_config': SiteConfig.get_config(),
        'current_datetime': datetime.now(),
        'current_year': datetime.now().year,
        'weather': weather_data
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