#!/bin/bash
set -e

# Initialiser la base de données si nécessaire
flask db upgrade

# Exécuter la commande fournie
exec "$@"
