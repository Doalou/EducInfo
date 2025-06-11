#!/bin/bash
# Script de démarrage pour EducInfo en mode cluster load balancé
# Usage: ./scripts/cluster.sh [OPTIONS]

set -e

# Configuration par défaut
PROFILE="basic"
COMPOSE_FILE="docker-compose.cluster.yml"
MONITORING=false
FULL_CLUSTER=false

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    echo "EducInfo - Démarrage Cluster Load Balancé"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Affiche cette aide"
    echo "  -f, --full              Démarre avec 3 instances (au lieu de 2)"
    echo "  -m, --monitoring        Active Prometheus + Grafana"
    echo "  -d, --dev               Mode développement avec logs détaillés"
    echo "  --stop                  Arrête le cluster"
    echo "  --restart               Redémarre le cluster"
    echo "  --status                Affiche le statut du cluster"
    echo "  --logs [service]        Affiche les logs (optionnel: service spécifique)"
    echo "  --scale instances=N     Scale le nombre d'instances EducInfo"
    echo ""
    echo "Exemples:"
    echo "  $0                      # Démarre 2 instances + load balancer"
    echo "  $0 --full --monitoring  # Démarre 3 instances + monitoring"
    echo "  $0 --logs nginx         # Affiche les logs Nginx"
    echo "  $0 --scale educinfo-1=0 # Désactive temporairement l'instance 1"
}

# Fonction de logging
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    log "Vérification des prérequis..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "Fichier $COMPOSE_FILE non trouvé"
        exit 1
    fi
    
    log "Prérequis validés ✓"
}

# Construction des profils Docker Compose
build_profiles() {
    local profiles=""
    
    if [ "$FULL_CLUSTER" = true ]; then
        profiles="$profiles --profile full-cluster"
    fi
    
    if [ "$MONITORING" = true ]; then
        profiles="$profiles --profile monitoring"
    fi
    
    echo "$profiles"
}

# Démarrage du cluster
start_cluster() {
    log "Démarrage du cluster EducInfo..."
    
    local profiles=$(build_profiles)
    
    # Créer les réseaux et volumes si nécessaire
    docker-compose -f "$COMPOSE_FILE" $profiles up -d --build
    
    log "Cluster démarré ! Services actifs :"
    docker-compose -f "$COMPOSE_FILE" $profiles ps
    
    echo ""
    log "URLs d'accès :"
    echo "  • Application principale: ${BLUE}http://localhost${NC}"
    echo "  • Health check: ${BLUE}http://localhost/health${NC}"
    echo "  • Statut Nginx: ${BLUE}http://localhost/nginx-status${NC} (depuis le réseau local)"
    
    if [ "$MONITORING" = true ]; then
        echo "  • Prometheus: ${BLUE}http://localhost:9090${NC}"
        echo "  • Grafana: ${BLUE}http://localhost:3000${NC} (admin/admin)"
    fi
    
    echo ""
    warn "Attendez 30-60 secondes que tous les services soient prêts"
    
    # Vérifier la santé du cluster
    sleep 10
    check_cluster_health
}

# Arrêt du cluster
stop_cluster() {
    log "Arrêt du cluster..."
    
    local profiles=$(build_profiles)
    docker-compose -f "$COMPOSE_FILE" $profiles down
    
    log "Cluster arrêté ✓"
}

# Redémarrage du cluster
restart_cluster() {
    log "Redémarrage du cluster..."
    stop_cluster
    sleep 2
    start_cluster
}

# Vérification de la santé du cluster
check_cluster_health() {
    log "Vérification de la santé du cluster..."
    
    # Tester la connectivité
    if curl -s -f http://localhost/health > /dev/null 2>&1; then
        log "Health check: ${GREEN}OK${NC}"
    else
        warn "Health check: ${RED}FAIL${NC}"
    fi
    
    # Afficher les stats des conteneurs
    echo ""
    echo "État des conteneurs :"
    docker-compose -f "$COMPOSE_FILE" ps --format "table {{.Service}}\t{{.State}}\t{{.Ports}}"
}

# Affichage des logs
show_logs() {
    local service="$1"
    local profiles=$(build_profiles)
    
    if [ -n "$service" ]; then
        log "Logs du service: $service"
        docker-compose -f "$COMPOSE_FILE" $profiles logs -f "$service"
    else
        log "Logs de tous les services"
        docker-compose -f "$COMPOSE_FILE" $profiles logs -f
    fi
}

# Mise à l'échelle
scale_service() {
    local scale_args="$1"
    local profiles=$(build_profiles)
    
    log "Mise à l'échelle: $scale_args"
    docker-compose -f "$COMPOSE_FILE" $profiles up -d --scale $scale_args
    
    # Vérifier le résultat
    docker-compose -f "$COMPOSE_FILE" $profiles ps
}

# Affichage du statut
show_status() {
    log "Statut du cluster :"
    
    local profiles=$(build_profiles)
    docker-compose -f "$COMPOSE_FILE" $profiles ps
    
    echo ""
    check_cluster_health
    
    echo ""
    log "Ressources utilisées :"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Parsing des arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--full)
            FULL_CLUSTER=true
            shift
            ;;
        -m|--monitoring)
            MONITORING=true
            shift
            ;;
        -d|--dev)
            export COMPOSE_LOG_LEVEL=DEBUG
            shift
            ;;
        --stop)
            check_prerequisites
            stop_cluster
            exit 0
            ;;
        --restart)
            check_prerequisites
            restart_cluster
            exit 0
            ;;
        --status)
            show_status
            exit 0
            ;;
        --logs)
            shift
            show_logs "$1"
            exit 0
            ;;
        --scale)
            shift
            check_prerequisites
            scale_service "$1"
            exit 0
            ;;
        *)
            error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# Démarrage par défaut
check_prerequisites
start_cluster 