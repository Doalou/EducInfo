# Makefile pour le projet EducInfo
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
AUTHOR ?= doalou
REGISTRY ?= docker.io
BASE_IMAGE_REGISTRY ?= docker.io
WEB_SITE ?= doalo.fr
IMAGE_VERSION ?= 1.1.0
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
	@echo "  run         : Lance l'application en mode développement"
	@echo "  test        : Lance les tests"
	@echo "  init-db     : Initialise la base de données"
	@echo "  docker      : Construit et lance l'image Docker"
	@echo "  docker.build: Construit l'image Docker"
	@echo "  docker.run  : Lance l'image Docker"
	@echo "  docker.test : Lance les tests dans Docker"
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
