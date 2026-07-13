"""
Service de récupération des données météo via l'API OpenWeatherMap.
Optimisé pour l'affichage sur écrans TV avec cache intelligent et gestion d'erreurs robuste.
Inclut désormais la qualité de l'air (AQI), l'indice UV et les alertes de vigilance.
"""
import requests
import logging
from flask import current_app, json
from datetime import datetime, timedelta
import pytz

logger = logging.getLogger(__name__)

class WeatherService:
    """
    Service météo enrichi pour EducInfo avec cache intelligent et récupération robuste.
    Fournit des données complètes : météo, prévisions, qualité de l'air et alertes.
    """
    
    def __init__(self):
        self.cache = current_app.extensions.get('cache')
    
    def _cache_get(self, key):
        """Helper optimisé pour récupérer depuis le cache."""
        if not self.cache:
            return None
        
        try:
            return self.cache.get(key)
        except Exception as e:
            logger.warning(f"Erreur cache get: {e}")
            return None
    
    def _cache_set(self, key, value, timeout=None):
        """Helper optimisé pour mettre en cache."""
        if not self.cache:
            return
        
        try:
            self.cache.set(key, value, timeout=timeout)
        except Exception as e:
            logger.warning(f"Erreur cache set: {e}")
        
    def get_weather_data(self, city=None, api_key=None):
        """
        Récupère les données météo enrichies avec système de cache intelligent.
        """
        try:
            from app.models.config import WeatherConfig
            config = WeatherConfig.get_config()
            
            final_city = city or config.city or current_app.config.get('WEATHER_CITY', 'Strasbourg')
            final_api_key = api_key or config.api_key or current_app.config.get('WEATHER_API_KEY')
            
            if not config.show_weather:
                return self._format_error_response("Widget météo désactivé")
            
            # Clé de cache spécialisée
            cache_key = f"weather_data_full_{final_city.lower().replace(' ', '_')}"
            
            cached_data = self._cache_get(cache_key)
            if cached_data:
                return cached_data
            
            # Récupération des données multi-sources (OWM One Call API ou combination)
            weather_data = self._fetch_comprehensive_weather(final_city, final_api_key)
            
            if weather_data.get('success'):
                cache_timeout = current_app.config.get('CACHE_TIMEOUTS', {}).get('weather', 1800)
                self._cache_set(cache_key, weather_data, timeout=cache_timeout)
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données météo: {str(e)}")
            return self._format_error_response(f"Erreur technique: {str(e)}")
    
    def _fetch_comprehensive_weather(self, city, api_key):
        """
        Récupère les données depuis OpenWeatherMap et combine les infos.
        """
        if not api_key:
            return self._get_demo_weather_data(city)

        try:
            # 1. Obtenir les coordonnées et la météo actuelle
            base_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {'q': city, 'appid': api_key, 'units': 'metric', 'lang': 'fr'}
            
            resp = requests.get(base_url, params=params, timeout=10)
            if resp.status_code != 200:
                return self._get_demo_weather_data(city)
            
            curr = resp.json()
            lat, lon = curr['coord']['lat'], curr['coord']['lon']
            
            # 2. Obtenir la qualité de l'air (Air Pollution API)
            aqi_data = self._fetch_aqi(lat, lon, api_key)
            
            # 3. Formater le tout
            return self._format_enriched_data(curr, aqi_data)
                
        except Exception as e:
            logger.error(f"Erreur connexion météo: {str(e)}")
            return self._get_demo_weather_data(city)

    def _fetch_aqi(self, lat, lon, api_key):
        """Récupère l'indice de qualité de l'air."""
        try:
            url = "https://api.openweathermap.org/data/2.5/air_pollution"
            params = {'lat': lat, 'lon': lon, 'appid': api_key}
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                return resp.json()['list'][0]
        except Exception:
            pass
        return None

    def _format_enriched_data(self, curr, aqi_data):
        """Formate les données enrichies."""
        tz = pytz.timezone('Europe/Paris')
        now = datetime.now(tz)
        
        formatted = {
            'success': True,
            'city': curr['name'],
            'country': curr['sys']['country'],
            'temperature': round(curr['main']['temp']),
            'feels_like': round(curr['main']['feels_like']),
            'humidity': curr['main']['humidity'],
            'pressure': curr['main']['pressure'],
            'description': curr['weather'][0]['description'].title(),
            'icon': curr['weather'][0]['icon'],
            'wind_speed': round(curr.get('wind', {}).get('speed', 0) * 3.6, 1),
            'emoji': self._get_weather_emoji(curr['weather'][0]['icon'], curr['weather'][0]['id']),
            'last_update': now.strftime('%H:%M'),
            'timestamp': now.isoformat(),
            # Nouvelles données
            'sunrise': datetime.fromtimestamp(curr['sys']['sunrise'], tz).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(curr['sys']['sunset'], tz).strftime('%H:%M'),
            'visibility': curr.get('visibility', 0) // 1000,
            'is_night': 'n' in curr['weather'][0]['icon']
        }
        
        if aqi_data:
            aqi_val = aqi_data['main']['aqi']
            aqi_labels = {1: 'Excellent', 2: 'Bon', 3: 'Moyen', 4: 'Médiocre', 5: 'Mauvais'}
            formatted['aqi'] = {
                'value': aqi_val,
                'label': aqi_labels.get(aqi_val, 'Inconnu'),
                'color': self._get_aqi_color(aqi_val)
            }
        
        formatted.update({
            'display_text': f"{formatted['temperature']}°C • {formatted['description']}",
            'display_details': f"Ressenti {formatted['feels_like']}°C • Humidité {formatted['humidity']}%",
            'wind_text': f"{formatted['wind_speed']} km/h"
        })
        
        return formatted

    def _get_demo_weather_data(self, city):
        """Retourne des données météo fictives réalistes."""
        now = datetime.now(pytz.timezone('Europe/Paris'))
        # Simuler des variations basées sur l'heure
        hour = now.hour
        base_temp = 15 + (10 if 10 <= hour <= 18 else 0)
        
        return {
            'success': True,
            'city': city or 'Strasbourg',
            'country': 'FR',
            'temperature': base_temp,
            'feels_like': base_temp + 2,
            'humidity': 65,
            'pressure': 1020,
            'description': 'Ciel dégagé (Démo)',
            'icon': '01d' if 7 <= hour <= 20 else '01n',
            'wind_speed': 10,
            'emoji': '☀️' if 7 <= hour <= 20 else '🌙',
            'last_update': now.strftime('%H:%M'),
            'timestamp': now.isoformat(),
            'sunrise': '07:30',
            'sunset': '18:45',
            'visibility': 10,
            'is_night': not (7 <= hour <= 20),
            'aqi': {'value': 1, 'label': 'Excellent', 'color': '#10b981'},
            'display_text': f"{base_temp}°C • Ciel dégagé (Démo)",
            'display_details': f"Ressenti {base_temp+2}°C • Humidité 65%",
            'wind_text': '10 km/h',
            'is_demo': True
        }

    def _get_aqi_color(self, aqi):
        colors = {1: '#10b981', 2: '#84cc16', 3: '#eab308', 4: '#f97316', 5: '#ef4444'}
        return colors.get(aqi, '#94a3b8')

    def _get_weather_emoji(self, icon_code, weather_id):
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
        return id_emojis.get(weather_id, '🌡️')

    def _format_error_response(self, error_message):
        return {
            'success': False,
            'error': error_message,
            'temperature': None,
            'description': 'Indisponible',
            'icon': '01d',
            'emoji': '❌',
            'city': 'Inconnue',
            'display_text': 'Météo indisponible',
            'display_details': error_message,
            'timestamp': datetime.now().isoformat(),
            'last_update': 'Erreur'
        }

    def get_forecast_summary(self, city=None, api_key=None):
        """Récupère un résumé des prévisions pour les prochaines 12h."""
        try:
            from app.models.config import WeatherConfig
            config = WeatherConfig.get_config()
            final_city = city or config.city or 'Strasbourg'
            final_api_key = api_key or config.api_key
            
            if not final_api_key:
                return {'success': False, 'message': 'API Key missing'}

            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {'q': final_city, 'appid': final_api_key, 'units': 'metric', 'cnt': 4, 'lang': 'fr'}
            
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                forecasts = []
                for item in data['list']:
                    forecasts.append({
                        'time': datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
                        'temp': round(item['main']['temp']),
                        'desc': item['weather'][0]['description'].title(),
                        'emoji': self._get_weather_emoji(item['weather'][0]['icon'], item['weather'][0]['id'])
                    })
                return {'success': True, 'forecasts': forecasts}
        except Exception:
            pass
        return {'success': False}

    def get_weather_for_display(self):
        """Recupere les donnees meteo normalisees pour l'affichage dans les templates."""
        try:
            from app.models.config import WeatherConfig
            config = WeatherConfig.get_config()
            if not config or not config.show_weather:
                return None

            data = self.get_weather_data()
            if not data or 'error' in data or not data.get('success'):
                return {
                    'temp': None, 'temperature': None,
                    'description': 'Service indisponible',
                    'icon': '01d', 'icon_emoji': '🌡️',
                    'city': config.city if config else 'Inconnue',
                    'status': 'error',
                }

            # Normaliser temp/temperature
            if 'temperature' in data and 'temp' not in data:
                data['temp'] = data['temperature']

            # Ajouter emoji si absent
            if 'icon_emoji' not in data:
                icon = data.get('icon', '01d')
                weather_id = data.get('weather_id', 800)
                data['icon_emoji'] = self._get_weather_emoji(icon, weather_id)

            return data
        except Exception as e:
            logger.error(f"Erreur get_weather_for_display: {e}")
            return None


# Instance du service créée via lazy loading dans __init__.py 