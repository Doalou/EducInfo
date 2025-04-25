from flask_login import UserMixin
from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from flask import current_app

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    identifiant = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

    @property
    def is_admin(self):
        return self.role == 'admin'

class Absence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professeur = db.Column(db.String(100), nullable=False)
    lundi = db.Column(db.Boolean, default=False)
    mardi = db.Column(db.Boolean, default=False)
    mercredi = db.Column(db.Boolean, default=False)
    jeudi = db.Column(db.Boolean, default=False)
    vendredi = db.Column(db.Boolean, default=False)
    samedi = db.Column(db.Boolean, default=False)

class WidgetConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_menu_cantine = db.Column(db.Boolean, default=False)
    show_transports = db.Column(db.Boolean, default=False)
    cts_stop_code = db.Column(db.String(20), default="")
    cts_vehicle_mode = db.Column(db.String(20), default="undefined")
    cts_api_token = db.Column(db.String(64), default="")
    cts_stop_display = db.Column(db.String(50), default="")

    @staticmethod
    def get_config():
        return WidgetConfig.query.first() or WidgetConfig()

    def has_valid_transport_config(self):
        """Vérifie si la configuration des transports est valide"""
        return bool(
            self.show_transports and
            self.cts_stop_code and
            self.cts_stop_code.strip() and
            (self.cts_api_token or current_app.config.get('CTS_API_TOKEN'))
        )
        
    def get_all_active_widgets(self):
        """Retourne tous les widgets actifs"""
        active_widgets = []
        if self.show_menu_cantine:
            active_widgets.append('menu')
        if self.has_valid_transport_config():
            active_widgets.append('transport')
        return active_widgets

    def save_widget_settings(self, settings):
        """Sauvegarde les paramètres des widgets en conservant les valeurs existantes"""
        for key, value in settings.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()

class ThemeConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primary_color = db.Column(db.String(20), default='indigo')
    
    @staticmethod
    def get_color_choices():
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
    __tablename__ = 'site_config'
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default='EducInfo')
    
    @classmethod
    def get_config(cls):
        config = cls.query.first()
        if not config:
            config = cls()
            db.session.add(config)
            db.session.commit()
        return config

class WeatherConfig(db.Model):
    __tablename__ = 'weather_config'
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(32), nullable=False, default='0b0b32c21c0e7a28f8dc6711e0c2e86b')
    city = db.Column(db.String(100), nullable=False, default='Paris')
    show_weather = db.Column(db.Boolean, default=True)
    
    @classmethod
    def get_config(cls):
        return cls.query.first() or cls()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, default="")

    def is_future(self):
        return self.date >= date.today()

    @staticmethod
    def get_upcoming_events(days=30):
        future_date = date.today() + timedelta(days=days)
        return Event.query.filter(
            Event.date >= date.today(),
            Event.date <= future_date
        ).order_by(Event.date).all()

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    icons = db.Column(db.String(50))
    date = db.Column(db.Date, nullable=False, default=date.today)
    order = db.Column(db.Integer, default=0)

    @staticmethod
    def get_menu_categories():
        return [
            ('entree', 'Entrées', '🥗'),
            ('plat', 'Plats', '🍽️'),
            ('accompagnement', 'Accompagnements', '🥔'),
            ('fromage', 'Fromages', '🧀'),
            ('dessert', 'Desserts', '🍰'),
        ]

    @staticmethod
    def get_icons():
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
        return MenuItem.query.filter_by(date=date.today()).order_by(MenuItem.category, MenuItem.order).all()