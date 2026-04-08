"""
Commandes CLI pour l'application EducInfo.
Ce module contient les commandes pour gérer l'application via le terminal.
"""
import os
import secrets
import click
from datetime import datetime, date
from flask import current_app
from flask.cli import with_appcontext
from app.extensions import db, logger, cache
from app.models.user import User
from app.models.absence import Absence
from app.models.event import Event
from app.models.menu import MenuItem
from app.models.config import SiteConfig, WeatherConfig, WidgetConfig
from app.services import get_weather_service

# Importer le groupe de commandes admin défini dans app.commands
from app.commands import admin_cli


def init_db(cts_token=None, admin_username=None, admin_password=None):
    """Fonction d'initialisation de la base de données sans le décorateur Click."""
    db.create_all()
    print('Tables de la base de données créées.')

    # Configuration du site
    if not SiteConfig.query.first():
        site_config = SiteConfig(site_name="EducInfo")
        db.session.add(site_config)
        print('Configuration du site par défaut créée.')

    # Configuration météo
    if not WeatherConfig.query.first():
        weather_config = WeatherConfig(city="Strasbourg", api_key="demo_key", show_weather=True)
        db.session.add(weather_config)
        print('Configuration météo par défaut créée.')

    # Configuration des widgets (avec le token CTS)
    widget_config = WidgetConfig.query.first()
    if not widget_config:
        widget_config = WidgetConfig(
            show_menu_cantine=True,
            show_transports=True,
            cts_stop_code="366",
            cts_stop_display="Arrêt Lycée Couffignal"
        )
        db.session.add(widget_config)
        print('Configuration des widgets par défaut créée.')
    
    # Essayer de récupérer le token depuis current_app.config si pas écrasé par l'option
    try:
        env_cts_token = current_app.config.get('CTS_API_TOKEN')
    except RuntimeError:
        env_cts_token = None
    
    # Utiliser le token fourni, ou celui de l'environnement, sinon laisser vide
    if cts_token or env_cts_token:
        if widget_config and cts_token:  # Si le token est fourni comme paramètre
            widget_config.cts_api_token = cts_token
            print(f'Token CTS configuré depuis option CLI.')
        elif widget_config and env_cts_token:  # Sinon utiliser celui de l'environnement
            widget_config.cts_api_token = env_cts_token
            print(f'Token CTS configuré depuis variable d\'environnement.')
    
    # Créer un utilisateur admin s'il n'existe pas
    admin_exists = User.query.filter_by(is_admin=True).first() is not None
    
    if not admin_exists:
        # Utiliser les paramètres ou demander interactivement
        username = admin_username or "admin"
        password = admin_password
        
        if not password and click:  # Si dans un contexte CLI
            generated = secrets.token_urlsafe(12)
            password = click.prompt('Mot de passe administrateur', hide_input=True,
                                   confirmation_prompt=True, default=generated)
            if password == generated:
                print(f'⚠️  Mot de passe admin généré automatiquement : {generated}')
                print('   Conservez-le précieusement ou changez-le dans le dashboard admin.')
        elif not password:  # Fallback
            password = secrets.token_urlsafe(12)
            print(f'⚠️  Mot de passe admin généré automatiquement : {password}')
            print('   Conservez-le précieusement ou changez-le dans le dashboard admin.')
        
        admin = User(username=username, is_admin=True)
        admin.set_password(password)
        db.session.add(admin)
        print(f'Utilisateur administrateur créé: {username}')
    
    # Commit des changements
    db.session.commit()


@click.command('init-db')
@click.option('--cts-token', help="Token API pour le service de transport CTS.")
@click.option('--admin-username', help="Nom d'utilisateur pour le premier administrateur.")
@click.option('--admin-password', help="Mot de passe pour le premier administrateur (sera demandé si non fourni).")
@with_appcontext
def init_db_command(cts_token, admin_username, admin_password):
    """Initialise la base de données, crée les tables et les configurations initiales."""
    init_db(cts_token, admin_username, admin_password)


