#!/bin/bash
set -euo pipefail

echo "=== Test d'EducInfo dans Docker ==="

# Test 1: Vérifier que Python et Flask sont installés
echo "Test 1: Vérification de Python et Flask..."
python --version
pip show flask

# Test 2: Vérifier que FLASK_APP est défini
echo "Test 2: Vérification de FLASK_APP..."
if [ -z "${FLASK_APP:-}" ]; then
    echo "ERREUR: FLASK_APP n'est pas défini"
    exit 1
fi
echo "FLASK_APP = $FLASK_APP"

# Test 3: Vérifier la structure de l'application
echo "Test 3: Vérification de la structure de l'application..."
if [ ! -f "run.py" ]; then
    echo "ERREUR: run.py introuvable"
    exit 1
fi

if [ ! -d "app" ]; then
    echo "ERREUR: dossier app introuvable"
    exit 1
fi

# Test 4: Vérifier que la base de données peut être initialisée
echo "Test 4: Test d'initialisation de la base de données..."
if [ ! -f "/app/instance/educinfo.db" ]; then
    echo "Base de données non trouvée, tentative d'initialisation..."
    python run.py init-db --admin-username "testadmin" --admin-password "testpass123"
    echo "Initialisation réussie"
else
    echo "Base de données existante détectée"
fi

# Test 5: Vérifier que l'application peut démarrer avec run.py
echo "Test 5: Test de démarrage de l'application avec run.py..."
timeout 10s python run.py run --host=0.0.0.0 --port=5000 &
APP_PID=$!

# Attendre que l'application démarre
sleep 3

# Tester si l'application répond
if curl -f http://localhost:5000/ > /dev/null 2>&1; then
    echo "✅ Application accessible sur le port 5000"
else
    echo "ERREUR: Application non accessible"
    kill $APP_PID 2>/dev/null || true
    exit 1
fi

# Arrêter l'application
kill $APP_PID 2>/dev/null || true
wait $APP_PID 2>/dev/null || true

echo "=== Tous les tests ont réussi! ==="
