#!/bin/bash
# Script de développement pour EducInfo
# Usage: ./scripts/dev.sh [OPTIONS]

set -e

# Configuration par défaut
FLASK_ENV="development"
FLASK_DEBUG=1
HOST="0.0.0.0"
PORT=5000

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    echo "EducInfo - Script de Développement"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Affiche cette aide"
    echo "  -p, --port PORT         Port d'écoute (défaut: 5000)"
    echo "  --host HOST             Host d'écoute (défaut: 0.0.0.0)"
    echo "  --init                  Initialise la base de données"
    echo "  --reset                 Remet à zéro la base de données"
    echo "  --install               Installe les dépendances"
    echo "  --test                  Lance les tests"
    echo ""
    echo "Exemples:"
    echo "  $0                      # Démarre en mode développement"
    echo "  $0 --port 8000         # Démarre sur le port 8000"
    echo "  $0 --init              # Initialise la DB puis démarre"
    echo "  $0 --reset             # Remet à zéro la DB puis démarre"
}

# Fonction de logging
log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    log "Vérification des prérequis de développement..."
    
    if ! command -v python3 &> /dev/null; then
        error "Python 3 n'est pas installé"
        exit 1
    fi
    
    if [ ! -f "requirements.txt" ]; then
        error "Fichier requirements.txt non trouvé"
        exit 1
    fi
    
    if [ ! -f "run.py" ]; then
        error "Fichier run.py non trouvé"
        exit 1
    fi
    
    log "Prérequis validés ✓"
}

# Installation des dépendances
install_dependencies() {
    log "Installation des dépendances..."
    
    # Créer un environnement virtuel s'il n'existe pas
    if [ ! -d "venv" ]; then
        log "Création de l'environnement virtuel..."
        python3 -m venv venv
    fi
    
    # Activer l'environnement virtuel
    source venv/bin/activate
    
    # Installer les dépendances
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log "Dépendances installées ✓"
}

# Initialisation de la base de données
init_database() {
    log "Initialisation de la base de données..."
    
    # S'assurer que le dossier instance existe
    mkdir -p instance
    
    # Initialiser la base avec les données de développement
    python run.py init-db \
        --admin-username "admin" \
        --admin-password "admin123"
    
    log "Base de données initialisée ✓"
}

# Remise à zéro de la base de données
reset_database() {
    log "Remise à zéro de la base de données..."
    
    # Supprimer la base existante
    if [ -f "instance/educinfo.db" ]; then
        rm instance/educinfo.db
        log "Ancienne base supprimée"
    fi
    
    # Réinitialiser
    init_database
}

# Lancement des tests
run_tests() {
    log "Lancement des tests..."
    
    if [ -d "tests" ]; then
        # Activer l'environnement virtuel
        source venv/bin/activate 2>/dev/null || true
        
        # Installer pytest si nécessaire
        pip install pytest pytest-cov
        
        # Lancer les tests
        pytest tests/ -v --cov=app
        
        log "Tests terminés ✓"
    else
        warn "Dossier tests/ non trouvé"
    fi
}

# Démarrage de l'application
start_app() {
    log "Démarrage d'EducInfo en mode développement..."
    
    # Variables d'environnement
    export FLASK_ENV="$FLASK_ENV"
    export FLASK_DEBUG="$FLASK_DEBUG"
    
    # Activer l'environnement virtuel s'il existe
    if [ -d "venv" ]; then
        source venv/bin/activate
        log "Environnement virtuel activé"
    fi
    
    log "Application démarrant sur ${BLUE}http://${HOST}:${PORT}${NC}"
    log "Mode debug: ${GREEN}activé${NC}"
    log "Arrêt avec Ctrl+C"
    
    # Démarrer l'application
    python run.py --host="$HOST" --port="$PORT"
}

# Variables pour les actions
INIT_DB=false
RESET_DB=false
INSTALL_DEPS=false
RUN_TESTS=false

# Parsing des arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --init)
            INIT_DB=true
            shift
            ;;
        --reset)
            RESET_DB=true
            shift
            ;;
        --install)
            INSTALL_DEPS=true
            shift
            ;;
        --test)
            RUN_TESTS=true
            shift
            ;;
        *)
            error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# Exécution
check_prerequisites

if [ "$INSTALL_DEPS" = true ]; then
    install_dependencies
fi

if [ "$RESET_DB" = true ]; then
    reset_database
elif [ "$INIT_DB" = true ]; then
    init_database
fi

if [ "$RUN_TESTS" = true ]; then
    run_tests
    exit 0
fi

# Démarrer l'application par défaut
start_app 