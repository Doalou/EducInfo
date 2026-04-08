# ==============================================
# Stage 1: Builder - Installation des dépendances
# ==============================================
FROM python:3.13-slim-bookworm as builder

LABEL maintainer="contact@doalo.fr"
LABEL description="EducInfo - Plateforme d'Information Scolaire (Builder)"

# Variables d'environnement pour le build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Installation des dépendances système pour la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    libssl-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Créer un environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip dans l'environnement virtuel
RUN pip install --upgrade pip setuptools wheel

# Copie et installation des dépendances Python (gunicorn inclus)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==============================================
# Stage 2: Production - Image finale optimisée
# ==============================================
FROM python:3.13-slim-bookworm as production

LABEL maintainer="contact@doalo.fr"
LABEL version="1.3.0"
LABEL description="EducInfo - Plateforme d'Information Scolaire"

# Métadonnées de l'image
LABEL org.opencontainers.image.title="EducInfo"
LABEL org.opencontainers.image.description="Plateforme d'information scolaire avec Flask"
LABEL org.opencontainers.image.version="1.3.0"
LABEL org.opencontainers.image.vendor="DoaLo"
LABEL org.opencontainers.image.url="https://github.com/doalo/educinfo"
LABEL org.opencontainers.image.source="https://github.com/doalo/educinfo"

# Variables d'environnement pour la production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PATH="/opt/venv/bin:$PATH"

# Installation des dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    dumb-init \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Copie de l'environnement virtuel depuis le builder
COPY --from=builder /opt/venv /opt/venv

# Créer un utilisateur et groupe non-root
RUN groupadd -r educinfo --gid=1000 && \
    useradd -r -g educinfo --uid=1000 --home-dir=/app --shell=/bin/bash educinfo

# Répertoire de travail
WORKDIR /app

# Copie du code source (optimisé avec .dockerignore)
COPY --chown=educinfo:educinfo . .

# Configuration et permissions des scripts (les fins de ligne LF sont gérées par .gitattributes)
RUN cp /app/docker/entrypoint.sh /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh && \
    chmod +x /app/scripts/*.sh

# Création des dossiers nécessaires avec bonnes permissions
RUN mkdir -p /app/instance /app/logs /app/uploads && \
    chown -R educinfo:educinfo /app && \
    chmod -R 755 /app/instance /app/logs /app/uploads

# Health check pour Docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Changement vers l'utilisateur non-root
USER educinfo

# Exposition du port
EXPOSE 5000

# Les volumes sont gérés par docker-compose, pas dans le Dockerfile

# Entrypoint avec dumb-init pour une gestion propre des signaux
ENTRYPOINT ["/usr/bin/dumb-init", "--", "/usr/local/bin/entrypoint.sh"]

# Nombre de workers configurable (défaut: auto basé sur CPU)
ENV GUNICORN_WORKERS=""

# Commande par défaut optimisée pour la production
CMD ["gunicorn", \
    "--bind", "0.0.0.0:5000", \
    "--workers", "3", \
    "--worker-class", "sync", \
    "--worker-connections", "1000", \
    "--max-requests", "1000", \
    "--max-requests-jitter", "100", \
    "--timeout", "30", \
    "--keep-alive", "2", \
    "--log-level", "info", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--capture-output", \
    "run:app"]

# ==============================================
# Stage 3: Development - Image de développement
# ==============================================
FROM production as development

LABEL description="EducInfo - Plateforme d'Information Scolaire (Development)"

# Repasser en root temporairement pour les installations
USER root

# Installation des outils de développement
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    htop \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances de développement
COPY requirements-dev.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements-dev.txt

# Variables d'environnement pour le développement
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

# Retour à l'utilisateur non-root
USER educinfo

# Commande par défaut pour le développement
CMD ["python", "run.py", "run", "--host=0.0.0.0", "--port=5000", "--debug"]

