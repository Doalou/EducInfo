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
    parser.add_argument('--host', default='127.0.0.1', help='Adresse d\'écoute (défaut: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Port d\'écoute (défaut: 5000)')
    parser.add_argument('--debug', action='store_true', help='Activer le mode debug')
    parser.add_argument('--production', action='store_true', help='Lancer en mode production (prioritaire sur --debug)')
    
    args = parser.parse_args()
    
    # Déterminer le mode d'exécution
    debug_mode = args.debug
    if args.production:
        debug_mode = False
        print("Application lancée en mode production")
    elif debug_mode:
        print("Application lancée en mode debug")
    else:
        print("Application lancée en mode standard")
    
    # Lancement du serveur
    app.run(
        host=args.host,
        port=args.port,
        debug=debug_mode
    )