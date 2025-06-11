"""Script principal d'exécution optimisé pour EducInfo."""
import os
import sys
import argparse
from app import create_app, cli

# Application Flask
app = create_app()

# Enregistrement des commandes CLI
cli.register_commands(app)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lancer le serveur EducInfo')
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande serveur
    run_parser = subparsers.add_parser('run', help='Lancer le serveur web')
    run_parser.add_argument('--host', default='127.0.0.1', help='Adresse d\'écoute')
    run_parser.add_argument('--port', type=int, default=5000, help='Port d\'écoute')
    run_parser.add_argument('--debug', action='store_true', help='Mode debug')
    run_parser.add_argument('--production', action='store_true', help='Mode production (prioritaire)')
    
    # Commande init-db
    init_db_parser = subparsers.add_parser('init-db', help='Initialiser la base de données')
    init_db_parser.add_argument('--cts-token', help="Token API CTS")
    init_db_parser.add_argument('--admin-username', help="Nom d'utilisateur admin")
    init_db_parser.add_argument('--admin-password', help="Mot de passe admin")

    # Commande reset-db
    reset_db_parser = subparsers.add_parser('reset-db', help='Réinitialiser la base de données')
    reset_db_parser.add_argument('--force', action='store_true', help="Forcer sans confirmation")
    
    args = parser.parse_args()
    
    # Exécution des commandes
    if args.command == 'init-db':
        with app.app_context():
            from app.cli import init_db
            init_db(
                cts_token=getattr(args, 'cts_token', None),
                admin_username=getattr(args, 'admin_username', None),
                admin_password=getattr(args, 'admin_password', None)
            )
    elif args.command == 'reset-db':
        with app.app_context():
            from app.cli import reset_db
            if getattr(args, 'force', False) or input("Supprimer toutes les données ? (oui/non): ").lower() in ['oui', 'o', 'yes', 'y']:
                reset_db()
            else:
                print("Opération annulée.")
    else:  # Serveur par défaut
        debug_mode = getattr(args, 'debug', False)
        if getattr(args, 'production', False):
            debug_mode = False
            print("Application lancée en mode production")
        elif debug_mode:
            print("Application lancée en mode debug")
        else:
            print("Application lancée en mode standard")
        
        app.run(
            host=getattr(args, 'host', '127.0.0.1'),
            port=getattr(args, 'port', 5000),
            debug=debug_mode
        )