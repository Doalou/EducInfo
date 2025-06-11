import click
import secrets
from flask import current_app
from flask.cli import AppGroup

# Créer un groupe de commandes pour une meilleure organisation
# Cela permettra d'appeler la commande via: flask admin generate-emergency-code
admin_cli = AppGroup('admin', help='Commandes d\'administration personnalisées.')

@admin_cli.command('generate-emergency-code')
@click.option('--length', default=16, help='Longueur du token en octets (résultera en une chaîne hexadécimale 2x plus longue).', type=int)
def generate_emergency_code_command(length):
    """Génère un nouveau code d\'urgence à usage unique."""
    if length <= 0:
        click.echo(click.style("Erreur: La longueur doit être un entier positif.", fg='red'))
        return

    new_code = secrets.token_hex(length)
    
    # Stockage temporaire du code.
    # ATTENTION: Pour la production avec plusieurs workers, ce n'est pas une solution robuste.
    # Un cache partagé (Redis, Memcached) ou une table en BDD avec expiration serait préférable.
    current_app.config['GENERATED_EMERGENCY_CODE'] = new_code
    current_app.logger.info(f"DEBUG: Emergency code SET in config by CLI: {current_app.config.get('GENERATED_EMERGENCY_CODE')}")
    # Optionnel: stocker un timestamp pour gérer l\'expiration du code.
    # current_app.config['GENERATED_EMERGENCY_CODE_TS'] = datetime.utcnow()

    log_message = f"Nouveau code d\'urgence généré: {new_code}"
    
    # Assurer que le logger est disponible
    if hasattr(current_app, 'logger'):
        current_app.logger.info(f"CODE D\'URGENCE GÉNÉRÉ: {new_code}")
    else:
        click.echo(f"Log (INFO): {log_message}") # Fallback si logger non configuré tôt

    click.echo(click.style("IMPORTANT: Le code suivant est à usage unique et sensible.", fg='yellow', bold=True))
    click.echo(f"Code d\'urgence: {click.style(new_code, fg='green', bold=True)}")
    click.echo("Ce code a été stocké temporairement et enregistré dans les logs de l\'application (niveau INFO).")
    click.echo(click.style("Utilisez ce code rapidement. Il sera invalidé après la première utilisation réussie.", fg='yellow'))

def init_app(app):
    """Enregistre les commandes CLI avec l\'application Flask."""
    app.cli.add_command(admin_cli)
    # Vous pouvez ajouter d\'autres initialisations de commandes ici si nécessaire 