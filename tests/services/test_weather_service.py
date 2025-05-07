"""
Tests unitaires pour le service WeatherService.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.weather import WeatherService


@pytest.fixture
def weather_service():
    """Fixture qui crée une instance du service WeatherService pour les tests."""
    return WeatherService(api_key="test_key", city="Test City")


def test_weather_service_init(weather_service):
    """
    ETANT DONNE un service WeatherService
    QUAND une instance est créée
    ALORS les attributs doivent être correctement initialisés
    """
    assert weather_service.api_key == "test_key"
    assert weather_service.city == "Test City"
    assert weather_service.cache_expiry == 1800  # Par défaut 30 minutes (1800 secondes)


@patch('app.services.weather.requests.get')
def test_get_weather_success(mock_get, weather_service):
    """
    ETANT DONNE un service WeatherService
    QUAND la méthode get_weather est appelée avec succès
    ALORS elle doit retourner les données météo formatées correctement
    """
    # Configuration du mock pour simuler une réponse réussie
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "weather": [{"id": 800, "main": "Clear", "description": "ciel dégagé", "icon": "01d"}],
        "main": {
            "temp": 20.5,
            "feels_like": 19.8,
            "humidity": 55
        },
        "wind": {
            "speed": 3.5
        },
        "name": "Test City"
    }
    mock_get.return_value = mock_response
    
    # Appel de la méthode à tester
    result = weather_service.get_weather()
    
    # Vérifications
    assert result is not None
    assert result.get('error') is None
    assert result.get('city') == "Test City"
    assert result.get('temp') == 20.5
    assert result.get('feels_like') == 19.8
    assert result.get('humidity') == 55
    assert result.get('wind_speed') == 3.5
    assert result.get('description') == "ciel dégagé"
    assert result.get('icon') == "01d"


@patch('app.services.weather.requests.get')
def test_get_weather_api_error(mock_get, weather_service):
    """
    ETANT DONNE un service WeatherService
    QUAND l'API météo retourne une erreur
    ALORS la méthode get_weather doit retourner un dictionnaire contenant une erreur
    """
    # Configuration du mock pour simuler une erreur
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response
    
    # Appel de la méthode à tester
    result = weather_service.get_weather()
    
    # Vérifications
    assert result is not None
    assert result.get('error') == "Erreur d'accès à l'API météo (code 401)" 