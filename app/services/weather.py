"""
Service de récupération des données météo via l'API OpenWeatherMap.
Optimisé pour l'affichage sur écrans TV avec cache intelligent et gestion d'erreurs robuste.
"""
import requests
import logging
from flask import current_app, json
from datetime import datetime, timedelta
import pytz

logger = logging.getLogger(__name__)

class WeatherService:
    """
    Service météo optimisé pour EducInfo avec cache intelligent et récupération robuste.
    Spécialement conçu pour l'affichage sur écrans TV avec mise à jour automatique.
    """
    
    def __init__(self):
        self.cache = current_app.extensions.get('cache')
    
    def _cache_get(self, key):
        """Helper optimisé pour récupérer depuis le cache."""
        if not self.cache:
            return None
        
        try:
            return self.cache.get(key) if hasattr(self.cache, 'get') else self.cache.get(key) if isinstance(self.cache, dict) else None
        except Exception as e:
            logger.warning(f"Erreur cache get: {e}")
            return None
    
    def _cache_set(self, key, value, timeout=None):
        """Helper optimisé pour mettre en cache."""
        if not self.cache:
            return
        
        try:
            if hasattr(self.cache, 'set'):
                self.cache.set(key, value, timeout=timeout) if timeout else self.cache.set(key, value)
            elif isinstance(self.cache, dict):
                self.cache[key] = value
        except Exception as e:
            logger.warning(f"Erreur cache set: {e}")
        
    def get_weather_data(self, city=None, api_key=None):
        """
        Récupère les données météo avec système de cache intelligent.
        
        Args:
            city (str, optional): Nom de la ville
            api_key (str, optional): Clé API OpenWeatherMap
            
        Returns:
            dict: Données météo formatées ou message d'erreur
        """
        try:
            # Configuration depuis la base de données ou l'environnement
            from app.models.config import WeatherConfig
            config = WeatherConfig.get_config()
            
            # Utiliser les paramètres fournis ou la configuration
            final_city = city or config.city or current_app.config.get('WEATHER_CITY', 'Strasbourg')
            final_api_key = api_key or config.api_key or current_app.config.get('WEATHER_API_KEY')
            
            # Vérifier si le widget météo est activé
            if not config.show_weather:
                return self._format_error_response("Widget météo désactivé")
            
            if not final_api_key:
                logger.warning("Clé API OpenWeatherMap manquante")
                return self._format_error_response("Configuration manquante : clé API OpenWeatherMap non configurée")
            
            # Clé de cache spécialisée
            cache_key = f"weather_data_{final_city.lower().replace(' ', '_')}"
            
            # Tentative de récupération depuis le cache
            cached_data = self._cache_get(cache_key)
            if cached_data:
                logger.debug(f"Données météo récupérées depuis le cache pour {final_city}")
                return cached_data
            
            # Récupération des données depuis l'API
            weather_data = self._fetch_weather_data(final_city, final_api_key)
            
            if weather_data.get('success'):
                # Mise en cache avec timeout configuré
                cache_timeout = current_app.config.get('CACHE_TIMEOUTS', {}).get('weather', 1800)  # 30min par défaut
                self._cache_set(cache_key, weather_data, timeout=cache_timeout)
                logger.debug(f"Données météo mises en cache pour {cache_timeout}s")
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données météo: {str(e)}")
            return self._format_error_response(f"Erreur technique: {str(e)}")
    
    def _fetch_weather_data(self, city, api_key):
        """
        Récupère les données météo depuis l'API OpenWeatherMap.
        
        Args:
            city (str): Nom de la ville
            api_key (str): Clé API
            
        Returns:
            dict: Données météo formatées
        """
        try:
            # Configuration de la requête avec optimisations
            base_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': api_key,
                'units': 'metric',
                'lang': 'fr'  # Interface en français
            }
            
            # Requête avec timeout optimisé
            timeout = current_app.config.get('REQUEST_TIMEOUT', 10)
            response = requests.get(base_url, params=params, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Formatage avancé des données pour l'affichage TV
                formatted_data = {
                    'success': True,
                    'city': data['name'],
                    'country': data['sys']['country'],
                    'temperature': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'].title(),
                    'icon': data['weather'][0]['icon'],
                    'wind_speed': round(data.get('wind', {}).get('speed', 0) * 3.6, 1),  # Conversion m/s vers km/h
                    'wind_direction': data.get('wind', {}).get('deg', 0),
                    'visibility': data.get('visibility', 0) // 1000 if data.get('visibility') else None,  # En km
                    'emoji': self._get_weather_emoji(data['weather'][0]['icon'], data['weather'][0]['id']),
                    'last_update': datetime.now(pytz.timezone('Europe/Paris')).strftime('%H:%M'),
                    'timestamp': datetime.now().isoformat(),
                    'quality_index': self._calculate_weather_quality(data)
                }
                
                # Ajout de données pour l'affichage TV
                formatted_data.update({
                    'display_text': f"{formatted_data['temperature']}°C • {formatted_data['description']}",
                    'display_details': f"Ressenti {formatted_data['feels_like']}°C • Humidité {formatted_data['humidity']}%",
                    'wind_text': f"{formatted_data['wind_speed']} km/h" if formatted_data['wind_speed'] > 0 else "Calme"
                })
                
                logger.info(f"Données météo récupérées pour {city}: {formatted_data['temperature']}°C")
                return formatted_data
                
            elif response.status_code == 401:
                logger.error("Clé API OpenWeatherMap invalide")
                return self._format_error_response("Clé API invalide ou expirée")
            elif response.status_code == 404:
                logger.error(f"Ville '{city}' non trouvée")
                return self._format_error_response(f"Ville '{city}' non trouvée")
            else:
                logger.error(f"Erreur API OpenWeatherMap: {response.status_code}")
                return self._format_error_response(f"Erreur API (code {response.status_code})")
                
        except requests.exceptions.Timeout:
            logger.error("Timeout lors de la requête météo")
            return self._format_error_response("Délai d'attente dépassé")
        except requests.exceptions.ConnectionError:
            logger.error("Erreur de connexion à l'API météo")
            return self._format_error_response("Erreur de connexion réseau")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération météo: {str(e)}")
            return self._format_error_response(f"Erreur technique: {str(e)}")
    
    def _get_weather_emoji(self, icon_code, weather_id):
        """
        Retourne l'emoji météo approprié basé sur l'icône et l'ID météo.
        Optimisé pour l'affichage sur écrans TV avec des emojis visibles.
        
        Args:
            icon_code (str): Code icône OpenWeatherMap
            weather_id (int): ID de condition météo
            
        Returns:
            str: Emoji météo
        """
        # Mapping précis basé sur les conditions météorologiques
        weather_emojis = {
            # Ciel clair
            '01d': '☀️', '01n': '🌙',
            # Peu nuageux
            '02d': '🌤️', '02n': '☁️',
            # Nuageux
            '03d': '☁️', '03n': '☁️',
            '04d': '☁️', '04n': '☁️',
            # Pluie
            '09d': '🌧️', '09n': '🌧️',
            '10d': '🌦️', '10n': '🌧️',
            # Orages
            '11d': '⛈️', '11n': '⛈️',
            # Neige
            '13d': '🌨️', '13n': '🌨️',
            # Brouillard
            '50d': '🌫️', '50n': '🌫️'
        }
        
        # Emojis basés sur l'ID météo pour plus de précision
        id_emojis = {
            200: '⛈️', 201: '⛈️', 202: '⛈️',  # Orages
            300: '🌦️', 301: '🌧️', 302: '🌧️',  # Bruine
            500: '🌦️', 501: '🌧️', 502: '🌧️', 503: '🌧️', 504: '🌧️',  # Pluie
            600: '🌨️', 601: '❄️', 602: '❄️',  # Neige
            701: '🌫️', 741: '🌫️',  # Brouillard
            800: '☀️' if 'd' in icon_code else '🌙',  # Ciel clair
            801: '🌤️', 802: '⛅', 803: '☁️', 804: '☁️'  # Nuages
        }
        
        return id_emojis.get(weather_id) or weather_emojis.get(icon_code) or '🌡️'
    
    def _calculate_weather_quality(self, data):
        """
        Calcule un indice de qualité météo pour l'affichage.
        
        Args:
            data (dict): Données météo brutes
            
        Returns:
            str: Indice de qualité ('excellent', 'bon', 'moyen', 'mauvais')
        """
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        weather_id = data['weather'][0]['id']
        
        score = 0
        
        # Score basé sur la température (optimisé pour la France)
        if 18 <= temp <= 25:
            score += 3
        elif 15 <= temp <= 28:
            score += 2
        elif 10 <= temp <= 30:
            score += 1
        
        # Score basé sur l'humidité
        if 40 <= humidity <= 60:
            score += 2
        elif 30 <= humidity <= 70:
            score += 1
        
        # Score basé sur les conditions
        if weather_id == 800:  # Ciel clair
            score += 3
        elif weather_id in [801, 802]:  # Peu nuageux
            score += 2
        elif weather_id in [803, 804]:  # Nuageux
            score += 1
        elif weather_id >= 200 and weather_id < 600:  # Pluie/orage
            score -= 1
        
        # Classification
        if score >= 7:
            return 'excellent'
        elif score >= 5:
            return 'bon'
        elif score >= 3:
            return 'moyen'
        else:
            return 'mauvais'
    
    def _format_error_response(self, error_message):
        """
        Formate une réponse d'erreur standardisée.
        
        Args:
            error_message (str): Message d'erreur
            
        Returns:
            dict: Réponse d'erreur formatée
        """
        return {
            'success': False,
            'error': error_message,
            # Compatibilité avec les différents templates
            'temp': None,
            'temperature': None,
            'description': 'Service indisponible',
            'icon': '01d',
            'icon_emoji': '❌',
            'emoji': '❌',
            'city': 'Inconnue',
            'status': 'error',
            # Données pour affichage TV
            'display_text': 'Données météo indisponibles',
            'display_details': error_message,
            'timestamp': datetime.now().isoformat(),
            'last_update': 'Erreur'
        }
    
    def clear_cache(self, city=None):
        """
        Efface le cache météo pour une ville ou tout le cache météo.
        
        Args:
            city (str, optional): Ville spécifique à effacer du cache
        """
        if not self.cache:
            return
        
        try:
            if city:
                cache_key = f"weather_data_{city.lower().replace(' ', '_')}"
                self.cache.delete(cache_key)
                logger.info(f"Cache météo effacé pour {city}")
            else:
                # Effacer tout le cache météo (pattern matching si possible)
                if hasattr(self.cache, 'delete_many'):
                    # Pour Redis ou cache avancé
                    pattern = "weather_data_*"
                    self.cache.delete_many(pattern)
                else:
                    # Fallback pour cache simple
                    logger.warning("Cache météo: effacement global non supporté par ce type de cache")
                logger.info("Cache météo global effacé")
        except Exception as e:
            logger.error(f"Erreur lors de l'effacement du cache météo: {str(e)}")

    def get_forecast_summary(self, city=None, api_key=None):
        """Récupère un résumé des prévisions pour les prochaines heures."""
        cache_key = f"weather_forecast_{city or 'default'}"
        cached_forecast = self._cache_get(cache_key)
        
        if cached_forecast:
            return cached_forecast
        
        try:
            from app.models.config import WeatherConfig
            config = WeatherConfig.get_config()
            
            final_city = city or config.city or current_app.config.get('WEATHER_CITY', 'Strasbourg')
            final_api_key = api_key or config.api_key or current_app.config.get('WEATHER_API_KEY')
            
            if not final_api_key:
                return self._format_error_response("Clé API manquante")
            
            base_url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                'q': final_city,
                'appid': final_api_key,
                'units': 'metric',
                'cnt': 8,  # 8 prochaines prévisions (24h)
                'lang': 'fr'
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                forecast_summary = {
                    'success': True,
                    'city': data['city']['name'],
                    'next_hours': []
                }
                
                for item in data['list'][:4]:  # 4 prochaines prévisions (12h)
                    forecast_summary['next_hours'].append({
                        'time': datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
                        'temperature': round(item['main']['temp']),
                        'description': item['weather'][0]['description'].title(),
                        'emoji': self._get_weather_emoji(item['weather'][0]['icon'], item['weather'][0]['id'])
                    })
                
                # Cache pour 1 heure
                self._cache_set(cache_key, forecast_summary, timeout=3600)
                return forecast_summary
            else:
                return self._format_error_response(f"Erreur prévisions (code {response.status_code})")
                
        except Exception as e:
            logger.error(f"Erreur récupération prévisions: {e}")
            return self._format_error_response(f"Erreur technique: {str(e)}")

# Instance du service créée via lazy loading dans __init__.py 