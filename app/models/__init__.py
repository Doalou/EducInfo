"""
Package contenant les modèles de données.
"""
# Importation des modèles pour les rendre disponibles
from app.models.user import User
from app.models.absence import Absence
from app.models.event import Event
from app.models.menu import MenuItem
from app.models.config import SiteConfig, WidgetConfig, ThemeConfig, WeatherConfig

# Définition des noms disponibles lors de l'import depuis ce package
__all__ = [
    'User', 
    'Absence', 
    'Event', 
    'MenuItem', 
    'SiteConfig', 
    'WidgetConfig', 
    'ThemeConfig', 
    'WeatherConfig'
] 