def reset_db():
    """Supprime et recrée la base de données avec les données initiales."""
    # Obtenir le chemin de la base de données
    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        # Extraire le chemin de fichier
        db_path = db_uri.replace('sqlite:///', '')
        
        if os.path.exists(db_path):
            try:
                # Supprimer la base de données existante
                os.remove(db_path)
                print(f"Base de données existante supprimée: {db_path}")
            except Exception as e:
                print(f"Erreur lors de la suppression de la base de données: {e}")
    
    # Recréer les tables et initialiser les données
    db.create_all()
    print("Tables créées avec succès!")
    
    # Configurer le site
    site_config = SiteConfig()
    site_config.site_name = "EducInfo"
    db.session.add(site_config)
    
    # Configurer la météo
    weather_config = WeatherConfig()
    weather_config.city = "Strasbourg"
    weather_config.api_key = "demo_key"
    weather_config.show_weather = True
    db.session.add(weather_config)
    
    # Configurer les widgets
    widget_config = WidgetConfig()
    widget_config.show_menu_cantine = True
    widget_config.show_transports = True
    widget_config.cts_stop_code = "HOMME"
    widget_config.cts_stop_display = "Arrêt Homme de Fer"
    db.session.add(widget_config)
    
    # Créer un utilisateur admin avec mot de passe aléatoire
    generated_password = secrets.token_urlsafe(12)
    user = User()
    user.username = "admin"
    user.is_admin = True
    user.set_password(generated_password)
    db.session.add(user)
    print(f"Utilisateur admin créé: admin / {generated_password}")
    print("⚠️  Conservez ce mot de passe ou changez-le dans le dashboard admin.")
    
    # Ajouter des données de démonstration pour les absences
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
    
    # Ajouter des événements de démonstration
    # Convertir les chaînes de date en objets date Python
    event1 = Event()
    event1.title = "Journée portes ouvertes"
    # Convertir "25/06/2024" en objet date
    day1, month1, year1 = map(int, "25/06/2024".split('/'))
    event1.date = date(year1, month1, day1)
    event1.description = "Visite de l'établissement"
    
    event2 = Event()
    event2.title = "Conseil de classe"
    # Convertir "15/06/2024" en objet date
    day2, month2, year2 = map(int, "15/06/2024".split('/'))
    event2.date = date(year2, month2, day2)
    event2.description = "Pour les classes de terminale"
    
    db.session.add(event1)
    db.session.add(event2)
    
    # Ajouter des éléments de menu de démonstration
    today = datetime.now().date()
    
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
    
    # Commit des changements
    db.session.commit()
    print("Base de données réinitialisée avec succès!")


@click.command('reset-db')
@click.confirmation_option(prompt="Cette opération va supprimer toutes les données existantes. Êtes-vous sûr ?")
@with_appcontext
def reset_db_command():
    """Réinitialise complètement la base de données avec des données par défaut."""
    reset_db()


@click.command('add-user')
@click.option('--username', prompt=True, help='Le nom d\'utilisateur.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Le mot de passe.')
@click.option('--admin', is_flag=True, help='Définit l\'utilisateur comme administrateur.')
@with_appcontext
def add_user_command(username, password, admin):
    """Crée un nouvel utilisateur."""
    if User.query.filter_by(username=username).first():
        click.echo(f"Le nom d'utilisateur {username} existe déjà.")
        return
    
    user = User(username=username, is_admin=admin)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    role = "Administrateur" if admin else "Utilisateur"
    click.echo(f"{role} {username} créé avec succès!")


