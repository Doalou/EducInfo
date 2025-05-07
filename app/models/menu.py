"""
Modèle pour la gestion des menus de cantine.
"""
from datetime import date, datetime
from app.extensions import db


class MenuItem(db.Model):
    """
    Modèle représentant un élément de menu de la cantine.
    """
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="")
    icons = db.Column(db.String(20), default="")
    date = db.Column(db.String(10), default="")
    order = db.Column(db.Integer, default=0)

    def __repr__(self):
        """Représentation de l'objet MenuItem"""
        return f'<MenuItem {self.category}: {self.name}>'

    @staticmethod
    def get_menu_categories():
        """
        Retourne les catégories disponibles pour les éléments de menu.
        
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
    def get_todays_menu():
        """
        Récupère le menu du jour.
        
        Returns:
            list: Liste des éléments du menu du jour
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return MenuItem.query.filter_by(date=today).order_by(MenuItem.order, MenuItem.category).all() 