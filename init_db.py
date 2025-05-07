"""
Script pour initialiser la base de données et créer les tables nécessaires.
"""
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Ajout du répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# S'assurer que le répertoire instance existe
instance_path = os.path.join(os.path.dirname(__file__), "instance")
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# Vérifier si la base de données existe déjà
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance", "educinfo.db")
db_exists = os.path.exists(db_path)
if db_exists:
    # Supprimer l'ancienne base de données
    try:
        os.remove(db_path)
        print(f"Base de données existante supprimée: {db_path}")
    except Exception as e:
        print(f"Erreur lors de la suppression de la base de données: {e}")

# Création d'une application Flask minimale pour initialiser la DB
app = Flask(__name__)
# S'assurer d'utiliser un chemin absolu pour la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Création de l'instance db une seule fois
db = SQLAlchemy(app)


# On doit définir les modèles ici pour éviter les problèmes d'instances SQLAlchemy multiples
class User(db.Model):
    """Modèle utilisateur simplifié pour l'initialisation."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        """Défini le mot de passe en le hashant."""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)


class Absence(db.Model):
    """Modèle absence simplifié pour l'initialisation."""
    __tablename__ = 'absences'
    
    id = db.Column(db.Integer, primary_key=True)
    professeur = db.Column(db.String(100), nullable=False)
    lundi = db.Column(db.Boolean, default=False)
    mardi = db.Column(db.Boolean, default=False)
    mercredi = db.Column(db.Boolean, default=False)
    jeudi = db.Column(db.Boolean, default=False)
    vendredi = db.Column(db.Boolean, default=False)
    samedi = db.Column(db.Boolean, default=False)


class SiteConfig(db.Model):
    """Modèle configuration site simplifié pour l'initialisation."""
    __tablename__ = 'site_config'
    
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default='EducInfo')


class WeatherConfig(db.Model):
    """Modèle configuration météo simplifié pour l'initialisation."""
    __tablename__ = 'weather_config'
    
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(32), nullable=False, default='0b0b32c21c0e7a28f8dc6711e0c2e86b')
    city = db.Column(db.String(100), nullable=False, default='Paris')
    show_weather = db.Column(db.Boolean, default=True)


class WidgetConfig(db.Model):
    """Modèle configuration widgets simplifié pour l'initialisation."""
    __tablename__ = 'widget_config'
    
    id = db.Column(db.Integer, primary_key=True)
    show_menu_cantine = db.Column(db.Boolean, default=False)
    show_transports = db.Column(db.Boolean, default=False)
    cts_stop_code = db.Column(db.String(20), default="")
    cts_vehicle_mode = db.Column(db.String(20), default="undefined")
    cts_api_token = db.Column(db.String(64), default="")
    cts_stop_display = db.Column(db.String(50), default="")


class Event(db.Model):
    """Modèle événement simplifié pour l'initialisation."""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # Format: "JJ/MM/AAAA"
    description = db.Column(db.Text, default="")


class MenuItem(db.Model):
    """Modèle élément de menu simplifié pour l'initialisation."""
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="")
    icons = db.Column(db.String(20), default="")
    date = db.Column(db.String(10), default="")  # Format: "JJ/MM/AAAA"
    order = db.Column(db.Integer, default=0)


def init_db():
    """Initialise la base de données et crée les tables nécessaires."""
    with app.app_context():
        # Création des tables
        db.create_all()
        
        print("Tables créées avec succès!")
        
        # Vérifier si les configurations existent, sinon les créer
        if not SiteConfig.query.first():
            site_config = SiteConfig()
            site_config.site_name = "EducInfo"
            db.session.add(site_config)
            print("Configuration du site créée.")
        
        if not WeatherConfig.query.first():
            weather_config = WeatherConfig()
            weather_config.city = "Strasbourg"
            weather_config.api_key = "demo_key"
            weather_config.show_weather = True
            db.session.add(weather_config)
            print("Configuration météo créée.")
        
        if not WidgetConfig.query.first():
            widget_config = WidgetConfig()
            widget_config.show_menu_cantine = True
            widget_config.show_transports = True
            widget_config.cts_stop_code = "HOMME"
            widget_config.cts_stop_display = "Arrêt Homme de Fer"
            db.session.add(widget_config)
            print("Configuration des widgets créée.")
        
        # Créer un utilisateur admin si aucun n'existe
        if not User.query.filter_by(is_admin=True).first():
            user = User()
            user.email = "admin@educinfo.fr"
            user.is_admin = True
            user.set_password("admin123")
            db.session.add(user)
            print("Utilisateur admin créé: admin@educinfo.fr / admin123")
        
        # Ajouter quelques données de démonstration pour les absences
        if not Absence.query.first():
            absence1 = Absence()
            absence1.professeur = "Dupont"
            absence1.lundi = True
            absence1.mercredi = True
            
            absence2 = Absence()
            absence2.professeur = "Martin"
            absence2.mardi = True
            absence2.jeudi = True
            
            db.session.add(absence1)
            db.session.add(absence2)
            print("Données de démonstration pour les absences créées.")
            
        # Ajouter quelques événements de démonstration
        if not Event.query.first():
            event1 = Event()
            event1.title = "Journée portes ouvertes"
            event1.date = "25/06/2024"
            event1.description = "Visite de l'établissement"
            
            event2 = Event()
            event2.title = "Conseil de classe"
            event2.date = "15/06/2024"
            event2.description = "Pour les classes de terminale"
            
            db.session.add(event1)
            db.session.add(event2)
            print("Données de démonstration pour les événements créées.")
            
        # Ajouter quelques éléments de menu de démonstration
        if not MenuItem.query.first():
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")  # Format pour SQLAlchemy

            menu1 = MenuItem()
            menu1.category = 1  # Entrée
            menu1.name = "Salade verte"
            menu1.icons = "🌱"
            menu1.date = today
            menu1.order = 1
            
            menu2 = MenuItem()
            menu2.category = 2  # Plat principal
            menu2.name = "Steak haché"
            menu2.date = today
            menu2.order = 1
            
            menu3 = MenuItem()
            menu3.category = 4  # Dessert
            menu3.name = "Yaourt nature"
            menu3.date = today
            menu3.order = 1
            
            db.session.add(menu1)
            db.session.add(menu2)
            db.session.add(menu3)
            print("Données de démonstration pour le menu créées.")
        
        # Commit des changements
        db.session.commit()
        print("Base de données initialisée avec succès!")

if __name__ == "__main__":
    print(f"Initialisation de la base de données à : {db_path}")
    init_db() 