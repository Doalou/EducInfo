#!/bin/bash
# Script d'initialisation pour EducInfo dans Docker
# 
# Ce script initialise l'application EducInfo dans un conteneur Docker
# en utilisant le fichier run.py principal du projet.
#
# Variables d'environnement supportées:
#   - ADMIN_USERNAME (défaut: admin)
#   - ADMIN_PASSWORD (auto-généré si non défini)
#   - CTS_API_TOKEN (optionnel)
#   - FLASK_APP (défaut: run.py)
#   - FLASK_ENV (défaut: production)

set -e

echo "=== Démarrage d'EducInfo (Docker) ==="

# Changer vers le répertoire de l'application
cd /app

# Définir la variable FLASK_APP pour les commandes Flask CLI
export FLASK_APP=${FLASK_APP:-"run.py"}
echo "FLASK_APP configuré: $FLASK_APP"

# Vérifier si la base de données existe et l'initialiser si nécessaire
DB_PATH="/app/instance/educinfo.db"
if [ ! -f "$DB_PATH" ]; then
    echo "Base de données non trouvée: $DB_PATH"
    echo "Initialisation de la base de données..."
    
    # Utiliser les variables d'environnement (mot de passe auto-généré si non défini)
    ADMIN_USER=${ADMIN_USERNAME:-"admin"}
    ADMIN_PASS=${ADMIN_PASSWORD:-$(python -c "import secrets; print(secrets.token_urlsafe(12))")}
    CTS_TOKEN=${CTS_API_TOKEN:-""}
    
    # Construire la commande d'initialisation avec run.py
    INIT_CMD="python run.py init-db --admin-username \"$ADMIN_USER\" --admin-password \"$ADMIN_PASS\""
    if [ ! -z "$CTS_TOKEN" ]; then
        INIT_CMD="$INIT_CMD --cts-token \"$CTS_TOKEN\""
        echo "Token CTS configuré pour l'initialisation"
    fi
    
    # Exécuter l'initialisation
    echo "Commande d'initialisation: $INIT_CMD"
    eval $INIT_CMD || {
        echo "ERREUR: Échec de l'initialisation de la base de données"
        exit 1
    }
    
    echo "✅ Base de données initialisée avec succès."
    echo "👤 Utilisateur admin créé: $ADMIN_USER"
else
    echo "✅ Base de données existante détectée: $DB_PATH"
fi

# Créer les dossiers nécessaires s'ils n'existent pas
echo "Création des dossiers nécessaires..."
mkdir -p /app/logs /app/instance/uploads

# Ajuster les permissions si nécessaire
chmod -R 755 /app/instance /app/logs 2>/dev/null || echo "ℹ️  Permissions déjà configurées"

# Afficher les informations de démarrage
echo "📊 Informations de démarrage:"
echo "   - Répertoire de travail: /app"
echo "   - Base de données: $DB_PATH"
echo "   - FLASK_APP: $FLASK_APP"
echo "   - FLASK_ENV: ${FLASK_ENV:-'production'}"

echo "🚀 Configuration terminée. Lancement de l'application..."

# Exécuter la commande fournie
exec "$@"
