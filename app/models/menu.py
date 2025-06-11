"""
Modèle pour la gestion des menus de cantine optimisé.
"""
from datetime import date, datetime
from app.extensions import db


class MenuItem(db.Model):
    """
    Modèle représentant un élément de menu de cantine avec optimisations.
    Optimisé avec des index pour de meilleures performances de requête.
    """
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, nullable=False, index=True)  # Index pour filtrer par catégorie
    name = db.Column(db.String(100), nullable=False, index=True)  # Index pour recherche par nom
    description = db.Column(db.Text, default="")
    icons = db.Column(db.String(20), default="")
    date = db.Column(db.Date, nullable=False, index=True)  # Index critique pour filtrer par date
    order = db.Column(db.Integer, default=0, index=True)   # Index pour l'ordre d'affichage
    
    # Index composite optimisé pour les requêtes fréquentes
    __table_args__ = (
        db.Index('idx_date_category_order', 'date', 'category', 'order'),
        db.Index('idx_date_order', 'date', 'order'),
    )

    def __repr__(self):
        """Représentation de l'objet MenuItem"""
        return f'<MenuItem {self.category}: {self.name}>'

    @staticmethod
    def get_menu_categories():
        """
        Retourne les catégories disponibles avec leurs labels et icônes.
        
        Returns:
            list: Liste des catégories avec leurs labels et icônes
        """
        return [
            (1, 'Entrées', '🥗'),
            (2, 'Plats', '🍽️'),
            (3, 'Accompagnements', '🥔'),
            (4, 'Fromages', '🧀'),
            (5, 'Desserts', '🍰'),
        ]

    @staticmethod
    def get_icons():
        """
        Retourne les icônes disponibles pour les éléments de menu.
        
        Returns:
            list: Liste des icônes avec leurs descriptions
        """
        return [
            ('🌱', 'Végétarien'),
            ('🌾', 'Sans Gluten'),
            ('🥜', 'Contient des allergènes'),
            ('🥛', 'Produits laitiers'),
            ('🥩', 'Viande'),
            ('🐟', 'Poisson'),
            ('🌶️', 'Épicé'),
        ]

    @staticmethod
    def get_category_name(category_id):
        """Retourne le nom d'une catégorie par son ID."""
        categories = {cat[0]: cat[1] for cat in MenuItem.get_menu_categories()}
        return categories.get(category_id, 'Inconnu')

    @staticmethod
    def get_category_icon(category_id):
        """Retourne l'icône d'une catégorie par son ID."""
        categories = {cat[0]: cat[2] for cat in MenuItem.get_menu_categories()}
        return categories.get(category_id, '🍽️')

    @staticmethod
    def get_menus_for_date(target_date):
        """
        Retourne tous les éléments de menu pour une date donnée, 
        groupés par catégorie et triés par ordre.
        """
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        elif isinstance(target_date, datetime):
            target_date = target_date.date()
        
        return (MenuItem.query
                .filter(MenuItem.date == target_date)
                .order_by(MenuItem.category.asc(), MenuItem.order.asc(), MenuItem.id.asc())
                .all())

    @staticmethod
    def get_menus_grouped_by_category(target_date):
        """Retourne les menus groupés par catégorie pour une date donnée."""
        menu_items = MenuItem.get_menus_for_date(target_date)
        grouped = {}
        
        for item in menu_items:
            category = item.category
            if category not in grouped:
                grouped[category] = {
                    'name': MenuItem.get_category_name(category),
                    'icon': MenuItem.get_category_icon(category),
                    'items': []
                }
            grouped[category]['items'].append(item)
        
        return grouped

    @staticmethod
    def get_todays_menu():
        """
        Récupère le menu du jour.
        
        Returns:
            list: Liste des éléments du menu du jour
        """
        today = date.today()
        return MenuItem.query.filter_by(date=today).order_by(MenuItem.order, MenuItem.category).all() 