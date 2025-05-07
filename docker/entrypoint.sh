#!/bin/sh
set -e

# Vérifier si l'application existe
cd /app

# Initialiser la base de données si nécessaire
if [ ! -f /app/instance/educinfo.db ]; then
    echo "Base de données non trouvée. Initialisation..."
    python run.py init-db || echo "Échec de l'initialisation de la base de données"
fi

# Exécuter la commande fournie
echo "Démarrage de l'application..."
exec "$@"
