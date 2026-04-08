"""
Tests unitaires pour le service WeatherService.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.weather import WeatherService
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['WEATHER_CITY'] = 'Strasbourg'
    app.config['WEATHER_API_KEY'] = 'test_key'
    return app

@pytest.fixture
def weather_service(app):
    """Fixture qui crée une instance du service WeatherService pour les tests."""
    with app.app_context():
        # Mocking cache to avoid dependency issues during init
        with patch('app.services.weather.current_app') as mock_app:
            mock_cache = MagicMock()
            mock_cache.get.return_value = None
            mock_app.extensions = {'cache': mock_cache}
            return WeatherService()


def test_weather_service_init(weather_service):
    """
    ETANT DONNE un service WeatherService
    QUAND une instance est créée
    ALORS elle doit être correctement initialisée
    """
    assert weather_service is not None


@patch('app.services.weather.requests.get')
@patch('app.models.config.WeatherConfig.get_config')
def test_get_weather_success(mock_get_config, mock_get, weather_service):
    """
    ETANT DONNE un service WeatherService
    QUAND la méthode get_weather_data est appelée avec succès
    ALORS elle doit retourner les données météo formatées correctement
    """
    # Mock Config
    mock_config = MagicMock()
    mock_config.city = "Test City"
    mock_config.api_key = "test_key"
    mock_config.show_weather = True
    mock_get_config.return_value = mock_config

    # Configuration du mock pour simuler une réponse réussie
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "weather": [{"id": 800, "main": "Clear", "description": "ciel dégagé", "icon": "01d"}],
        "main": {
            "temp": 20.5,
            "feels_like": 19.8,
            "humidity": 55,
            "pressure": 1015
        },
        "wind": {
            "speed": 3.5
        },
        "sys": {
            "country": "FR",
            "sunrise": 1600000000,
            "sunset": 1600040000
        },
        "name": "Test City",
        "coord": {"lat": 48.58, "lon": 7.75}
    }
    
    # Second call for AQI (Air Pollution) which is called internally
    mock_aqi_response = MagicMock()
    mock_aqi_response.status_code = 200
    mock_aqi_response.json.return_value = {
        "list": [{"main": {"aqi": 1}}]
    }

    mock_get.side_effect = [mock_response, mock_aqi_response]
    
    # Appel de la méthode à tester
    with patch('app.services.weather.current_app') as mock_app:
        mock_app.config = {'WEATHER_API_KEY': 'test_key', 'WEATHER_CITY': 'Test City'}
        result = weather_service.get_weather_data(city="Test City", api_key="test_key")
    
    # Vérifications
    assert result is not None
    assert result.get('success') is True
    assert result.get('city') == "Test City"
    assert result.get('temperature') == 20  # Rounding in service
    assert result.get('feels_like') == 20
    assert result.get('humidity') == 55
    assert result.get('wind_speed') == 12.6  # 3.5 * 3.6
    assert result.get('description') == "Ciel Dégagé"  # Title case
    assert result.get('icon') == "01d"


@patch('app.services.weather.requests.get')
@patch('app.models.config.WeatherConfig.get_config')
def test_get_weather_api_error(mock_get_config, mock_get, weather_service):
    """
    ETANT DONNE un service WeatherService
    QUAND l'API météo retourne une erreur
    ALORS la méthode get_weather_data doit retourner les données de démo (fallback)
    """
    # Mock Config
    mock_config = MagicMock()
    mock_config.city = "Test City"
    mock_config.api_key = "test_key"
    mock_config.show_weather = True
    mock_get_config.return_value = mock_config

    # Configuration du mock pour simuler une erreur
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response
    
    # Appel de la méthode à tester
    with patch('app.services.weather.current_app') as mock_app:
         mock_app.config = {'WEATHER_API_KEY': 'test_key', 'WEATHER_CITY': 'Test City'}
         result = weather_service.get_weather_data(city="Test City", api_key="test_key")
    
    # Vérifications - Le service retourne des données de démo en cas d'erreur
    assert result is not None
    assert result.get('success') is True
    assert result.get('is_demo') is True 