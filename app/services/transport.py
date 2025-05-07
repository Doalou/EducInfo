"""
Service de transport pour l'application.
Ce module encapsule la logique d'interrogation de l'API CTS (Compagnie des Transports Strasbourgeois).
"""
import time
import requests
from flask import current_app
from app.extensions import logger
from app.models import WidgetConfig

class TransportService:
    """
    Service pour récupérer les données de transport via l'API CTS.
    Gère le cache et la récupération des horaires de passage.
    """
    # Constantes
    CACHE_DURATION = 60  # 1 minute en secondes (courts car données temps réel)
    REQUEST_TIMEOUT = 5  # Timeout en secondes
    DEFAULT_PREVIEW_INTERVAL = "PT2H"  # 2 heures par défaut
    DEFAULT_MAX_VISITS = 10  # Nombre maximum de passages par défaut
    
    def __init__(self):
        """Initialise le service de transport avec un cache vide."""
        self._cache = {}
        self._last_update = {}
    
    def get_stop_arrivals(self, stop_code=None, vehicle_mode=None, api_token=None, 
                          preview_interval=None, max_visits=None):
        """
        Récupère les passages à un arrêt CTS donné.
        Utilise le cache si les données sont encore fraîches.
        
        Args:
            stop_code (str): Code de l'arrêt CTS (ou None pour utiliser la config)
            vehicle_mode (str): Mode de transport (bus, tram, undefined)
            api_token (str): Token d'API CTS (ou None pour utiliser la config)
            preview_interval (str): Intervalle de prévision (format PT2H)
            max_visits (int): Nombre maximum de passages à récupérer
            
        Returns:
            dict: Données de passages ou dictionnaire d'erreur
        """
        # Récupérer la configuration
        widget_config = WidgetConfig.get_config()
        
        # Vérifier si le widget transport est activé
        if not widget_config.show_transports:
            logger.info("Service transport: Widget transport désactivé")
            return {"error": "Widget transport désactivé"}
        
        # Utiliser les paramètres de config si non fournis
        effective_stop_code = stop_code or widget_config.cts_stop_code
        effective_vehicle_mode = vehicle_mode or widget_config.cts_vehicle_mode or "undefined"
        effective_api_token = (
            api_token or 
            widget_config.cts_api_token or 
            current_app.config.get('CTS_API_TOKEN')
        )
        effective_preview_interval = preview_interval or self.DEFAULT_PREVIEW_INTERVAL
        effective_max_visits = max_visits or self.DEFAULT_MAX_VISITS
        
        # Vérifier que les paramètres nécessaires sont disponibles
        if not effective_stop_code or not effective_stop_code.strip():
            logger.error("Service transport: Code d'arrêt manquant")
            return {"error": "Code d'arrêt manquant"}
            
        if not effective_api_token:
            logger.error("Service transport: Token API CTS manquant")
            return {"error": "Token API CTS manquant"}
        
        # Vérifier le cache
        cache_key = f"{effective_stop_code}_{effective_vehicle_mode}_{effective_preview_interval}_{effective_max_visits}"
        current_time = time.time()
        
        if (cache_key in self._cache and 
            cache_key in self._last_update and 
            current_time - self._last_update[cache_key] < self.CACHE_DURATION):
            logger.debug(f"Service transport: Utilisation du cache pour l'arrêt {effective_stop_code}")
            return self._cache[cache_key]
        
        # Récupérer les données fraîches
        try:
            logger.info(f"Service transport: Récupération des données pour l'arrêt {effective_stop_code}")
            
            # Récupérer l'URL de base de l'API CTS
            base_url = current_app.config.get('CTS_BASE_URL')
            if not base_url:
                raise ValueError("URL de base de l'API CTS manquante dans la configuration")
            
            arrivals_data = self._fetch_arrivals_data(
                base_url=base_url,
                stop_code=effective_stop_code,
                vehicle_mode=effective_vehicle_mode,
                api_token=effective_api_token,
                preview_interval=effective_preview_interval,
                max_visits=effective_max_visits
            )
            
            # Mettre à jour le cache
            self._cache[cache_key] = arrivals_data
            self._last_update[cache_key] = current_time
            
            return arrivals_data
        except Exception as e:
            logger.error(f"Service transport: Erreur lors de la récupération des données - {str(e)}")
            # En cas d'erreur, retourner le cache même s'il est périmé
            if cache_key in self._cache:
                logger.warning(f"Service transport: Utilisation du cache périmé pour l'arrêt {effective_stop_code}")
                return self._cache[cache_key]
            return {"error": f"Erreur transport: {str(e)}"}
    
    def _fetch_arrivals_data(self, base_url, stop_code, vehicle_mode, api_token, 
                            preview_interval, max_visits):
        """
        Interroge l'API CTS pour récupérer les données de passages.
        
        Args:
            base_url (str): URL de base de l'API CTS
            stop_code (str): Code de l'arrêt CTS
            vehicle_mode (str): Mode de transport (bus, tram, undefined)
            api_token (str): Token d'API CTS
            preview_interval (str): Intervalle de prévision
            max_visits (int): Nombre maximum de passages à récupérer
            
        Returns:
            dict: Données de passages formatées
            
        Raises:
            Exception: En cas d'erreur lors de la requête ou du traitement des données
        """
        try:
            endpoint = f"{base_url}/v1/siri/2.0/stop-monitoring"
            params = {
                "MonitoringRef": stop_code,
                "VehicleMode": vehicle_mode,
                "PreviewInterval": preview_interval,
                "MaximumStopVisits": max_visits
            }
            
            logger.debug(f"Service transport: Requête API - {endpoint} avec params {params}")
            
            response = requests.get(
                endpoint, 
                params=params,
                auth=(api_token, ""),
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Accès sécurisé aux données
            delivery = data.get("ServiceDelivery", {}).get("StopMonitoringDelivery", [{}])[0]
            visits = delivery.get("MonitoredStopVisit", [])
            
            # Formater les données pour qu'elles soient plus faciles à utiliser
            formatted_arrivals = self._format_arrivals(visits, stop_code)
            
            logger.info(f"Service transport: {len(formatted_arrivals)} passages trouvés pour l'arrêt {stop_code}")
            
            return {
                "status": "success",
                "stop_code": stop_code,
                "arrivals": formatted_arrivals,
                "count": len(formatted_arrivals),
                "timestamp": int(time.time())
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Service transport: Erreur de requête - {str(e)}")
            raise Exception(f"Erreur de communication avec l'API CTS: {str(e)}")
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Service transport: Erreur de traitement des données - {str(e)}")
            raise Exception(f"Erreur de traitement des données CTS: {str(e)}")
        except Exception as e:
            logger.error(f"Service transport: Erreur inattendue - {str(e)}")
            raise Exception(f"Erreur inattendue du service transport: {str(e)}")
    
    def _format_arrivals(self, visits, stop_code):
        """
        Formate les données de passage pour qu'elles soient plus faciles à utiliser.
        
        Args:
            visits (list): Liste des passages bruts de l'API
            stop_code (str): Code de l'arrêt CTS
            
        Returns:
            list: Liste formatée des passages
        """
        formatted_arrivals = []
        
        for visit in visits:
            try:
                # Accès sécurisé aux données
                journey = visit.get("MonitoredVehicleJourney", {})
                line_ref = journey.get("LineRef", "")
                line_name = journey.get("PublishedLineName", "")
                destination = journey.get("DestinationName", "")
                vehicle_mode = journey.get("VehicleMode", "")  # Mode de véhicule depuis l'API
                
                # Gestion des temps d'arrivée
                call = journey.get("MonitoredCall", {})
                expected_arrival = call.get("ExpectedArrivalTime", "")
                aimed_arrival = call.get("AimedArrivalTime", "")
                
                # Temps restant avant l'arrivée (en minutes)
                expected_time_left = self._calculate_time_left(expected_arrival)
                aimed_time_left = self._calculate_time_left(aimed_arrival)
                
                # Déterminer si c'est un tram selon différentes heuristiques
                is_tram = (
                    vehicle_mode == "tram" or  # Si l'API fournit directement l'info
                    (line_ref and "T" in line_ref) or  # Si la référence contient T
                    (line_name and line_name.startswith("T"))  # Si le nom commence par T
                )
                
                formatted_arrivals.append({
                    "line": line_name,
                    "line_ref": line_ref,
                    "destination": destination,
                    "expected_arrival": expected_arrival,
                    "aimed_arrival": aimed_arrival,
                    "expected_time_left": expected_time_left,
                    "aimed_time_left": aimed_time_left,
                    "is_realtime": expected_arrival != aimed_arrival,
                    "stop_code": stop_code,
                    "vehicle_mode": vehicle_mode,  # Mode de véhicule brut de l'API
                    "is_tram": is_tram,  # Indicateur simplifié
                    "mode": "tram" if is_tram else "bus"  # Valeur simplifiée pour l'affichage
                })
            except Exception as e:
                logger.warning(f"Service transport: Erreur lors du formatage d'un passage - {str(e)}")
                # On continue avec les autres passages
                continue
        
        # Trier par temps d'arrivée - gestion des valeurs None
        def sort_key(x):
            # Mettre les valeurs None à la fin
            if x["expected_time_left"] is None:
                return float('inf')
            return x["expected_time_left"]
            
        return sorted(formatted_arrivals, key=sort_key)
    
    def _calculate_time_left(self, arrival_time_str):
        """
        Calcule le temps restant en minutes à partir d'une chaîne de date ISO.
        
        Args:
            arrival_time_str (str): Chaîne de date ISO de l'API CTS
            
        Returns:
            int: Nombre de minutes avant l'arrivée, ou None si la date est invalide
        """
        if not arrival_time_str:
            return None
        
        try:
            from datetime import datetime
            import pytz
            
            # Format de l'API CTS: 2023-05-20T14:30:00.000+02:00
            # On retire le .000 et on parse
            arrival_time_str = arrival_time_str.replace(".000", "")
            arrival_time = datetime.fromisoformat(arrival_time_str)
            
            # Assurer que l'heure est en UTC
            if arrival_time.tzinfo is None:
                # Si pas de timezone, on suppose UTC
                arrival_time = pytz.utc.localize(arrival_time)
            
            # Heure actuelle en UTC
            now = datetime.now(pytz.utc)
            
            # Calculer la différence en minutes
            time_diff = arrival_time - now
            minutes = int(time_diff.total_seconds() / 60)
            
            return max(0, minutes)  # Ne pas retourner de temps négatif
        except Exception as e:
            logger.warning(f"Service transport: Erreur lors du calcul du temps restant - {str(e)}")
            return None

# Instance unique du service à utiliser dans l'application
transport_service = TransportService() 