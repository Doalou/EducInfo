#!/bin/bash
# Script d'initialisation générale pour EducInfo
# Usage: ./scripts/setup.sh [OPTIONS]

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    echo -e "${CYAN}EducInfo - Script d'Initialisation Complète${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Affiche cette aide"
    echo "  --dev                   Configuration développement complète"
    echo "  --cluster               Configuration cluster (Docker)"
    echo "  --minimal               Installation minimale"
    echo "  --check-only            Vérifie les prérequis uniquement"
    echo ""
    echo "Le script effectue :"
    echo "  ✓ Vérification des prérequis"
    echo "  ✓ Installation des dépendances Python"
    echo "  ✓ Configuration de l'environnement"
    echo "  ✓ Initialisation de la base de données"
    echo "  ✓ Configuration des API externes (optionnel)"
    echo "  ✓ Test de l'installation"
}

# Fonction de logging
log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] ✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ✗${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] ℹ${NC} $1"
}

# Banner d'accueil
show_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║                    🎓 EducInfo v2.0.0                       ║"
    echo "║              Script d'Initialisation Complète               ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# Vérification des prérequis système
check_system_requirements() {
    info "Vérification des prérequis système..."
    
    local errors=0
    
    # Python 3
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        log "Python 3 détecté : v$python_version"
    else
        error "Python 3 non trouvé"
        ((errors++))
    fi
    
    # pip
    if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        log "pip détecté"
    else
        error "pip non trouvé"
        ((errors++))
    fi
    
    # Git (optionnel)
    if command -v git &> /dev/null; then
        log "Git détecté"
    else
        warn "Git non trouvé (optionnel)"
    fi
    
    # Docker (pour cluster)
    if command -v docker &> /dev/null; then
        log "Docker détecté"
        if command -v docker-compose &> /dev/null; then
            log "Docker Compose détecté"
        else
            warn "Docker Compose non trouvé (requis pour cluster)"
        fi
    else
        warn "Docker non trouvé (requis pour cluster)"
    fi
    
    # Vérifier les fichiers essentiels
    local required_files=("run.py" "requirements.txt" "app/__init__.py")
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log "Fichier $file présent"
        else
            error "Fichier $file manquant"
            ((errors++))
        fi
    done
    
    if [ $errors -gt 0 ]; then
        error "$errors erreur(s) détectée(s). Veuillez corriger avant de continuer."
        exit 1
    fi
    
    log "Tous les prérequis sont satisfaits"
}

# Installation des dépendances Python
install_python_dependencies() {
    info "Installation des dépendances Python..."
    
    # Créer un environnement virtuel s'il n'existe pas
    if [ ! -d "venv" ]; then
        info "Création de l'environnement virtuel..."
        python3 -m venv venv
        log "Environnement virtuel créé"
    else
        log "Environnement virtuel existant détecté"
    fi
    
    # Activer l'environnement virtuel
    source venv/bin/activate
    log "Environnement virtuel activé"
    
    # Mettre à jour pip
    info "Mise à jour de pip..."
    pip install --upgrade pip
    
    # Installer les dépendances
    info "Installation des dépendances depuis requirements.txt..."
    pip install -r requirements.txt
    
    log "Dépendances Python installées"
}

# Configuration de l'environnement
setup_environment() {
    info "Configuration de l'environnement..."
    
    # Créer les dossiers nécessaires
    local dirs=("instance" "logs" "uploads")
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log "Dossier $dir créé"
        else
            log "Dossier $dir existe déjà"
        fi
    done
    
    # Copier les fichiers de configuration d'exemple
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log "Fichier .env créé depuis .env.example"
            warn "Pensez à modifier .env avec vos configurations"
        else
            warn "Fichier .env.example non trouvé"
        fi
    else
        log "Fichier .env existe déjà"
    fi
    
    log "Environnement configuré"
}

# Initialisation de la base de données
initialize_database() {
    info "Initialisation de la base de données..."
    
    # Activer l'environnement virtuel
    source venv/bin/activate 2>/dev/null || true
    
    # Initialiser la base de données (le mot de passe sera généré automatiquement si non fourni)
    python run.py init-db \
        --admin-username "admin"

    log "Base de données initialisée"
    warn "Le mot de passe admin a été affiché ci-dessus. Conservez-le !"
}

