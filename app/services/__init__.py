"""
Package contenant les services métier.
Ce package fournit des services encapsulant la logique métier de l'application.
"""
# Importation des services
from app.services.weather import weather_service
from app.services.transport import transport_service
from app.services.menu import menu_service

# Définition des noms disponibles lors de l'import depuis ce package
__all__ = [
    'weather_service',
    'transport_service',
    'menu_service'
] 