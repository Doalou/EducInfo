"""
Service de menu pour l'application.
Ce module encapsule la logique de gestion des menus de cantine.
"""
from datetime import datetime, timedelta, date
from app.extensions import db, logger, cache
from app.models import MenuItem

class MenuService:
    """
    Service pour gérer les menus de cantine.
    Fournit des méthodes pour récupérer, formater et organiser les menus.
    """
    
    @staticmethod
    def get_todays_menu():
        """
        Récupère le menu du jour avec mise en cache optimisée.
        
        Returns:
            list: Liste des éléments du menu du jour triés par catégorie et ordre
        """
        from flask import current_app
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Système de cache pour le menu du jour
            cache_key = f"{current_app.config.get('CACHE_KEY_PREFIX', 'educinfo')}:menu:today:{today}"
            
            # Vérifier le cache
            cached_menu = cache.get(cache_key)
            if cached_menu is not None:
                logger.debug(f"Service menu: Cache hit pour le menu du {today}")
                return cached_menu
            
            # Requête optimisée avec tri dans la base de données
            menu_items = MenuItem.query.filter_by(date=today)\
                                     .order_by(MenuItem.category, MenuItem.order, MenuItem.name)\
                                     .all()
            
            # Mise en cache avec timeout configuré
            cache_timeout = current_app.config.get('CACHE_TIMEOUTS', {}).get('menu', 3600)
            cache.set(cache_key, menu_items, timeout=cache_timeout)
            
            logger.info(f"Service menu: Menu du {today} chargé et mis en cache ({len(menu_items)} éléments)")
            return menu_items
            
        except Exception as e:
            logger.error(f"Service menu: Erreur lors de la récupération du menu du jour - {str(e)}")
            return []
    
    @staticmethod
    def get_menu_by_date(target_date):
        """
        Récupère le menu pour une date spécifique.
        
        Args:
            target_date (str): Date au format YYYY-MM-DD pour laquelle récupérer le menu
            
        Returns:
            list: Liste des éléments du menu pour la date spécifiée
        """
        try:
            return MenuItem.query.filter_by(date=target_date).order_by(MenuItem.order, MenuItem.category).all()
        except Exception as e:
            logger.error(f"Service menu: Erreur lors de la récupération du menu pour {target_date} - {str(e)}")
            return []
    
    @staticmethod
    def get_menu_by_date_range(start_date, end_date):
        """
        Récupère les menus pour une période donnée.
        
        Args:
            start_date (str): Date de début au format YYYY-MM-DD
            end_date (str): Date de fin au format YYYY-MM-DD
            
        Returns:
            dict: Dictionnaire des menus par date
        """
        try:
            menu_items = MenuItem.query.filter(
                MenuItem.date >= start_date,
                MenuItem.date <= end_date
            ).order_by(MenuItem.date, MenuItem.order, MenuItem.category).all()
            
            # Organiser par date
            menus_by_date = {}
            for item in menu_items:
                date_str = item.date
                if date_str not in menus_by_date:
                    menus_by_date[date_str] = []
                menus_by_date[date_str].append(item)
            
            return menus_by_date
        except Exception as e:
            logger.error(f"Service menu: Erreur lors de la récupération des menus du {start_date} au {end_date} - {str(e)}")
            return {}
    
    @staticmethod
    def get_weekly_menu(week_offset=0):
        """
        Récupère le menu pour une semaine spécifique.
        
        Args:
            week_offset (int): Décalage de semaine (0=semaine courante, 1=semaine prochaine, etc.)
            
        Returns:
            dict: Dictionnaire des menus par jour de la semaine
        """
        try:
            # Déterminer le premier jour de la semaine (lundi)
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())
            
            # Appliquer le décalage de semaine
            start_of_week = start_of_week + timedelta(weeks=week_offset)
            
            # Fin de la semaine (dimanche)
            end_of_week = start_of_week + timedelta(days=6)
            
            # Récupérer les menus pour cette période
            menus_by_date = MenuService.get_menu_by_date_range(start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d"))
            
            # Transformer en dictionnaire par jour de la semaine
            weekdays = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
            menus_by_weekday = {}
            
            for i in range(7):
                day = start_of_week + timedelta(days=i)
                date_str = day.strftime('%Y-%m-%d')
                weekday = weekdays[i]
                
                menus_by_weekday[weekday] = {
                    'date': day,
                    'menu_items': menus_by_date.get(date_str, [])
                }
            
            return menus_by_weekday
        except Exception as e:
            logger.error(f"Service menu: Erreur lors de la récupération du menu hebdomadaire (offset={week_offset}) - {str(e)}")
            return {}
    
    @staticmethod
    def organize_menu_by_category(menu_items):
        """
        Organise les éléments de menu par catégorie.
        
        Args:
            menu_items (list): Liste d'objets MenuItem
            
        Returns:
            dict: Dictionnaire des éléments de menu organisés par catégorie
        """
        try:
            categories = {}
            for item in menu_items:
                if item.category not in categories:
                    categories[item.category] = []
                categories[item.category].append(item)
            return categories
        except Exception as e:
            logger.error(f"Service menu: Erreur lors de l'organisation du menu par catégorie - {str(e)}")
            return {}
    
    @staticmethod
    def get_category_info(category_id):
        """
        Récupère les informations d'une catégorie de menu.
        
        Args:
            category_id (int): ID de la catégorie
            
        Returns:
            dict: Dictionnaire contenant les informations de la catégorie (label et icon)
        """
        categories_map = {
            1: {'label': 'Entrée', 'icon': '🥗'},
            2: {'label': 'Plat principal', 'icon': '🍖'},
            3: {'label': 'Fromage', 'icon': '🧀'},
            4: {'label': 'Dessert', 'icon': '🍦'}
        }
        return categories_map.get(category_id, {'label': 'Catégorie', 'icon': '🍴'})
    
    @staticmethod
    def add_menu_item(category, name, description=None, icons=None, menu_date=None, order=0):
        """
        Ajoute un élément au menu.
        
        Args:
            category (int): Catégorie du plat (1=Entrée, 2=Plat, etc.)
            name (str): Nom du plat
            description (str): Description du plat
            icons (str): Icônes associées au plat
            menu_date (str|date): Date du menu au format YYYY-MM-DD ou objet date (aujourd'hui par défaut)
            order (int): Ordre d'affichage
            
        Returns:
            MenuItem: L'élément de menu créé, ou None en cas d'erreur
        """
        try:
            # Gestion de la date - accepter les objets date et les chaînes
            if menu_date is None:
                date_value = datetime.now().date()
            elif isinstance(menu_date, str):
                # Si c'est une chaîne, la convertir en objet date
                date_value = datetime.strptime(menu_date, "%Y-%m-%d").date()
            elif hasattr(menu_date, 'date'):
                # Si c'est un datetime, prendre la partie date
                date_value = menu_date.date()
            else:
                # Si c'est déjà un objet date
                date_value = menu_date
                
            menu_item = MenuItem(
                category=category,
                name=name,
                description=description or "",
                icons=icons or "",
                date=date_value,
                order=order
            )
            
            db.session.add(menu_item)
            db.session.commit()
            
            logger.info(f"Service menu: Nouvel élément ajouté - {category}: {name} pour le {date_value}")
            return menu_item
        except Exception as e:
            db.session.rollback()
            logger.error(f"Service menu: Erreur lors de l'ajout d'un élément au menu - {str(e)}")
            return None
    
    @staticmethod
    def update_menu_item(item_id, **kwargs):
        """
        Met à jour un élément de menu existant.
        
        Args:
            item_id (int): ID de l'élément à mettre à jour
            **kwargs: Attributs à mettre à jour (category, name, description, icons, date, order)
            
        Returns:
            MenuItem: L'élément de menu mis à jour, ou None en cas d'erreur
        """
        try:
            menu_item = MenuItem.query.get(item_id)
            if not menu_item:
                logger.warning(f"Service menu: Élément de menu {item_id} non trouvé pour mise à jour")
                return None
            
            # Mettre à jour les attributs
            for key, value in kwargs.items():
                if hasattr(menu_item, key):
                    setattr(menu_item, key, value)
            
            db.session.commit()
            logger.info(f"Service menu: Élément {item_id} mis à jour")
            return menu_item
        except Exception as e:
            db.session.rollback()
            logger.error(f"Service menu: Erreur lors de la mise à jour de l'élément {item_id} - {str(e)}")
            return None
    
    @staticmethod
    def delete_menu_item(item_id):
        """
        Supprime un élément de menu.
        
        Args:
            item_id (int): ID de l'élément à supprimer
            
        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        try:
            menu_item = MenuItem.query.get(item_id)
            if not menu_item:
                logger.warning(f"Service menu: Élément de menu {item_id} non trouvé pour suppression")
                return False
            
            db.session.delete(menu_item)
            db.session.commit()
            logger.info(f"Service menu: Élément {item_id} supprimé")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Service menu: Erreur lors de la suppression de l'élément {item_id} - {str(e)}")
            return False

# Instance du service créée via lazy loading dans __init__.py 