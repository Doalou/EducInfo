"""
Modèles pour la gestion des configurations de l'application.
"""
from datetime import date
from app.extensions import db
from flask import current_app


class WidgetConfig(db.Model):
    """
    Configuration des widgets affichés sur la page d'accueil.
    Singleton - une seule configuration par instance.
    """
    __tablename__ = 'widget_config'
    __table_args__ = (
        db.CheckConstraint('id = 1', name='unique_singleton'),
    )
    
    id = db.Column(db.Integer, primary_key=True, default=1)
    show_menu_cantine = db.Column(db.Boolean, default=False)
    show_transports = db.Column(db.Boolean, default=False)
    cts_stop_code = db.Column(db.String(20), default="")
    cts_vehicle_mode = db.Column(db.String(20), default="undefined")
    cts_api_token = db.Column(db.String(64), default="")
    cts_stop_display = db.Column(db.String(50), default="")

    def __repr__(self):
        """Représentation de l'objet WidgetConfig"""
        return f'<WidgetConfig Menu={self.show_menu_cantine} Transport={self.show_transports}>'

    @classmethod
    def get_config(cls):
        """
        Récupère la configuration des widgets (singleton).
        Garantit une seule instance avec ID=1.
        
        Returns:
            WidgetConfig: Instance unique de configuration des widgets
        """
        # Utilise get() au lieu de first() pour cibler spécifiquement ID=1
        config = cls.query.get(1)
        if not config:
            # Assure l'unicité en supprimant d'éventuels doublons
            cls.query.filter(cls.id != 1).delete()
            config = cls(id=1)
            db.session.add(config)
            db.session.commit()
        return config

    @staticmethod  
    def get_config_legacy():
        """
        Méthode statique obsolète - utiliser la méthode de classe get_config().
        Maintenue pour compatibilité ascendante.
        
        Returns:
            WidgetConfig: Instance de configuration des widgets
        """
        return WidgetConfig.get_config()

    def has_valid_transport_config(self, cts_api_token_from_config=None):
        """
        Vérifie si la configuration des transports est valide.
        
        Args:
            cts_api_token_from_config (str, optional): Jeton API CTS provenant de la configuration de l'application.
                                                    Passer None pour utiliser la valeur stockée dans l'instance.

        Returns:
            bool: True si la configuration est valide
        """
        # Utilise le token de config si fourni, sinon celui de l'instance, sinon celui de l'app (legacy, à retirer à terme)
        # L'idéal est que le token de l'app soit chargé dans l'instance au démarrage ou lors de la sauvegarde.
        # Pour l'instant, on garde la compatibilité mais on privilégie le token passé en argument.
        effective_api_token = cts_api_token_from_config if cts_api_token_from_config is not None else self.cts_api_token
        if not effective_api_token:
            try:
                from flask import has_app_context
                if has_app_context():
                    effective_api_token = current_app.config.get('CTS_API_TOKEN')
            except (RuntimeError, ImportError):
                # Contexte d'application non disponible ou erreur d'import
                pass

        return bool(
            self.show_transports and
            self.cts_stop_code and
            self.cts_stop_code.strip() and
            effective_api_token
        )
        
    def get_all_active_widgets(self, cts_api_token_from_config=None):
        """
        Retourne tous les widgets actifs.

        Args:
            cts_api_token_from_config (str, optional): Jeton API CTS provenant de la configuration de l'application.

        Returns:
            list: Liste des widgets actifs
        """
        active_widgets = []
        if self.show_menu_cantine:
            active_widgets.append('menu')
        if self.has_valid_transport_config(cts_api_token_from_config=cts_api_token_from_config):
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
        # db.session.commit() # Commit doit être géré par la vue/service


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
    api_key = db.Column(db.String(32), nullable=True, default='')
    city = db.Column(db.String(100), nullable=False, default='Paris')
    show_weather = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        """Représentation de l'objet WeatherConfig"""
        return f'<WeatherConfig City={self.city} Show={self.show_weather}>'

    @classmethod
    def get_config(cls):
        """
        Récupère la configuration météo ou en crée une par défaut si elle n'existe pas.
        
        Returns:
            WeatherConfig: Instance de configuration météo
        """
        config = cls.query.first()
        if not config:
            config = cls()
            db.session.add(config)
            db.session.commit()
        return config 