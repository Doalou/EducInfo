"""
Commandes CLI pour l'application EducInfo.
Ce module contient les commandes pour gérer l'application via le terminal.
"""
import click
from flask import current_app
from flask.cli import with_appcontext
from app.extensions import db
from app.models.user import User
from app.models.absence import Absence
from app.models.event import Event
from app.models.menu import MenuItem
from app.models.config import SiteConfig, WeatherConfig, WidgetConfig


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
            cts_stop_code="HOMME",
            cts_stop_display="Arrêt Homme de Fer"
        )
        db.session.add(widget_config)
        print('Configuration des widgets par défaut créée.')
    
    # Essayer de récupérer le token depuis current_app.config si pas écrasé par l'option
    try:
        env_cts_token = current_app.config.get('CTS_API_TOKEN')
    except RuntimeError:
        env_cts_token = None
    
    # Ordre de priorité: option CLI > variable d'env > valeur existante en BDD (si widget_config existait)
    final_cts_token = cts_token or env_cts_token or (widget_config.cts_api_token if widget_config else None)

    if final_cts_token:
        widget_config.cts_api_token = final_cts_token
        print(f'Token API CTS configuré pour WidgetConfig.')
    else:
        print('Attention: Aucun token API CTS n\'a été configuré. Le widget transport pourrait ne pas fonctionner.')
        print('Vous pouvez le définir via l\'option --cts-token, la variable d\'environnement CTS_API_TOKEN, ou le modifier plus tard via l\'interface d\'administration.')

    db.session.commit()
    print('Configurations initiales sauvegardées.')

    # Création de l'utilisateur administrateur initial s'il n'en existe aucun
    if not User.query.filter_by(is_admin=True).first():
        print("Aucun administrateur trouvé. Création du premier administrateur.")
        if not admin_username:
            admin_username = input("Nom d'utilisateur de l'administrateur: ")
        
        existing_user = User.query.filter_by(username=admin_username).first()
        if existing_user:
            # Si l'utilisateur existe mais n'est pas admin, on pourrait proposer de le promouvoir
            # Pour l'instant, on affiche une erreur et on arrête.
            if not existing_user.is_admin:
                print(f"L'utilisateur '{admin_username}' existe déjà mais n'est pas administrateur.")
                print("Veuillez choisir un autre nom d'utilisateur ou promouvoir cet utilisateur manuellement.")
            else:
                print(f"L'administrateur '{admin_username}' existe déjà.") # Cas où il existe et est déjà admin
            return # Arrêter si l'utilisateur existe déjà pour éviter confusion/erreur de mot de passe

        # Si l'utilisateur n'existe pas, on le crée
        if not admin_password:
            from getpass import getpass
            admin_password = getpass("Mot de passe de l'administrateur: ")
            password_confirm = getpass("Confirmez le mot de passe: ")
            if admin_password != password_confirm:
                print("Les mots de passe ne correspondent pas.")
                return
        
        admin_user = User(username=admin_username, is_admin=True)
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        db.session.commit()
        print(f"Administrateur '{admin_username}' créé avec succès.")
    else:
        print("Un compte administrateur existe déjà.")

    print('Base de données initialisée avec succès!')


@click.command('init-db')
@click.option('--cts-token', help="Token API pour le service de transport CTS.")
@click.option('--admin-username', help="Nom d'utilisateur pour le premier administrateur.")
@click.option('--admin-password', help="Mot de passe pour le premier administrateur (sera demandé si non fourni).")
@with_appcontext
def init_db_command(cts_token, admin_username, admin_password):
    """Initialise la base de données, crée les tables et les configurations initiales."""
    init_db(cts_token, admin_username, admin_password)


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
    """Ajoute des données de démonstration."""
    # Ajout d'absences
    absences = [
        Absence(professeur="Dupont", lundi=True, mardi=False, mercredi=True, jeudi=False, vendredi=False, samedi=False),
        Absence(professeur="Martin", lundi=False, mardi=True, mercredi=False, jeudi=True, vendredi=False, samedi=False),
        Absence(professeur="Durand", lundi=False, mardi=False, mercredi=False, jeudi=False, vendredi=True, samedi=True)
    ]
    for absence in absences:
        if not Absence.query.filter_by(professeur=absence.professeur).first():
            db.session.add(absence)
    
    # Ajout d'événements
    events = [
        Event(title="Journée portes ouvertes", date="25/06/2024", description="Visite de l'établissement"),
        Event(title="Conseil de classe", date="15/06/2024", description="Pour les classes de terminale"),
        Event(title="Sortie scolaire", date="10/06/2024", description="Musée des sciences")
    ]
    for event in events:
        if not Event.query.filter_by(title=event.title, date=event.date).first():
            db.session.add(event)
    
    # Ajout d'éléments de menu
    menu_items = [
        MenuItem(category=1, name="Salade verte", icons="🌱"),
        MenuItem(category=2, name="Steak haché", icons=""),
        MenuItem(category=2, name="Poisson pané", icons="🐟"),
        MenuItem(category=3, name="Fromage blanc", icons=""),
        MenuItem(category=4, name="Fruit de saison", icons="🌱")
    ]
    for item in menu_items:
        if not MenuItem.query.filter_by(name=item.name, category=item.category).first():
            db.session.add(item)
    
    db.session.commit()
    click.echo('Données de démonstration ajoutées avec succès!')


def register_commands(app):
    """Enregistre les commandes CLI."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(add_user_command)
    app.cli.add_command(add_demo_data_command) 