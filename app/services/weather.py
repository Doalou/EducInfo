"""
Service météo pour l'application.
Ce module encapsule la logique d'interrogation de l'API OpenWeather.
"""
import time
import requests
from flask import current_app
from app.extensions import logger
from app.models import WeatherConfig

class WeatherService:
    """
    Service pour récupérer les données météo via l'API OpenWeather.
    Gère le cache et la récupération des données météo.
    """
    # Constantes
    CACHE_DURATION = 1800  # 30 minutes en secondes
    REQUEST_TIMEOUT = 5    # Timeout en secondes
    
    def __init__(self):
        """Initialise le service météo avec un cache vide."""
        self._cache = {}
        self._last_update = {}
    
    def get_weather_data(self, city=None, api_key=None):
        """
        Récupère les données météo pour une ville donnée.
        Utilise le cache si les données sont encore fraîches.
        
        Args:
            city (str): Ville pour laquelle récupérer la météo (ou None pour utiliser la config)
            api_key (str): Clé API OpenWeather (ou None pour utiliser la config)
            
        Returns:
            dict: Données météo ou dictionnaire d'erreur
        """
        # Récupérer la configuration
        weather_config = WeatherConfig.get_config()
        
        # Vérifier si la météo est activée
        if not weather_config.show_weather:
            logger.info("Service météo: Météo désactivée dans la configuration")
            return {"error": "Météo désactivée"}
        
        # Utiliser les paramètres de config si non fournis
        effective_city = city or weather_config.city
        effective_api_key = api_key or weather_config.api_key or current_app.config.get('WEATHER_API_KEY')
        
        # Vérifier que les paramètres nécessaires sont disponibles
        if not effective_city or not effective_api_key:
            logger.error("Service météo: Configuration incomplète (ville ou clé API manquante)")
            return {"error": "Configuration météo incomplète"}
        
        # Vérifier le cache
        cache_key = f"{effective_city}_{effective_api_key}"
        current_time = time.time()
        
        if (cache_key in self._cache and 
            cache_key in self._last_update and 
            current_time - self._last_update[cache_key] < self.CACHE_DURATION):
            logger.debug(f"Service météo: Utilisation du cache pour {effective_city}")
            return self._cache[cache_key]
        
        # Récupérer les données fraîches
        try:
            logger.info(f"Service météo: Récupération des données pour {effective_city}")
            weather_data = self._fetch_weather_data(effective_city, effective_api_key)
            
            # Mettre à jour le cache
            self._cache[cache_key] = weather_data
            self._last_update[cache_key] = current_time
            
            return weather_data
        except Exception as e:
            logger.error(f"Service météo: Erreur lors de la récupération des données - {str(e)}")
            # En cas d'erreur, retourner le cache même s'il est périmé
            if cache_key in self._cache:
                logger.warning(f"Service météo: Utilisation du cache périmé pour {effective_city}")
                return self._cache[cache_key]
            return {"error": "An internal error occurred while fetching weather data."}
    
    def _fetch_weather_data(self, city, api_key):
        """
        Interroge l'API OpenWeather pour récupérer les données météo.
        
        Args:
            city (str): Ville pour laquelle récupérer la météo
            api_key (str): Clé API OpenWeather
            
        Returns:
            dict: Données météo formatées
            
        Raises:
            Exception: En cas d'erreur lors de la requête ou du traitement des données
        """
        try:
            response = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "q": city,
                    "appid": api_key,
                    "units": "metric",
                    "lang": "fr"
                },
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Accès sécurisé aux données
            weather_data = data.get('weather', [{}])[0]
            main_data = data.get('main', {})
            temp = main_data.get('temp')
            
            if temp is None:
                raise ValueError("Données de température manquantes dans la réponse")
            
            # Formatage des données
            description = weather_data.get('description', 'N/A')
            # Capitalisation de la première lettre de la description
            description = description[:1].upper() + description[1:] if description else 'N/A'
            
            return {
                'temp': round(temp),
                'description': description,
                'icon': weather_data.get('icon', 'N/A'),
                'humidity': main_data.get('humidity'),
                'feels_like': round(main_data.get('feels_like', 0)),
                'wind_speed': data.get('wind', {}).get('speed'),
                'city': data.get('name', city),
                'timestamp': int(time.time())
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Service météo: Erreur de requête - {str(e)}")
            raise Exception(f"Erreur de communication avec l'API météo: {str(e)}")
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Service météo: Erreur de traitement des données - {str(e)}")
            raise Exception(f"Erreur de traitement des données météo: {str(e)}")
        except Exception as e:
            logger.error(f"Service météo: Erreur inattendue - {str(e)}")
            raise Exception(f"Erreur inattendue du service météo: {str(e)}")

# Instance unique du service à utiliser dans l'application
weather_service = WeatherService() 