"""
Package contenant les services métier.
Ce package fournit des services encapsulant la logique métier de l'application.
"""
# Importation des classes de services
from app.services.weather import WeatherService
from app.services.transport import TransportService
from app.services.menu import MenuService

# Instances lazy des services (initialisées à la demande)
_weather_service = None
_transport_service = None
_menu_service = None

def get_weather_service():
    """Retourne l'instance du service météo (lazy loading)"""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service

def get_transport_service():
    """Retourne l'instance du service transport (lazy loading)"""
    global _transport_service
    if _transport_service is None:
        _transport_service = TransportService()
    return _transport_service

def get_menu_service():
    """Retourne l'instance du service menu (lazy loading)"""
    global _menu_service
    if _menu_service is None:
        _menu_service = MenuService()
    return _menu_service

# Variables simulant les anciennes instances globales pour compatibilité
class LazyService:
    """Classe helper pour simuler une instance lazy loaded"""
    def __init__(self, service_func):
        self._service_func = service_func
        self._service = None
    
    def __getattr__(self, name):
        if self._service is None:
            self._service = self._service_func()
        return getattr(self._service, name)

# Instances lazy compatibles avec l'ancien code
weather_service = LazyService(get_weather_service)
transport_service = LazyService(get_transport_service)
menu_service = LazyService(get_menu_service)

# Définition des noms disponibles lors de l'import depuis ce package
__all__ = [
    'WeatherService',
    'TransportService', 
    'MenuService',
    'get_weather_service',
    'get_transport_service',
    'get_menu_service',
    'weather_service',
    'transport_service',
    'menu_service'
] 