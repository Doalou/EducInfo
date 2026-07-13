# Docker pour EducInfo

Ce dossier contient tous les fichiers nécessaires pour containeriser EducInfo avec Docker.

## Structure

- `Dockerfile` : Image Docker principale
- `entrypoint.sh` : Script d'initialisation du container
- `test/test.sh` : Script de test de l'application dans Docker
- `DockerImage.mk` : Makefile pour la construction avancée
- `Makefile` : Makefile simplifié

**Note :** L'application utilise `run.py` comme fichier principal d'exécution.

## Utilisation rapide avec docker-compose

### 1. Prérequis

Créez un fichier `.env` à la racine du projet :

```bash
# Configuration de base
ADMIN_USERNAME=admin
ADMIN_PASSWORD=votre_mot_de_passe_securise
SECRET_KEY=votre_cle_secrete_unique

# APIs optionnelles
WEATHER_API_KEY=votre_cle_openweather
CTS_API_TOKEN=votre_token_cts
```

### 2. Démarrage

```bash
# Construction et démarrage
docker-compose up --build

# En arrière-plan
docker-compose up -d --build
```

### 3. Accès

Avec `docker-compose.yml`, le port `5000` du conteneur est publié sur le port `5001` de la machine hôte.

L'application sera donc accessible sur : http://localhost:5001

> Note : l'exemple `docker run` plus bas expose bien `5000:5000`, donc dans ce cas précis l'accès reste `http://localhost:5000`.

## Utilisation avec Docker

### Construction de l'image

```bash
docker build -f docker/Dockerfile -t educinfo .
```

### Démarrage du container

```bash
docker run -d \
  --name educinfo-app \
  -p 5000:5000 \
  -v $(pwd)/instance:/app/instance \
  -v $(pwd)/logs:/app/logs \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_PASSWORD=your-secure-password \
  --env-file .env \
  educinfo
```

### Tests

```bash
# Test dans l'image
docker run --rm educinfo ./scripts/test-docker.sh

# Test via Makefile
make docker.test
```

## Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `FLASK_APP` | Application Flask | `run.py` |
| `FLASK_ENV` | Environnement | `production` |
| `ADMIN_USERNAME` | Nom admin initial | `admin` |
| `ADMIN_PASSWORD` | Mot de passe admin | (auto-généré) |
| `SECRET_KEY` | Clé secrète Flask | (auto-généré) |
| `WEATHER_API_KEY` | Clé OpenWeather | (vide) |
| `WEATHER_CITY` | Ville météo | `Strasbourg` |
| `CTS_API_TOKEN` | Token CTS | (vide) |

## Troubleshooting

### Base de données

La base de données est automatiquement initialisée au premier démarrage. Si vous voulez la réinitialiser :

```bash
# Supprimer les données persistantes
docker-compose down -v
rm -rf instance/educinfo.db

# Redémarrer
docker-compose up --build
```

### Logs

```bash
# Voir les logs
docker-compose logs -f

# Logs du container
docker logs educinfo-app
```

### Accès au container

```bash
# Shell dans le container
docker-compose exec educinfo /bin/bash

# Ou avec docker
docker exec -it educinfo-app /bin/bash
```

## Production

Pour la production, modifiez :

1. Le `SECRET_KEY` dans votre `.env`
2. Les mots de passe administrateurs
3. Utilisez un reverse proxy (nginx, traefik)
4. Configurez les sauvegardes des volumes `instance/` et `logs/`
