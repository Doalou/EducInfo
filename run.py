"""
Script principal d'exécution pour l'application EducInfo.

Ce script peut être utilisé de deux façons:
1. Via la commande Flask CLI: `flask run` (méthode recommandée pour le développement)
   Dans ce cas, définir FLASK_APP=run:app dans l'environnement ou dans .env/.flaskenv

2. Directement avec Python: `python run.py [options]`
   Utile pour le déploiement rapide ou les tests

Pour l'utilisation des commandes CLI (comme init-db, add-user, etc.),
utilisez la syntaxe: `flask <commande>` après avoir défini FLASK_APP=run:app
"""
import os
import sys
import argparse
from app import create_app, cli

# Création de l'application Flask
app = create_app()

# Enregistrement des commandes CLI
cli.register_commands(app)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lancer le serveur EducInfo')
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande pour le serveur (comportement par défaut)
    run_parser = subparsers.add_parser('run', help='Lancer le serveur web')
    run_parser.add_argument('--host', default='127.0.0.1', help='Adresse d\'écoute (défaut: 127.0.0.1)')
    run_parser.add_argument('--port', type=int, default=5000, help='Port d\'écoute (défaut: 5000)')
    run_parser.add_argument('--debug', action='store_true', help='Activer le mode debug')
    run_parser.add_argument('--production', action='store_true', help='Lancer en mode production (prioritaire sur --debug)')
    
    # Commande pour initialiser la base de données
    init_db_parser = subparsers.add_parser('init-db', help='Initialiser la base de données')
    init_db_parser.add_argument('--cts-token', help="Token API pour le service de transport CTS")
    init_db_parser.add_argument('--admin-username', help="Nom d'utilisateur pour le premier administrateur")
    init_db_parser.add_argument('--admin-password', help="Mot de passe pour le premier administrateur")
    
    args = parser.parse_args()
    
    # Exécuter la commande appropriée
    if args.command == 'init-db':
        with app.app_context():
            from app.cli import init_db
            init_db(
                cts_token=getattr(args, 'cts_token', None),
                admin_username=getattr(args, 'admin_username', None),
                admin_password=getattr(args, 'admin_password', None)
            )
    else:  # Comportement par défaut: lancer le serveur
        # Si aucune commande n'est fournie, supposer 'run'
        # Déterminer le mode d'exécution
        debug_mode = getattr(args, 'debug', False)
        if getattr(args, 'production', False):
            debug_mode = False
            print("Application lancée en mode production")
        elif debug_mode:
            print("Application lancée en mode debug")
        else:
            print("Application lancée en mode standard")
        
        # Lancement du serveur
        app.run(
            host=getattr(args, 'host', '127.0.0.1'),
            port=getattr(args, 'port', 5000),
            debug=debug_mode
        )