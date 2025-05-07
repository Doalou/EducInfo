"""
Modèles pour la gestion des configurations de l'application.
"""
from datetime import date
from app.extensions import db
from flask import current_app


class WidgetConfig(db.Model):
    """
    Configuration des widgets affichés sur la page d'accueil.
    """
    __tablename__ = 'widget_config'
    
    id = db.Column(db.Integer, primary_key=True)
    show_menu_cantine = db.Column(db.Boolean, default=False)
    show_transports = db.Column(db.Boolean, default=False)
    cts_stop_code = db.Column(db.String(20), default="")
    cts_vehicle_mode = db.Column(db.String(20), default="undefined")
    cts_api_token = db.Column(db.String(64), default="")
    cts_stop_display = db.Column(db.String(50), default="")

    def __repr__(self):
        """Représentation de l'objet WidgetConfig"""
        return f'<WidgetConfig Menu={self.show_menu_cantine} Transport={self.show_transports}>'

    @staticmethod
    def get_config():
        """
        Récupère la configuration des widgets ou en crée une par défaut.
        
        Returns:
            WidgetConfig: Instance de configuration des widgets
        """
        return WidgetConfig.query.first() or WidgetConfig()

    def has_valid_transport_config(self):
        """
        Vérifie si la configuration des transports est valide.
        
        Returns:
            bool: True si la configuration est valide
        """
        return bool(
            self.show_transports and
            self.cts_stop_code and
            self.cts_stop_code.strip() and
            (self.cts_api_token or current_app.config.get('CTS_API_TOKEN'))
        )
        
    def get_all_active_widgets(self):
        """
        Retourne tous les widgets actifs.
        
        Returns:
            list: Liste des widgets actifs
        """
        active_widgets = []
        if self.show_menu_cantine:
            active_widgets.append('menu')
        if self.has_valid_transport_config():
            active_widgets.append('transport')
        return active_widgets

    def save_widget_settings(self, settings):
        """
        Sauvegarde les paramètres des widgets en conservant les valeurs existantes.
        
        Args:
            settings (dict): Dictionnaire des paramètres à sauvegarder
        """
        for key, value in settings.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()


class ThemeConfig(db.Model):
    """
    Configuration du thème de l'application.
    """
    __tablename__ = 'theme_config'
    
    id = db.Column(db.Integer, primary_key=True)
    primary_color = db.Column(db.String(20), default='indigo')
    
    def __repr__(self):
        """Représentation de l'objet ThemeConfig"""
        return f'<ThemeConfig Color={self.primary_color}>'

    @staticmethod
    def get_color_choices():
        """
        Retourne les choix de couleurs disponibles.
        
        Returns:
            list: Liste des choix de couleurs
        """
        return [
            ('indigo', 'Violet'),
            ('blue', 'Bleu'),
            ('green', 'Vert'),
            ('red', 'Rouge'),
            ('purple', 'Pourpre'),
            ('pink', 'Rose'),
            ('yellow', 'Jaune'),
            ('orange', 'Orange')
        ]


class SiteConfig(db.Model):
    """
    Configuration générale du site.
    """
    __tablename__ = 'site_config'
    
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default='EducInfo')
    
    def __repr__(self):
        """Représentation de l'objet SiteConfig"""
        return f'<SiteConfig Name={self.site_name}>'

    @classmethod
    def get_config(cls):
        """
        Récupère la configuration du site ou en crée une par défaut.
        
        Returns:
            SiteConfig: Instance de configuration du site
        """
        config = cls.query.first()
        if not config:
            config = cls()
            db.session.add(config)
            db.session.commit()
        return config


class WeatherConfig(db.Model):
    """
    Configuration du widget météo.
    """
    __tablename__ = 'weather_config'
    
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(32), nullable=False, default='0b0b32c21c0e7a28f8dc6711e0c2e86b')
    city = db.Column(db.String(100), nullable=False, default='Paris')
    show_weather = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        """Représentation de l'objet WeatherConfig"""
        return f'<WeatherConfig City={self.city} Show={self.show_weather}>'

    @classmethod
    def get_config(cls):
        """
        Récupère la configuration météo ou en crée une par défaut.
        
        Returns:
            WeatherConfig: Instance de configuration météo
        """
        return cls.query.first() or cls() 