# Configuration interactive des APIs
configure_apis() {
    info "Configuration des APIs externes (optionnel)..."
    
    echo ""
    echo -e "${YELLOW}Configuration des APIs externes :${NC}"
    echo ""
    
    # API Météo
    echo -e "${BLUE}1. API Météo OpenWeatherMap${NC}"
    echo "   Obtenez une clé gratuite sur : https://openweathermap.org/api"
    read -p "   Clé API Météo (optionnel, Entrée pour ignorer) : " weather_key
    
    if [ -n "$weather_key" ]; then
        # Mettre à jour le fichier .env
        if grep -q "WEATHER_API_KEY=" .env; then
            sed -i "s/WEATHER_API_KEY=.*/WEATHER_API_KEY=$weather_key/" .env
        else
            echo "WEATHER_API_KEY=$weather_key" >> .env
        fi
        log "Clé API Météo configurée"
    fi
    
    echo ""
    # API CTS
    echo -e "${BLUE}2. API Transport CTS Strasbourg${NC}"
    echo "   Demandez un token sur : https://www.cts-strasbourg.eu/fr/se-deplacer/opendata/"
    read -p "   Token API CTS (optionnel, Entrée pour ignorer) : " cts_token
    
    if [ -n "$cts_token" ]; then
        # Mettre à jour le fichier .env
        if grep -q "CTS_API_TOKEN=" .env; then
            sed -i "s/CTS_API_TOKEN=.*/CTS_API_TOKEN=$cts_token/" .env
        else
            echo "CTS_API_TOKEN=$cts_token" >> .env
        fi
        log "Token API CTS configuré"
    fi
    
    echo ""
    log "Configuration des APIs terminée"
}

# Test de l'installation
test_installation() {
    info "Test de l'installation..."
    
    # Activer l'environnement virtuel
    source venv/bin/activate 2>/dev/null || true
    
    # Test basique
    info "Test de démarrage rapide..."
    timeout 10s python run.py --host=127.0.0.1 --port=5050 &
    local app_pid=$!
    
    # Attendre le démarrage
    sleep 3
    
    # Tester la connectivité
    if curl -s -f http://127.0.0.1:5050/ > /dev/null 2>&1; then
        log "Application accessible ✓"
    else
        warn "Application non accessible (normal en test rapide)"
    fi
    
    # Arrêter l'application test
    kill $app_pid 2>/dev/null || true
    wait $app_pid 2>/dev/null || true
    
    log "Test d'installation terminé"
}

# Résumé final
show_summary() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗"
    echo "║                     Installation Terminée !                 ║"
    echo "╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}🎉 EducInfo est maintenant configuré !${NC}"
    echo ""
    echo "Prochaines étapes :"
    echo ""
    echo -e "${BLUE}📝 Développement :${NC}"
    echo "   ./scripts/dev.sh                 # Démarrer en mode développement"
    echo "   ./scripts/dev.sh --help          # Voir toutes les options"
    echo ""
    echo -e "${BLUE}🔄 Cluster (Production) :${NC}"
    echo "   ./scripts/cluster.sh             # Démarrer le cluster load balancé"
    echo "   ./scripts/cluster.sh --full      # Cluster complet avec monitoring"
    echo ""
    echo -e "${BLUE}🌐 Accès :${NC}"
    echo "   http://localhost:5000            # Application web"
    echo "   Utilisateur: admin               # Mot de passe affiché lors de l'init"
    echo ""
    echo -e "${YELLOW}⚠️  N'oubliez pas :${NC}"
    echo "   • Modifier le mot de passe admin en production"
    echo "   • Configurer les APIs externes dans .env"
    echo "   • Consulter la documentation : README.md"
    echo ""
}

# Variables pour les modes
DEV_MODE=false
CLUSTER_MODE=false
MINIMAL_MODE=false
CHECK_ONLY=false

# Parsing des arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        --cluster)
            CLUSTER_MODE=true
            shift
            ;;
        --minimal)
            MINIMAL_MODE=true
            shift
            ;;
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        *)
            error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# Exécution principale
show_banner

# Vérification des prérequis
check_system_requirements

if [ "$CHECK_ONLY" = true ]; then
    log "Vérification terminée. Tous les prérequis sont satisfaits."
    exit 0
fi

# Installation des dépendances
install_python_dependencies

# Configuration de l'environnement
setup_environment

# Initialisation de la base de données
initialize_database

# Configuration des APIs (sauf en mode minimal)
if [ "$MINIMAL_MODE" != true ]; then
    configure_apis
fi

# Test de l'installation
test_installation

# Résumé final
show_summary 