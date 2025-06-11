# Makefile optimisé pour EducInfo
.PHONY: help install run test docker.build docker.run docker.test clean

# Variables Python
PYTHON = python
PIP = pip
VENV = .venv
VENV_BIN = $(VENV)/bin
VENV_PYTHON = $(VENV_BIN)/python
VENV_PIP = $(VENV_BIN)/pip

# Variables Docker
SUBDIRS ?= docker
PROJECT_NAME ?= educinfo
AUTHOR ?= doalo
REGISTRY ?= docker.io
BASE_IMAGE_REGISTRY ?= docker.io
WEB_SITE ?= doalo.fr
IMAGE_VERSION ?= 1.2
IMAGE_NAME ?= $(PROJECT_NAME)

# Ressources Docker
CPUS ?= 4.0
CPU_SHARES ?= 1024
MEMORY ?= 8GB
MEMORY_RESERVATION ?= 2GB
TMPFS_SIZE ?= 4GB
BUILD_CPU_SHARES ?= 1024
BUILD_MEMORY ?= 8GB

# Commandes Docker
TEST_CMD ?= "./docker/test/test.sh"
RUN_CMD ?= "python run.py run"

# Aide
help:
	@echo "Commandes disponibles :"
	@echo "  help        : Affiche cette aide"
	@echo "  install     : Installe les dépendances"
	@echo "  run         : Lance l'application"
	@echo "  test        : Lance les tests"
	@echo "  init-db     : Initialise la base de données"
	@echo "  docker      : Construit et lance Docker"
	@echo "  docker.build: Construit l'image Docker"
	@echo "  docker.run  : Lance l'image Docker"
	@echo "  docker.test : Lance les tests Docker"
	@echo "  cluster     : Lance le cluster load balancé"
	@echo "  cluster-full: Lance le cluster complet (3 instances + monitoring)"
	@echo "  cluster-stop: Arrête le cluster"
	@echo "  cluster-status: Affiche le statut du cluster"
	@echo "  setup       : Initialisation complète (via scripts/setup.sh)"
	@echo "  dev-setup   : Configuration développement (via scripts/dev.sh)"
	@echo "  scripts     : Liste les scripts disponibles"
	@echo "  clean       : Nettoie les fichiers temporaires"

# Installation des dépendances
install:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install -r requirements.txt

# Lancement en mode développement
run:
	$(PYTHON) run.py run

# Lancement des tests
test:
	$(PYTHON) -m pytest tests/

# Initialisation de la base de données
init-db:
	$(PYTHON) run.py init-db

# Construction et lancement de l'image Docker
docker: docker.build docker.run

# Gestion du cluster load balancé
cluster:
	@echo "🚀 Démarrage du cluster EducInfo (2 instances)..."
	./scripts/cluster.sh

cluster-full:
	@echo "🚀 Démarrage du cluster EducInfo complet (3 instances + monitoring)..."
	./scripts/cluster.sh --full --monitoring

cluster-stop:
	@echo "🛑 Arrêt du cluster EducInfo..."
	./scripts/cluster.sh --stop

cluster-status:
	@echo "📊 Statut du cluster EducInfo..."
	./scripts/cluster.sh --status

cluster-logs:
	@echo "📋 Logs du cluster EducInfo..."
	./scripts/cluster.sh --logs

cluster-restart:
	@echo "🔄 Redémarrage du cluster EducInfo..."
	./scripts/cluster.sh --restart

# Initialisation complète via scripts
setup:
	@echo "🔧 Initialisation complète d'EducInfo..."
	./scripts/setup.sh

# Configuration développement via scripts
dev-setup:
	@echo "🔧 Configuration de l'environnement de développement..."
	./scripts/dev.sh --install --init

# Liste des scripts disponibles
scripts:
	@echo "📜 Scripts disponibles dans ./scripts/ :"
	@echo ""
	@echo "  🔧 setup.sh        : Initialisation complète"
	@echo "  🖥️  dev.sh          : Développement local"
	@echo "  🔄 cluster.sh      : Gestion du cluster"
	@echo "  🧪 test-docker.sh  : Tests Docker"
	@echo ""
	@echo "Consultez ./scripts/README.md pour plus d'informations"

# Nettoyage
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/

# Inclusion du Makefile Docker
include DockerImages.mk