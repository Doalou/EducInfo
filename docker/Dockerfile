FROM python:3.12-slim

LABEL maintainer="contact@doalo.fr"
LABEL version="1.1"
LABEL description="EducInfo - Plateforme d'Information Scolaire"

# Définition des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    dos2unix \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn==21.2.0 && \
    pip list | grep gunicorn

# Copie du code source
COPY . .

# Entrypoint - Configurer avant de changer d'utilisateur
COPY docker/entrypoint.sh /entrypoint.sh
RUN dos2unix /entrypoint.sh && chmod +x /entrypoint.sh

# Création de l'utilisateur non-root
RUN groupadd -r educinfo && useradd -r -g educinfo educinfo \
    && mkdir -p /app/instance /app/logs \
    && chown -R educinfo:educinfo /app

# Change vers l'utilisateur non-root
USER educinfo

# Exposition du port
EXPOSE 5000

# Configuration de l'entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Commande à exécuter au démarrage du conteneur
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "run:app"]

