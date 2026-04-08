"""
Service de métriques pour environnement distribué/load balancé
Gère l'agrégation des métriques de plusieurs instances EducInfo
"""

import os
import time
import json
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app
from ..utils.cache import get_cached, set_cached
from ..models import User, Absence, Event, MenuItem

logger = logging.getLogger(__name__)

class MetricsAggregator:
    """
    Gestionnaire de métriques pour environnements load balancés
    
    En cas de load balancing, plusieurs instances EducInfo peuvent tourner.
    Ce service permet d'agréger les métriques de toutes les instances.
    """
    
    def __init__(self):
        self.instance_id = self._get_instance_id()
        self.cache_prefix = "metrics:instance"
        self.aggregate_cache_key = "metrics:aggregated"
        self.instance_ttl = 300  # 5 minutes de TTL pour les métriques d'instance
        
    def _get_instance_id(self) -> str:
        """Génère un ID unique pour cette instance"""
        # Utilise hostname + PID pour identifier l'instance
        hostname = os.getenv('HOSTNAME', os.uname().nodename)
        pid = os.getpid()
        return f"{hostname}-{pid}"
    
    def collect_instance_metrics(self) -> Dict[str, Any]:
        """Collecte les métriques de cette instance spécifique"""
        try:
            # === Métriques système de cette instance ===
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # === Métriques d'uptime ===
            start_time = getattr(current_app, '_start_time', time.time())
            uptime_seconds = time.time() - start_time
            
            # === Métriques applicatives (partagées entre instances) ===
            total_users = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            today = datetime.utcnow().date()
            
            # Absences du jour selon le jour de la semaine
            day_mapping = {0: 'lundi', 1: 'mardi', 2: 'mercredi', 3: 'jeudi', 4: 'vendredi', 5: 'samedi'}
            current_day = day_mapping.get(today.weekday())
            
            absences_today = 0
            if current_day:
                absences = Absence.query.all()
                for absence in absences:
                    if getattr(absence, current_day, False):
                        absences_today += 1
            
            menu_items_today = MenuItem.query.filter_by(date=today).count()
            
            # Événements à venir (30 jours)
            future_date = today + timedelta(days=30)
            upcoming_events = Event.query.filter(
                Event.date >= today,
                Event.date <= future_date
            ).count()
            
            instance_metrics = {
                'instance_id': self.instance_id,
                'timestamp': datetime.utcnow().isoformat(),
                'system': {
                    'cpu_usage': round(cpu_percent, 1),
                    'memory_usage': round(memory.percent, 1),
                    'disk_usage': round(disk.percent, 1),
                    'uptime_seconds': uptime_seconds
                },
                'application': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'absences_today': absences_today,
                    'menu_items_today': menu_items_today,
                    'upcoming_events': upcoming_events
                },
                'health': {
                    'status': 'healthy',
                    'response_time': None  # Sera calculé par le load balancer
                }
            }
            
            return instance_metrics
            
        except Exception as e:
            logger.error(f"Erreur collecte métriques instance {self.instance_id}: {e}")
            return {
                'instance_id': self.instance_id,
                'timestamp': datetime.utcnow().isoformat(),
                'system': {'cpu_usage': 0, 'memory_usage': 0, 'disk_usage': 0, 'uptime_seconds': 0},
                'application': {'total_users': 0, 'active_users': 0, 'absences_today': 0, 'menu_items_today': 0, 'upcoming_events': 0},
                'health': {'status': 'error', 'response_time': None}
            }
    
    def store_instance_metrics(self) -> bool:
        """Stocke les métriques de cette instance dans le cache partagé"""
        try:
            metrics = self.collect_instance_metrics()
            cache_key = f"{self.cache_prefix}:{self.instance_id}"
            
            # Essayer d'abord Redis directement, puis fallback sur le cache helper
            try:
                import redis
                import json
                from flask import current_app
                
                redis_url = current_app.config.get('REDIS_URL') or os.getenv('REDIS_URL')
                if redis_url:
                    r = redis.from_url(redis_url, decode_responses=True,
                                     password=current_app.config.get('REDIS_PASSWORD'))
                    
                    # Stocker directement dans Redis avec TTL
                    r.setex(cache_key, self.instance_ttl, json.dumps(metrics))
                    logger.debug(f"Métriques stockées dans Redis pour instance {self.instance_id}")
                    return True
                    
            except ImportError:
                logger.debug("Redis non disponible, utilisation du cache helper")
            except Exception as e:
                logger.warning(f"Erreur Redis, fallback vers cache helper: {e}")
            
            # Fallback vers le système de cache standard
            success = set_cached(cache_key, metrics, timeout=self.instance_ttl)
            
            if success:
                logger.debug(f"Métriques stockées via cache helper pour instance {self.instance_id}")
                return True
            else:
                logger.warning(f"Échec stockage métriques pour instance {self.instance_id}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur stockage métriques instance {self.instance_id}: {e}")
            return False
    
    def get_all_instances_metrics(self) -> List[Dict[str, Any]]:
        """Récupère les métriques de toutes les instances actives"""
        try:
            # Métriques de l'instance actuelle
            current_metrics = self.collect_instance_metrics()
            all_instances = [current_metrics]
            
            # Tentative de découverte d'autres instances via Redis
            try:
                # Utilisation directe de Redis si disponible
                import redis
                from flask import current_app
                
                redis_url = current_app.config.get('REDIS_URL') or os.getenv('REDIS_URL')
                if redis_url:
                    r = redis.from_url(redis_url, decode_responses=True, 
                                     password=current_app.config.get('REDIS_PASSWORD'))
                    
                    # Scanner toutes les clés d'instances
                    pattern = f"{self.cache_prefix}:*"
                    for key in r.scan_iter(match=pattern):
                        if key != f"{self.cache_prefix}:{self.instance_id}":
                            try:
                                instance_data = r.get(key)
                                if instance_data:
                                    import json
                                    instance_metrics = json.loads(instance_data)
                                    
                                    # Vérifier que l'instance n'est pas trop ancienne (TTL + buffer)
                                    from datetime import datetime, timedelta
                                    instance_time = datetime.fromisoformat(instance_metrics['timestamp'])
                                    max_age = timedelta(seconds=self.instance_ttl + 60)  # TTL + 1 minute buffer
                                    
                                    if datetime.utcnow() - instance_time <= max_age:
                                        # Reformater pour compatibilité avec la structure attendue
                                        formatted_instance = {
                                            'id': instance_metrics['instance_id'],
                                            'status': instance_metrics['health']['status'],
                                            'cpu': instance_metrics['system']['cpu_usage'],
                                            'memory': instance_metrics['system']['memory_usage'],
                                            'disk': instance_metrics['system']['disk_usage'],
                                            'uptime': instance_metrics['system']['uptime_seconds'],
                                            'timestamp': instance_metrics['timestamp'],
                                            'system': instance_metrics['system'],
                                            'application': instance_metrics['application'],
                                            'health': instance_metrics['health']
                                        }
                                        all_instances.append(formatted_instance)
                                        
                            except (json.JSONDecodeError, KeyError, ValueError) as e:
                                logger.warning(f"Données invalides pour instance {key}: {e}")
                                continue
                                
                    logger.debug(f"Découverte de {len(all_instances)} instances (incluant cette instance)")
                    
            except ImportError:
                logger.info("Redis non disponible, mode instance unique")
            except Exception as e:
                logger.warning(f"Erreur découverte instances Redis: {e}")
            
            return all_instances
            
        except Exception as e:
            logger.error(f"Erreur récupération métriques toutes instances: {e}")
            return []
    
    def aggregate_metrics(self) -> Dict[str, Any]:
        """Agrège les métriques de toutes les instances"""
        try:
            instances_metrics = self.get_all_instances_metrics()
            
            if not instances_metrics:
                logger.warning("Aucune métrique d'instance disponible")
                return self._get_fallback_metrics()
            
            # === Agrégation des métriques système ===
            system_metrics = []
            application_metrics = []
            healthy_instances = []
            
            for instance in instances_metrics:
                if instance.get('system'):
                    system_metrics.append(instance['system'])
                if instance.get('application'):
                    application_metrics.append(instance['application'])
                if instance.get('health', {}).get('status') == 'healthy':
                    healthy_instances.append(instance)
            
            # Moyennes des métriques système
            if system_metrics:
                avg_cpu = sum(m['cpu_usage'] for m in system_metrics) / len(system_metrics)
                avg_memory = sum(m['memory_usage'] for m in system_metrics) / len(system_metrics)
                avg_disk = sum(m['disk_usage'] for m in system_metrics) / len(system_metrics)
                max_uptime = max(m['uptime_seconds'] for m in system_metrics)
            else:
                avg_cpu = avg_memory = avg_disk = max_uptime = 0
            
            # Les métriques applicatives sont identiques sur toutes les instances (même DB)
            if application_metrics:
                app_metrics = application_metrics[0]  # Prendre la première (toutes identiques)
            else:
                app_metrics = {'total_users': 0, 'active_users': 0, 'absences_today': 0, 'menu_items_today': 0, 'upcoming_events': 0}
            
            # === Métriques de cluster ===
            cluster_metrics = {
                'cluster': {
                    'total_instances': len(instances_metrics),
                    'healthy_instances': len(healthy_instances),
                    'load_balanced': len(instances_metrics) > 1
                },
                'system_avg': {
                    'cpu_usage': round(avg_cpu, 1),
                    'memory_usage': round(avg_memory, 1),
                    'disk_usage': round(avg_disk, 1),
                    'cluster_uptime': max_uptime
                },
                'application': app_metrics,
                'instances': [
                    {
                        'id': inst['instance_id'],
                        'status': inst.get('health', {}).get('status', 'unknown'),
                        'cpu': inst.get('system', {}).get('cpu_usage', 0),
                        'memory': inst.get('system', {}).get('memory_usage', 0),
                        'uptime': inst.get('system', {}).get('uptime_seconds', 0)
                    }
                    for inst in instances_metrics
                ],
                'aggregated_at': datetime.utcnow().isoformat()
            }
            
            # Mettre en cache les métriques agrégées
            set_cached(self.aggregate_cache_key, cluster_metrics, timeout=60)
            
            return cluster_metrics
            
        except Exception as e:
            logger.error(f"Erreur agrégation métriques: {e}")
            return self._get_fallback_metrics()
    
    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """Métriques de fallback en cas d'erreur"""
        return {
            'cluster': {'total_instances': 1, 'healthy_instances': 1, 'load_balanced': False},
            'system_avg': {'cpu_usage': 0, 'memory_usage': 0, 'disk_usage': 0, 'cluster_uptime': 0},
            'application': {'total_users': 0, 'active_users': 0, 'absences_today': 0, 'menu_items_today': 0, 'upcoming_events': 0},
            'instances': [{'id': self.instance_id, 'status': 'error', 'cpu': 0, 'memory': 0, 'uptime': 0}],
            'aggregated_at': datetime.utcnow().isoformat()
        }
    
    def get_metrics_for_display(self) -> Dict[str, Any]:
        """
        Retourne les métriques formatées pour l'affichage du dashboard
        Compatible avec l'interface existante
        """
        try:
            # Vérifier si on est en mode cluster
            aggregated = self.aggregate_metrics()
            
            if aggregated['cluster']['load_balanced']:
                # Mode cluster : utiliser les métriques agrégées
                metrics = {
                    'uptime': self._format_uptime(aggregated['system_avg']['cluster_uptime']),
                    'uptime_days': int(aggregated['system_avg']['cluster_uptime'] // 86400),
                    'active_services': aggregated['cluster']['healthy_instances'],
                    'cache_efficiency': 95,  # TODO: Calculer vraiment en mode cluster
                    'cpu_usage': aggregated['system_avg']['cpu_usage'],
                    'memory_usage': aggregated['system_avg']['memory_usage'],
                    'disk_usage': aggregated['system_avg']['disk_usage'],
                    'response_time': None,  # Sera mesuré par le load balancer
                    'business': {
                        'absences_today': aggregated['application']['absences_today'],
                        'menu_items_today': aggregated['application']['menu_items_today'],
                        'upcoming_events': aggregated['application']['upcoming_events']
                    },
                    'cluster_info': {
                        'is_clustered': True,
                        'total_instances': aggregated['cluster']['total_instances'],
                        'healthy_instances': aggregated['cluster']['healthy_instances'],
                        'instances': aggregated['instances']
                    }
                }
            else:
                # Mode instance unique : utiliser les métriques locales
                instance_metrics = self.collect_instance_metrics()
                metrics = {
                    'uptime': self._format_uptime(instance_metrics['system']['uptime_seconds']),
                    'uptime_days': int(instance_metrics['system']['uptime_seconds'] // 86400),
                    'active_services': 1,
                    'cache_efficiency': 95,  # TODO: Calculer vraiment
                    'cpu_usage': instance_metrics['system']['cpu_usage'],
                    'memory_usage': instance_metrics['system']['memory_usage'],
                    'disk_usage': instance_metrics['system']['disk_usage'],
                    'response_time': None,
                    'business': {
                        'absences_today': instance_metrics['application']['absences_today'],
                        'menu_items_today': instance_metrics['application']['menu_items_today'],
                        'upcoming_events': instance_metrics['application']['upcoming_events']
                    },
                    'cluster_info': {
                        'is_clustered': False,
                        'total_instances': 1,
                        'healthy_instances': 1,
                        'instances': [{'id': self.instance_id, 'status': 'healthy'}]
                    }
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur get_metrics_for_display: {e}")
            # Fallback vers les métriques de base
            return {
                'uptime': '0h 0m',
                'uptime_days': 0,
                'active_services': 1,
                'cache_efficiency': 0,
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'response_time': None,
                'business': {'absences_today': 0, 'menu_items_today': 0, 'upcoming_events': 0},
                'cluster_info': {'is_clustered': False, 'total_instances': 1, 'healthy_instances': 0, 'instances': []}
            }
    
    def _format_uptime(self, uptime_seconds: float) -> str:
        """Formate l'uptime en chaîne lisible"""
        try:
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            if days > 0:
                return f"{days}j {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except Exception:
            return "0m"


# Instanciation globale du service
metrics_aggregator = MetricsAggregator()

def get_aggregated_metrics() -> Dict[str, Any]:
    """
    Point d'entrée principal pour récupérer les métriques
    Compatible avec l'interface existante mais optimisé pour le load balancing
    """
    return metrics_aggregator.get_metrics_for_display()

def store_current_instance_metrics() -> bool:
    """
    Stocke les métriques de l'instance actuelle
    À appeler périodiquement (ex: toutes les minutes)
    """
    return metrics_aggregator.store_instance_metrics() 