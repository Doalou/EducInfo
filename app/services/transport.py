"""
Service de récupération des données de transport via l'API CTS Strasbourg.
Optimisé pour l'affichage temps réel sur écrans TV avec gestion intelligente du cache.
"""
import requests
import logging
from flask import current_app
from datetime import datetime, timedelta
import pytz
from dateutil import parser

logger = logging.getLogger(__name__)

class TransportService:
    """
    Service pour récupérer les données de transport via l'API CTS.
    Optimisé pour l'affichage temps réel sur écrans TV avec mise à jour fréquente.
    """
    # Constantes optimisées pour l'affichage temps réel
    CACHE_DURATION = 30  # 30 secondes pour les données temps réel
    REQUEST_TIMEOUT = 8  # Timeout augmenté pour la stabilité
    
    def __init__(self):
        self.cache = current_app.extensions.get('cache')
    
    def _cache_get(self, key):
        """Helper pour récupérer depuis le cache avec gestion des différents types."""
        if not self.cache:
            return None
        
        try:
            if hasattr(self.cache, 'get'):
                return self.cache.get(key)
            elif isinstance(self.cache, dict):
                return self.cache.get(key)
            else:
                return None
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération du cache transport: {e}")
            return None
    
    def _cache_set(self, key, value, timeout=None):
        """Helper pour mettre en cache avec gestion des différents types."""
        if not self.cache:
            return
        
        try:
            if hasattr(self.cache, 'set'):
                if timeout:
                    self.cache.set(key, value, timeout=timeout)
                else:
                    self.cache.set(key, value)
            elif isinstance(self.cache, dict):
                # Cache simple comme dictionnaire
                self.cache[key] = value
            else:
                logger.warning(f"Type de cache transport non supporté: {type(self.cache)}")
        except Exception as e:
            logger.warning(f"Erreur lors de la mise en cache transport: {e}")
        
    def get_stop_arrivals(self, stop_code=None, vehicle_mode=None, api_token=None, 
                          preview_interval=None, max_visits=None):
        """
        Récupère les 8 prochains passages en temps réel pour un arrêt CTS.
        Optimisé pour l'affichage TV avec formatage adapté.
        
        Args:
            stop_code (str, optional): Code d'arrêt CTS (3 chiffres)
            vehicle_mode (str, optional): Mode de transport ('bus', 'tram', 'undefined')
            api_token (str, optional): Token API CTS
            preview_interval (str, optional): Intervalle de prévision (format ISO 8601)
            max_visits (int, optional): Nombre maximum de passages
            
        Returns:
            dict: Données des prochains passages formatées pour l'affichage TV
        """
        try:
            # Configuration depuis la base de données ou l'environnement
            from app.models.config import WidgetConfig
            config = WidgetConfig.get_config()
            
            # Paramètres effectifs avec fallback intelligent
            final_stop_code = stop_code or config.cts_stop_code or current_app.config.get('CTS_STOP_CODE')
            final_api_token = api_token or config.cts_api_token or current_app.config.get('CTS_API_TOKEN')
            final_vehicle_mode = vehicle_mode or config.cts_vehicle_mode or 'undefined'
            final_preview_interval = preview_interval or current_app.config.get('CTS_PREVIEW_INTERVAL', 'PT90M')
            final_max_visits = max_visits or current_app.config.get('CTS_MAX_VISITS', 8)
            
            # Vérifications de configuration
            if not config.show_transports:
                return self._format_error_response("Widget transport désactivé", "disabled")
                
            if not final_api_token:
                logger.warning("Token API CTS manquant")
                return self._format_error_response("Configuration manquante : token API CTS requis", "config_error")
                
            if not final_stop_code:
                logger.warning("Code d'arrêt CTS manquant")
                return self._format_error_response("Configuration manquante : code d'arrêt CTS requis", "config_error")
            
            # Validation du format du code d'arrêt
            if not (final_stop_code.isdigit() and len(final_stop_code) == 3):
                logger.error(f"Format de code d'arrêt invalide: {final_stop_code}")
                return self._format_error_response("Code d'arrêt invalide : doit être 3 chiffres", "invalid_stop")
            
            # Clé de cache spécialisée pour les données temps réel
            cache_key = f"transport_cts_{final_stop_code}_{final_vehicle_mode}_{final_max_visits}"
            
            # Vérifier le cache (durée courte pour temps réel)
            cached_data = self._cache_get(cache_key)
            if cached_data:
                logger.debug(f"Données transport récupérées depuis le cache pour l'arrêt {final_stop_code}")
                return cached_data
            
            # Récupération des données en temps réel
            base_url = current_app.config.get('CTS_BASE_URL', 'https://api.cts-strasbourg.eu')
            arrivals_data = self._fetch_arrivals_data(
                base_url,
                final_stop_code,
                final_vehicle_mode,
                final_api_token,
                final_preview_interval,
                final_max_visits
            )
            
            if arrivals_data.get('success'):
                # Cache très court pour données temps réel
                cache_timeout = current_app.config.get('CACHE_TIMEOUTS', {}).get('transport', self.CACHE_DURATION)
                self._cache_set(cache_key, arrivals_data, timeout=cache_timeout)
                logger.debug(f"Données transport mises en cache pour {cache_timeout}s")
            
            return arrivals_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données transport: {str(e)}")
            return self._format_error_response(f"Erreur technique: {str(e)}", "error")
    
    def _fetch_arrivals_data(self, base_url, stop_code, vehicle_mode, api_token, 
                            preview_interval, max_visits):
        """
        Interroge l'API CTS pour récupérer les horaires de passage.
        Utilise l'endpoint stop-monitoring optimisé pour l'affichage temps réel.
        
        Args:
            base_url (str): URL de base de l'API CTS
            stop_code (str): Code d'arrêt à 3 chiffres
            vehicle_mode (str): Mode de transport
            api_token (str): Token d'authentification
            preview_interval (str): Intervalle de prévision
            max_visits (int): Nombre max de passages
            
        Returns:
            dict: Données formatées des prochains passages
        """
        try:
            # Configuration de l'endpoint avec paramètres optimisés
            endpoint = f"{base_url}/v1/siri/2.0/stop-monitoring"
            
            # Paramètres de requête selon spec CTS
            # MonitoringRef peut être un tableau selon la doc, mais un seul arrêt suffit
            params = {
                'MonitoringRef': [stop_code],  # Utiliser un tableau comme spécifié dans la doc
                'MaximumStopVisits': max_visits,
                'MinimumStopVisitsPerLine': 1,  # Au moins 1 passage par ligne
                'PreviewInterval': preview_interval,
                'VehicleMode': vehicle_mode if vehicle_mode != 'undefined' else None,
                'RequestorRef': f'EducInfo-{current_app.config.get("APP_VERSION", "2.0.0")}',
                'RemoveCheckOut': True  # Ne pas retourner les départs "anciens"
            }
            
            # Supprimer les paramètres None
            params = {k: v for k, v in params.items() if v is not None}
            
            # Headers sans authentification Bearer (HTTP Basic sera utilisé)
            headers = {
                'User-Agent': f'EducInfo/{current_app.config.get("APP_VERSION", "2.0.0")}',
                'Accept': 'application/json'
            }
            
            # Authentification HTTP Basic selon la documentation CTS
            # "You must fill the username field of the Basic HTTP Auth Header with your token"
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(api_token, '')  # token comme username, password vide
            
            logger.debug(f"Requête CTS pour arrêt {stop_code} (mode: {vehicle_mode})")
            
            # Requête API avec timeout adapté et authentification HTTP Basic
            response = requests.get(
                endpoint,
                params=params,
                headers=headers,
                auth=auth,
                timeout=self.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validation de la structure de réponse
                service_delivery = data.get('ServiceDelivery', {})
                stop_monitoring_delivery = service_delivery.get('StopMonitoringDelivery', [])
                
                if not stop_monitoring_delivery:
                    logger.warning(f"Aucune donnée de monitoring pour l'arrêt {stop_code}")
                    return self._format_error_response("Aucune donnée disponible pour cet arrêt", "no_data")
                
                # Extraction des visites d'arrêt
                monitored_stop_visits = stop_monitoring_delivery[0].get('MonitoredStopVisit', [])
                
                if not monitored_stop_visits:
                    logger.info(f"Aucun passage prévu pour l'arrêt {stop_code}")
                    return {
                        'success': True,
                        'arrivals': [],
                        'stop_code': stop_code,
                        'stop_name': f"Arrêt {stop_code}",
                        'last_update': datetime.now(pytz.timezone('Europe/Paris')).strftime('%H:%M:%S'),
                        'timestamp': datetime.now().isoformat(),
                        'message': "Aucun passage prévu dans les prochaines heures"
                    }
                
                # Formatage des passages pour l'affichage TV
                formatted_arrivals = self._format_arrivals(monitored_stop_visits, stop_code)
                
                logger.info(f"Récupération réussie: {len(formatted_arrivals)} passages pour l'arrêt {stop_code}")
                
                return {
                    'success': True,
                    'arrivals': formatted_arrivals,
                    'stop_code': stop_code,
                    'stop_name': formatted_arrivals[0].get('stop_name', f"Arrêt {stop_code}") if formatted_arrivals else f"Arrêt {stop_code}",
                    'last_update': datetime.now(pytz.timezone('Europe/Paris')).strftime('%H:%M:%S'),
                    'timestamp': datetime.now().isoformat(),
                    'total_arrivals': len(formatted_arrivals)
                }
                
            elif response.status_code == 401:
                logger.error("Token API CTS invalide ou authentification échouée")
                return self._format_error_response("Token API CTS invalide ou expiré", "auth_error")
            elif response.status_code == 403:
                logger.error("Accès refusé - Token API CTS invalide ou droits insuffisants")
                return self._format_error_response("Accès refusé à l'API CTS", "auth_error")
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Paramètres de requête invalides')
                    logger.error(f"Requête CTS invalide pour l'arrêt {stop_code}: {error_msg}")
                    return self._format_error_response(f"Requête invalide: {error_msg}", "bad_request")
                except Exception:
                    logger.error(f"Paramètres de requête invalides pour l'arrêt {stop_code}")
                    return self._format_error_response("Paramètres de requête invalides", "bad_request")
            elif response.status_code == 404:
                logger.error(f"Arrêt {stop_code} non trouvé dans le réseau CTS")
                return self._format_error_response(f"Arrêt {stop_code} non trouvé", "not_found")
            elif response.status_code == 500:
                logger.error("Erreur technique du service CTS")
                return self._format_error_response("Service CTS temporairement indisponible", "service_error")
            else:
                logger.error(f"Erreur API CTS: {response.status_code} - {response.text[:200]}")
                return self._format_error_response(f"Erreur API CTS (code {response.status_code})", "api_error")
                
        except requests.exceptions.Timeout:
            logger.error("Timeout lors de la requête CTS")
            return self._format_error_response("Délai d'attente dépassé pour les données transport", "timeout")
        except requests.exceptions.ConnectionError:
            logger.error("Erreur de connexion à l'API CTS")
            return self._format_error_response("Erreur de connexion au service transport", "connection_error")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération CTS: {str(e)}")
            return self._format_error_response(f"Erreur technique: {str(e)}", "error")
    
    def _format_arrivals(self, visits, stop_code):
        """
        Formate les données de passage pour l'affichage TV optimisé.
        Trie par temps d'attente et ajoute des indicateurs visuels.
        
        Args:
            visits (list): Liste des visites d'arrêt depuis l'API
            stop_code (str): Code de l'arrêt
            
        Returns:
            list: Liste des passages formatés pour l'affichage TV
        """
        formatted_arrivals = []
        
        for visit in visits:
            try:
                monitored_journey = visit.get('MonitoredVehicleJourney', {})
                monitored_call = monitored_journey.get('MonitoredCall', {})
                
                # Extraction des données essentielles
                line_ref = monitored_journey.get('LineRef', 'N/A')
                published_line_name = monitored_journey.get('PublishedLineName', line_ref)
                destination_name = monitored_journey.get('DestinationName', 'Destination inconnue')
                destination_short = monitored_journey.get('DestinationShortName', destination_name)
                via = monitored_journey.get('Via')
                
                # Formatage de la destination avec VIA si présent
                if via:
                    full_destination = f"{destination_name} via {via}"
                    display_destination = f"{destination_short} via {via}"
                else:
                    full_destination = destination_name
                    display_destination = destination_short
                
                # Temps de passage (priorité à l'heure de départ)
                expected_departure = monitored_call.get('ExpectedDepartureTime')
                expected_arrival = monitored_call.get('ExpectedArrivalTime')
                passage_time = expected_departure or expected_arrival
                
                if not passage_time:
                    logger.warning(f"Pas d'heure de passage pour un véhicule ligne {published_line_name}")
                    continue
                
                # Calcul du temps d'attente
                time_left_info = self._calculate_time_left(passage_time)
                
                # Mode de transport avec icône
                vehicle_mode = monitored_journey.get('VehicleMode', 'undefined')
                transport_icon = {
                    'bus': '🚌',
                    'tram': '🚋',
                    'coach': '🚌'
                }.get(vehicle_mode, '🚌')
                
                # Indicateur temps réel
                extension = monitored_call.get('Extension', {})
                is_realtime = extension.get('IsRealTime', False)
                realtime_indicator = '🔴' if is_realtime else '⏰'
                
                # Formatage pour l'affichage TV
                formatted_arrival = {
                    'line_name': published_line_name,
                    'line_ref': line_ref,
                    'destination': full_destination,
                    'destination_display': display_destination,
                    'via': via,
                    'expected_time': time_left_info['time_str'],
                    'expected_datetime': passage_time,
                    'minutes_left': time_left_info['minutes'],
                    'time_left_text': time_left_info['display_text'],
                    'time_left_class': time_left_info['css_class'],
                    'is_realtime': is_realtime,
                    'realtime_indicator': realtime_indicator,
                    'vehicle_mode': vehicle_mode,
                    'transport_icon': transport_icon,
                    'stop_code': stop_code,
                    'stop_name': monitored_call.get('StopPointName', f'Arrêt {stop_code}'),
                    'order': monitored_call.get('Order', 0),
                    'data_source': extension.get('DataSource', 'CTS'),
                    'experimentation': extension.get('Experimentation'),
                    # Données pour l'affichage TV
                    'display_line': f"{transport_icon} {published_line_name}",
                    'urgency_level': time_left_info['urgency_level']
                }
                
                formatted_arrivals.append(formatted_arrival)
                
            except Exception as e:
                logger.warning(f"Erreur lors du formatage d'un passage: {str(e)}")
                continue
        
        # Tri par temps d'attente croissant
        def sort_key(x):
            # Mettre les valeurs None à la fin
            return x['minutes_left'] if x['minutes_left'] is not None else 9999
            
        formatted_arrivals.sort(key=sort_key)
        
        # Limiter au nombre maximum demandé
        max_results = current_app.config.get('TRANSPORT_MAX_RESULTS', 8)
        return formatted_arrivals[:max_results]
    
    def _calculate_time_left(self, arrival_time_str):
        """
        Calcule le temps d'attente avec formatage optimisé pour l'affichage TV.
        
        Args:
            arrival_time_str (str): Heure d'arrivée au format ISO 8601
            
        Returns:
            dict: Informations de temps formatées
        """
        try:
            # Parsing de l'heure avec gestion des fuseaux horaires
            arrival_time = parser.isoparse(arrival_time_str)
            current_time = datetime.now(pytz.timezone('Europe/Paris'))
            
            # Assurer que les deux temps sont dans le même fuseau
            if arrival_time.tzinfo is None:
                arrival_time = pytz.timezone('Europe/Paris').localize(arrival_time)
            elif arrival_time.tzinfo != current_time.tzinfo:
                arrival_time = arrival_time.astimezone(current_time.tzinfo)
            
            # Calcul de la différence
            time_diff = arrival_time - current_time
            minutes_left = int(time_diff.total_seconds() / 60)
            
            # Formatage pour l'affichage
            time_str = arrival_time.strftime('%H:%M')
            
            # Texte d'affichage optimisé pour TV
            if minutes_left < 0:
                display_text = "Parti"
                css_class = "text-gray-500"
                urgency_level = "passed"
            elif minutes_left == 0:
                display_text = "Maintenant"
                css_class = "text-red-600 font-bold animate-pulse"
                urgency_level = "immediate"
            elif minutes_left == 1:
                display_text = "1 min"
                css_class = "text-red-500 font-bold"
                urgency_level = "urgent"
            elif minutes_left <= 3:
                display_text = f"{minutes_left} min"
                css_class = "text-orange-500 font-semibold"
                urgency_level = "soon"
            elif minutes_left <= 10:
                display_text = f"{minutes_left} min"
                css_class = "text-blue-600"
                urgency_level = "normal"
            else:
                display_text = time_str
                css_class = "text-gray-600"
                urgency_level = "later"
            
            return {
                'minutes': minutes_left,
                'time_str': time_str,
                'display_text': display_text,
                'css_class': css_class,
                'urgency_level': urgency_level,
                'arrival_time': arrival_time
            }
            
        except Exception as e:
            logger.warning(f"Erreur lors du calcul du temps: {str(e)}")
            return {
                'minutes': None,
                'time_str': 'N/A',
                'display_text': 'Heure inconnue',
                'css_class': 'text-gray-500',
                'urgency_level': 'unknown',
                'arrival_time': None
            }
    
    def _format_error_response(self, error_message, error_type="error"):
        """
        Formate une réponse d'erreur standardisée pour l'affichage TV.
        
        Args:
            error_message (str): Message d'erreur
            error_type (str): Type d'erreur pour le traitement
            
        Returns:
            dict: Réponse d'erreur formatée
        """
        # Icônes et messages selon le type d'erreur
        error_config = {
            'disabled': {
                'icon': '🚫',
                'title': 'Widget désactivé',
                'suggestion': 'Activez le widget transport dans les paramètres'
            },
            'config_error': {
                'icon': '⚙️',
                'title': 'Configuration manquante',
                'suggestion': 'Configurez le token API et le code d\'arrêt'
            },
            'auth_error': {
                'icon': '🔐',
                'title': 'Authentification échouée',
                'suggestion': 'Vérifiez le token API CTS'
            },
            'not_found': {
                'icon': '📍',
                'title': 'Arrêt non trouvé',
                'suggestion': 'Vérifiez le code d\'arrêt'
            },
            'timeout': {
                'icon': '⏱️',
                'title': 'Délai dépassé',
                'suggestion': 'Vérifiez la connexion réseau'
            },
            'no_data': {
                'icon': '📭',
                'title': 'Aucune donnée',
                'suggestion': 'Aucun passage prévu actuellement'
            }
        }
        
        config = error_config.get(error_type, {
            'icon': '❌',
            'title': 'Erreur technique',
            'suggestion': 'Réessayez dans quelques instants'
        })
        
        return {
            'success': False,
            'error': error_message,
            'error_type': error_type,
            'arrivals': [],
            'icon': config['icon'],
            'title': config['title'],
            'suggestion': config['suggestion'],
            'display_text': f"{config['icon']} {config['title']}",
            'display_details': error_message,
            'last_update': datetime.now(pytz.timezone('Europe/Paris')).strftime('%H:%M:%S'),
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_cache(self, stop_code=None):
        """
        Efface le cache transport pour un arrêt spécifique ou global.
        
        Args:
            stop_code (str, optional): Code d'arrêt spécifique
        """
        if not self.cache:
            return
        
        try:
            if stop_code:
                # Effacer le cache pour un arrêt spécifique
                pattern = f"transport_cts_{stop_code}_*"
                if hasattr(self.cache, 'delete_many'):
                    self.cache.delete_many(pattern)
                else:
                    # Fallback - essayer les clés communes
                    for mode in ['undefined', 'bus', 'tram']:
                        cache_key = f"transport_cts_{stop_code}_{mode}_8"
                        self.cache.delete(cache_key)
                logger.info(f"Cache transport effacé pour l'arrêt {stop_code}")
            else:
                # Effacer tout le cache transport
                if hasattr(self.cache, 'delete_many'):
                    pattern = "transport_cts_*"
                    self.cache.delete_many(pattern)
                else:
                    logger.warning("Cache transport: effacement global non supporté")
                logger.info("Cache transport global effacé")
        except Exception as e:
            logger.error(f"Erreur lors de l'effacement du cache transport: {str(e)}")

# Instance du service créée via lazy loading dans __init__.py 