@click.command('create-admin')
@click.option('--username', prompt=True, help='Le nom d\'utilisateur pour l\'administrateur.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Le mot de passe.')
@with_appcontext
def create_admin_command(username, password):
    """Crée un utilisateur administrateur. [OBSOLÈTE: utiliser add-user --admin]"""
    click.echo("Attention: Cette commande est obsolète. Veuillez utiliser 'flask add-user --admin' à la place.")
    if User.query.filter_by(username=username).first():
        click.echo(f"Le nom d'utilisateur {username} existe déjà.")
        return
    
    user = User(username=username, is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    click.echo(f"Administrateur {username} créé avec succès!")


@click.command('add-demo-data')
@with_appcontext
def add_demo_data_command():
    """Ajoute des données de démonstration à la base de données."""
    # Ajout des événements de démonstration
    if not Event.query.first():
        # Convertir les chaînes de date en objets date Python
        day1, month1, year1 = map(int, "25/06/2024".split('/'))
        event_date1 = date(year1, month1, day1)
        
        day2, month2, year2 = map(int, "15/06/2024".split('/'))
        event_date2 = date(year2, month2, day2)
        
        event1 = Event(
            title="Journée portes ouvertes",
            date=event_date1,
            description="Visite de l'établissement"
        )
        event2 = Event(
            title="Conseil de classe",
            date=event_date2,
            description="Pour les classes de terminale"
        )
        db.session.add(event1)
        db.session.add(event2)
        click.echo("Événements de démonstration ajoutés.")
    
    # Ajout des absences de démonstration
    if not Absence.query.first():
        absence1 = Absence(professeur="Dupont", lundi=True, mercredi=True)
        absence2 = Absence(professeur="Martin", mardi=True, jeudi=True)
        db.session.add(absence1)
        db.session.add(absence2)
        click.echo("Absences de démonstration ajoutées.")
    
    # Ajout des items de menu de démonstration
    if not MenuItem.query.first():
        today = datetime.now().date()
        menu1 = MenuItem(category=1, name="Salade verte", icons="🌱", date=today, order=1)
        menu2 = MenuItem(category=2, name="Steak haché", date=today, order=1)
        menu3 = MenuItem(category=4, name="Yaourt nature", date=today, order=1)
        db.session.add(menu1)
        db.session.add(menu2)
        db.session.add(menu3)
        click.echo("Items de menu de démonstration ajoutés.")
    
    db.session.commit()
    click.echo("Données de démonstration ajoutées avec succès!")


def register_commands(app):
    """Enregistre les commandes CLI."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(reset_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(add_user_command)
    app.cli.add_command(add_demo_data_command)
    app.cli.add_command(admin_cli) # Enregistrer le nouveau groupe de commandes 

    @app.cli.command()
    def init_db():
        """Initialise la base de données avec les tables et données de base."""
        with app.app_context():
            # Créer toutes les tables
            db.create_all()
            
            # Créer les configurations par défaut si elles n'existent pas
            if not WeatherConfig.query.first():
                weather_config = WeatherConfig()
                db.session.add(weather_config)
            
            if not WidgetConfig.query.first():
                widget_config = WidgetConfig()
                db.session.add(widget_config)
            
            db.session.commit()
            click.echo("Base de données initialisée avec succès!")
    
    @app.cli.command()
    @click.option('--username', prompt='Nom d\'utilisateur admin', help='Nom d\'utilisateur administrateur')
    @click.option('--password', prompt='Mot de passe', hide_input=True, help='Mot de passe administrateur')
    @click.option('--cts-token', help='Token API CTS (optionnel)')
    @click.option('--weather-key', help='Clé API OpenWeather (optionnel)')
    def init_admin(username, password, cts_token, weather_key):
        """Initialise un utilisateur administrateur."""
        with app.app_context():
            # Vérifier si un admin existe déjà
            existing_admin = User.query.filter_by(is_admin=True).first()
            if existing_admin:
                click.echo(f"Un administrateur existe déjà: {existing_admin.username}")
                if not click.confirm('Voulez-vous le remplacer?'):
                    return
                db.session.delete(existing_admin)
            
            # Créer le nouvel administrateur
            admin = User(username=username, is_admin=True)
            admin.set_password(password)
            db.session.add(admin)
            
            # Configurer les APIs si fournies
            if cts_token:
                widget_config = WidgetConfig.query.first() or WidgetConfig()
                widget_config.cts_api_token = cts_token
                db.session.add(widget_config)
            
            if weather_key:
                weather_config = WeatherConfig.query.first() or WeatherConfig()
                weather_config.api_key = weather_key
                db.session.add(weather_config)
            
            db.session.commit()
            click.echo(f"Administrateur '{username}' créé avec succès!")
    
    @app.cli.command()
    def reset_db():
        """Remet à zéro la base de données (ATTENTION: SUPPRIME TOUTES LES DONNÉES)."""
        if click.confirm('⚠️  ATTENTION: Cette action supprimera toutes les données. Continuer?'):
            with app.app_context():
                db.drop_all()
                db.create_all()
                click.echo("Base de données remise à zéro!")
    
    @app.cli.command()
    @click.option('--pattern', help='Pattern de clé de cache à supprimer')
    def clear_cache(pattern):
        """Vide le cache de l'application."""
        with app.app_context():
            if pattern:
                click.echo(f"Suppression des clés correspondant au pattern: {pattern}")
                # Pour Redis, nous pourrions utiliser des patterns, 
                # mais Flask-Caching ne le supporte pas nativement
                click.echo("Fonctionnalité de pattern non disponible avec ce backend de cache")
            else:
                cache.clear()
                click.echo("Cache vidé complètement!")
    
    @app.cli.command()
    @click.option('--city', help='Ville pour tester (optionnel)')
    @click.option('--api-key', help='Clé API pour tester (optionnel)')
    def test_weather(city, api_key):
        """Teste le service météo et affiche les informations de diagnostic."""
        with app.app_context():
            click.echo("🌤️  Test du service météo EducInfo")
            click.echo("=" * 50)
            
            # Récupérer la configuration
            weather_config = WeatherConfig.get_config()
            
            click.echo(f"Configuration météo:")
            click.echo(f"  - Affichage activé: {weather_config.show_weather}")
            click.echo(f"  - Ville configurée: {weather_config.city}")
            click.echo(f"  - Clé API configurée: {'Oui' if weather_config.api_key else 'Non'}")
            click.echo(f"  - Longueur clé API: {len(weather_config.api_key or '')}")
            
            # Variables d'environnement
            env_key = current_app.config.get('WEATHER_API_KEY')
            env_city = current_app.config.get('WEATHER_CITY')
            click.echo(f"\nVariables d'environnement:")
            click.echo(f"  - WEATHER_API_KEY: {'Oui' if env_key else 'Non'}")
            click.echo(f"  - WEATHER_CITY: {env_city}")
            click.echo(f"  - Longueur clé env: {len(env_key or '')}")
            
            # Test du service
            try:
                click.echo(f"\n🔄 Test du service météo...")
                
                # Utiliser les paramètres fournis ou ceux de la config
                test_city = city or weather_config.city or env_city
                test_key = api_key or weather_config.api_key or env_key
                
                click.echo(f"  - Ville testée: {test_city}")
                click.echo(f"  - Clé utilisée: {'***' + test_key[-4:] if test_key and len(test_key) > 4 else 'Aucune'}")
                
                weather_data = get_weather_service().get_weather_data(test_city, test_key)
                
                if weather_data:
                    if 'error' in weather_data:
                        click.echo(f"❌ Erreur: {weather_data['error']}")
                        if 'details' in weather_data:
                            click.echo(f"   Détails: {weather_data['details']}")
                    else:
                        click.echo(f"✅ Succès!")
                        click.echo(f"  - Température: {weather_data.get('temp')}°C")
                        click.echo(f"  - Description: {weather_data.get('description')}")
                        click.echo(f"  - Ville: {weather_data.get('city')}")
                        click.echo(f"  - Icône: {weather_data.get('icon')}")
                        click.echo(f"  - Humidité: {weather_data.get('humidity')}%")
                        click.echo(f"  - Ressenti: {weather_data.get('feels_like')}°C")
                else:
                    click.echo("❌ Aucune donnée retournée")
                    
            except Exception as e:
                click.echo(f"❌ Exception: {e}")
                logger.error(f"Erreur test météo CLI: {e}")
            
            click.echo(f"\n📝 Conseils:")
            if not weather_config.show_weather:
                click.echo("  - Activez l'affichage météo dans les paramètres admin")
            if not (weather_config.api_key or env_key):
                click.echo("  - Configurez une clé API OpenWeatherMap")
            if not (weather_config.city or env_city):
                click.echo("  - Configurez une ville")
            
            click.echo(f"\n🔗 URLs utiles:")
            click.echo(f"  - Configuration: /admin (dashboard)")
            click.echo(f"  - API météo: /get_weather")
            click.echo(f"  - Debug météo: /admin/debug/weather (authentification requise)")
    
    @app.cli.command()
    def show_config():
        """Affiche la configuration actuelle de l'application."""
        with app.app_context():
            click.echo("⚙️  Configuration EducInfo")
            click.echo("=" * 40)
            
            # Configuration de base
            click.echo(f"Mode: {current_app.config.get('ENV')}")
            click.echo(f"Debug: {current_app.config.get('DEBUG')}")
            click.echo(f"Version: {current_app.config.get('APP_VERSION')}")
            
            # Base de données
            db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'sqlite' in db_url:
                click.echo(f"Base de données: SQLite (locale)")
            else:
                click.echo(f"Base de données: {db_url[:20]}...")
            
            # Cache
            cache_type = current_app.config.get('CACHE_TYPE')
            click.echo(f"Cache: {cache_type}")
            
            # APIs
            click.echo(f"\nAPIs configurées:")
            click.echo(f"  - OpenWeather: {'✅' if current_app.config.get('WEATHER_API_KEY') else '❌'}")
            click.echo(f"  - CTS Transport: {'✅' if current_app.config.get('CTS_API_TOKEN') else '❌'}")
            
            # Utilisateurs
            with app.app_context():
                user_count = User.query.count()
                admin_count = User.query.filter_by(is_admin=True).count()
                click.echo(f"\nUtilisateurs:")
                click.echo(f"  - Total: {user_count}")
                click.echo(f"  - Administrateurs: {admin_count}") 