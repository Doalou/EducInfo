# 📺 EducInfo v1.3.0

> **Système d'affichage scolaire intelligent optimisé pour écrans TV**

EducInfo est une solution complète d'affichage numérique pour établissements scolaires (halls, couloirs, espaces communs). Elle permet de diffuser en temps réel les absences des professeurs, menus de cantine, événements, météo et transports, avec une interface "Pixel Perfect" pour écrans de télévision.

---

## ✨ Fonctionnalités Principales

### 🎯 Affichage TV & UX
- **Design pour Grands Écrans** : Interface épurée, polices lisibles à distance, contrastes élevés.
- **Mode TV Exclusif** : Activation par simple URL (`?tv=true`) ou touche `F11`.
- **Auto-Refresh** : Mise à jour automatique des données sans intervention.
- **Thèmes Adaptatifs** : Mode sombre/clair automatique.

### 📊 Contenu & Services
- **Absences Professeurs** : Gestion par jour de la semaine.
- **Menus Cantine** : Affichage coloré par catégories (Entrées, Plats, Desserts).
- **Widgets Intelligents** :
  - 🌤️ Météo locale (OpenWeatherMap).
  - 🚌 Transports en commun (API CTS Strasbourg).
  - 🕒 Horloge temps réel.
- **Événements** : Agenda scolaire et annonces importantes.

### ⚙️ Administration & Technique
- **Dashboard Admin** : Gestion complète des données et utilisateurs.
- **Monitoring** : Métriques système (CPU/RAM/Disque) et base de données.
- **Haute Disponibilité** : Support complet du Clustering et Load Balancing.
- **Sécurité** : Authentification forte, CSRF protection, Headers sécurisés.

---

## 🚀 Installation & Démarrage

EducInfo propose deux modes d'installation selon vos besoins.

### Option 1 : Docker (Recommandé)

#### Mode Simple (Développement / Petite structure)
Idéal pour tester ou pour une installation légère sur un seul serveur.

```bash
# Démarrer l'application
docker-compose up -d

# Accéder à l'application
# http://localhost:5001
```

#### Mode Cluster (Production)
Architecture haute disponibilité avec Load Balancer Nginx, Redis et PostgreSQL.

```bash
# Développement
make dev                # Démarrer en mode développement
make setup             # Installation complète
make dev-setup         # Configuration développement

# Production / Cluster
EducInfo est une application web Flask spécialement conçue pour l'affichage sur écrans de télévision dans les établissements scolaires (halls, couloirs, espaces communs):
- **📺 Affichage TV optimisé** pour écrans larges et très larges
- **👨‍🏫 Absences des professeurs** avec mise à jour automatique
- **🍽️ Menus de la cantine** avec affichage par catégories colorées
- **🌤️ Informations météo en temps réel** avec émojis visuels
- **🚌 Horaires des transports** (CTS Strasbourg) avec temps d'attente
- **📅 Événements scolaires** à venir avec descriptions
- **🎨 Interface adaptative** avec mode sombre/clair automatique
- **⚡ Système de cache optimisé** pour performances fluides
- **📊 Monitoring et métriques système** pour supervision

## ✨ Nouveautés de la version 2.0.0

### 🔗 Load Balancing et Haute Disponibilité
- **Cluster multi-instances** : Déploiement avec 2-3 instances pour la haute disponibilité
- **Load balancer Nginx** : Répartition intelligente du trafic avec health checks
- **Cache Redis partagé** : Métriques distribuées et découverte automatique d'instances
- **Métriques agrégées** : Interface admin adaptée pour le monitoring cluster
- **Déploiement simplifié** : Script `start-cluster.sh` et commandes Makefile intégrées
- **Monitoring avancé** : Support Prometheus/Grafana optionnel

### 🔧 Système de Métriques Avancé
- **Métriques système réelles** : CPU, mémoire, disque avec `psutil`
- **Métriques base de données** : Compteurs réels des entités
- **Interface admin modernisée** : Dashboard métriques avec barres de progression
- **Monitoring robuste** : Gestion d'erreurs et fallbacks gracieux
- **Documentation complète** : Guide d'installation et dépannage (`INSTALLATION_METRICS.md`)

### 🎨 Améliorations Visuelles TV
- **Interface d'administration repensée** : Design moderne optimisé pour la gestion
- **Cartes colorées** : Bordures arc-en-ciel et effets visuels pour écrans larges
- **Animations fluides** : Transitions d'entrée échelonnées pour affichage TV
- **Contraste optimisé** : Meilleure lisibilité sur grands écrans en mode sombre/clair
- **Cohérence visuelle** : Harmonisation des styles pour usage professionnel

### 📺 Mode TV pour Affichage Large
- **Interface TV dédiée** : Design épuré et lisible à distance
- **Plein écran** : Support F11 et contrôles intégrés
- **Auto-refresh** : Mise à jour automatique des données
- **Polices grandes** : Optimisé pour la lecture à distance
- **Contrastes élevés** : Visibilité parfaite en toutes conditions

### 🔧 Améliorations techniques majeures
- **Système de cache avancé** : Support Redis avec fallback intelligent
- **Monitoring intégré** : Métriques Prometheus et health checks
- **Sécurité renforcée** : En-têtes de sécurité, CSRF protection améliorée
- **Architecture modulaire** : Services optimisés et gestion d'erreurs robuste
- **Docker multi-stage** : Images optimisées pour production et développement

### 🛡️ Sécurité et Performance
- Mise à jour des dépendances vers les dernières versions sécurisées
- Validation et chiffrement renforcés
- Cache intelligent avec gestion des pannes
- Logging structuré avec rotation automatique
- Rate limiting configurable

## 📊 Système de Métriques Avancé

### Dashboard Métriques Admin
- **📈 Métriques Système** : CPU, RAM, disque en temps réel
- **🗃️ Métriques Base de Données** : Compteurs utilisateurs, absences, événements, menus
- **⚡ Performance** : Uptime, cache, status des APIs
- **🎯 Indicateurs visuels** : Barres de progression colorées selon les seuils

### Installation du Monitoring
```bash
# Installation automatique avec les dépendances
pip install -r requirements.txt

# Vérification du système de métriques
flask admin metrics-test

# Documentation complète
cat INSTALLATION_METRICS.md
```

### Métriques Disponibles
- **CPU Usage** : Pourcentage d'utilisation processeur
- **Memory Usage** : Utilisation RAM avec seuils d'alerte
- **Disk Usage** : Espace disque utilisé/disponible
- **Database Counts** : Nombre d'entités par type
- **Cache Status** : Fonctionnalité et performance du cache
- **Uptime** : Temps de fonctionnement de l'application

## 📺 Mode TV - Affichage pour Télévisions

### Activation du Mode TV
- **Bouton Mode TV** : Clic sur le bouton en haut à droite
- **Raccourci clavier** : Appuyez sur `F11`
- **URL directe** : Ajoutez `?tv=true` à l'URL
- **Auto-démarrage** : Le mode se souvient de votre préférence

### Fonctionnalités TV
- ⏰ **Horloge en temps réel** avec date complète
- 🌤️ **Météo intégrée** avec température et conditions
- 📊 **Widgets adaptatifs** selon la configuration
- 🔄 **Rafraîchissement automatique** toutes les 30 secondes
- 🖥️ **Mode plein écran** avec contrôles dédiés
- 🎨 **Design épuré** avec polices XL pour lisibilité à distance

### Optimisations pour TV
- **Tailles de police** : 20px minimum, jusqu'à 4rem pour les titres
- **Contrastes élevés** : Couleurs vives et bordures marquées
- **Espacement généreux** : Padding et marges augmentés
- **Animations fluides** : Transitions et effects visuels
- **Responsive XXL** : Adaptation automatique aux très grands écrans

## Structure du Projet

Le projet est organisé selon une architecture modulaire Flask moderne:

```
EducInfo/
├── app/                           # Code de l'application
│   ├── __init__.py                # Factory pattern Flask
│   ├── blueprints/                # Routes organisées par fonctionnalité
│   │   ├── admin/                 # Administration avec métriques
│   │   ├── api/                   # API REST
│   │   ├── auth/                  # Authentification
│   │   ├── errors/                # Gestion d'erreurs
│   │   └── public/                # Pages publiques
│   ├── models/                    # Modèles de données SQLAlchemy
│   ├── services/                  # Services et logique métier
│   │   ├── weather.py             # Service météo OpenWeather
│   │   ├── transport.py           # Service transport CTS
│   │   └── menu.py                # Service gestion menus
│   ├── static/                    # Ressources statiques
│   │   ├── css/
│   │   │   ├── style.css          # Styles généraux améliorés
│   │   │   ├── darkmode.css       # Mode sombre optimisé
│   │   │   └── tv-display.css     # 🆕 Styles Mode TV
│   │   └── js/
│   │       ├── main.js            # JavaScript principal
│   │       └── tv-mode.js         # 🆕 Logique Mode TV
│   ├── templates/                 # Templates Jinja2
│   │   └── admin/                 # 🆕 Templates admin redesignés
│   ├── utils/                     # Fonctions utilitaires
│   ├── config.py                  # Configuration par environnement
│   ├── extensions.py              # Extensions Flask (DB, Cache, etc.)
│   └── cli.py                     # Commandes CLI personnalisées
├── docker/                        # Configuration Docker multi-stage
├── tests/                         # Tests unitaires et d'intégration
├── INSTALLATION_METRICS.md        # 🆕 Guide des métriques système
├── pyproject.toml                 # Configuration moderne Python
├── requirements.txt               # Dépendances Python (avec psutil)
└── run.py                         # Point d'entrée de l'application
```

**Note importante pour la mise à jour depuis une version < 1.1.0 :**
Avec la version 1.1.0, le système d'authentification a été modifié pour utiliser un nom d'utilisateur au lieu d'une adresse e-mail comme identifiant principal. Si vous mettez à jour depuis une version antérieure, vous **devez supprimer votre ancien fichier de base de données** (par exemple, `instance/educinfo.db`) et réinitialiser la base de données avec `flask reset-db` pour appliquer les nouveaux changements de structure.

## 🚀 Options de Déploiement

EducInfo propose **deux modes de déploiement** selon vos besoins :

### 📦 **Mode Instance Unique** (Simple)
- ✅ **Fichier** : `docker-compose.yml`
- ✅ **Usage** : Développement, test, petites installations
- ✅ **Base de données** : SQLite locale
- ✅ **Démarrage** : `docker-compose up -d`

### 🔗 **Mode Cluster Load Balancé** (Production)
- ✅ **Fichier** : `docker-compose.cluster.yml` 
- ✅ **Usage** : Production, haute disponibilité
- ✅ **Instances** : 2-3 instances EducInfo + Load balancer Nginx
- ✅ **Base de données** : PostgreSQL + Redis partagé
- ✅ **Monitoring** : Prometheus/Grafana optionnel
- ✅ **Démarrage** : `./start-cluster.sh` ou `make cluster`

## Installation et Configuration

### Prérequis
- Python 3.10+ (recommandé 3.12)
- pip et virtualenv
- Redis (optionnel pour cache avancé, **requis pour cluster**)
- Docker (optionnel, pour le déploiement)
- **psutil** (inclus automatiquement pour les métriques système)

### Installation rapide

1. **Cloner le dépôt :**
```bash
# 1. Cloner et installer les dépendances
git clone https://github.com/doalou/educinfo.git
cd educinfo
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows
pip install -r requirements.txt

# 2. Configurer
cp .env.example .env

# 3. Initialiser la base de données
flask init-db
```

6. **Vérification des métriques (optionnel) :**
```bash
# Tester le système de métriques
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, RAM: {psutil.virtual_memory().percent}%')"
```

### Configuration avancée

#### Variables d'environnement principales

```bash
# Configuration de base
FLASK_ENV=development
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///./instance/educinfo.db

# Cache Redis (optionnel)
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=redis

# APIs externes
WEATHER_API_KEY=your-openweather-key
CTS_API_TOKEN=your-cts-token

# Monitoring (optionnel)
PROMETHEUS_ENABLED=true
HEALTH_CHECK_PATH=/health
```

## Utilisation

### Mode Administrateur
Accédez à `/admin` pour gérer le contenu.
- **Utilisateur par défaut** : Créé lors du `flask init-db` (voir logs ou définir via CLI).
- **Métriques** : Visualisez l'état de santé du serveur dans `/admin/metrics`.

### Mode Affichage (TV)
Pour un écran d'affichage dans un hall :
1. Ouvrez le navigateur sur l'URL de l'accueil.
2. Ajoutez `?tv=true` à la fin de l'URL ou cliquez sur le bouton "Mode TV".
3. Passez en plein écran (`F11`).
4. L'écran tournera désormais en autonomie.

---

## 🏗️ Architecture

```
EducInfo/
├── app/
│   ├── blueprints/    # Routes (admin, api, auth, public)
│   ├── models/        # Modèles SQLAlchemy
│   ├── services/      # Logique métier (Météo, Transport, etc.)
│   └── static/        # Assets (CSS optimisé TV, JS)
├── docker/            # Configuration conteneurs
├── scripts/           # Utilitaires de maintenance
└── tests/             # Tests unitaires et d'intégration
```

## 🤝 Contribuer

Les contributions sont bienvenues ! Merci de consulter [CONTRIBUTING.md](CONTRIBUTING.md) (à créer) pour les directives.

1. Forker le projet.
2. Créer une branche (`git checkout -b feature/ma-feature`).
3. Committer (`git commit -am 'Ajout de ma feature'`).
4. Pusher (`git push origin feature/ma-feature`).
5. Ouvrir une Pull Request.

---

## 📄 Licence
### Développement

```bash
# Méthode recommandée avec Flask CLI
export FLASK_APP=run.py
flask run --debug

# Ou directement avec Python
python run.py --debug

# Avec hot-reload et outils de dev
python run.py --host=0.0.0.0 --port=8000 --debug
```

### Accès aux Métriques
- **Dashboard Admin** : `/admin/dashboard` → Section Métriques
- **Page dédiée** : `/admin/metrics` (nécessite login administrateur)
- **Health Check** : `/health` (public)
- **API Métriques** : `/metrics` (si Prometheus activé)

### Production avec Gunicorn

```bash
# Configuration basique
gunicorn --bind 0.0.0.0:5000 --workers 3 run:app

# Configuration optimisée avec monitoring
gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --worker-class sync \
         --max-requests 1000 \
         --timeout 30 \
         --keep-alive 2 \
         --preload \
         run:app
```

### Docker (Recommandé)

#### Déploiement rapide avec docker-compose

```bash
# Créer le fichier .env
cat > .env << EOF
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
SECRET_KEY=your-super-secret-key
WEATHER_API_KEY=your-openweather-key
CTS_API_TOKEN=your-cts-token
REDIS_URL=redis://redis:6379/0
CACHE_TYPE=redis
PROMETHEUS_ENABLED=true
EOF

# Démarrer l'application avec Redis
docker-compose up -d --build

# Voir les logs
docker-compose logs -f

# Accéder à l'application : http://localhost:5000
# Activer le mode TV : http://localhost:5000?tv=true
```

#### Build manuel Docker

```bash
# Build image de production
docker build -f docker/Dockerfile -t educinfo:2.0.0 --target production .

# Build image de développement
docker build -f docker/Dockerfile -t educinfo:dev --target development .

# Lancer en production
docker run -d \
  --name educinfo-app \
  -p 5000:5000 \
  -v educinfo_data:/app/instance \
  -v educinfo_logs:/app/logs \
  --env-file .env \
  educinfo:2.0.0
```

## 🔗 Déploiement en Cluster Load Balancé

Pour la **production** et la **haute disponibilité**, EducInfo propose un mode cluster avec load balancing automatique.

### 🏗️ Architecture Cluster

```
┌─────────────────┐
│   Load Balancer │  ← Nginx (Port 80/443)
│     (Nginx)     │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼───┐   ┌───▼───┐   ┌───────┐
│ App-1 │   │ App-2 │   │ App-3 │  ← Instances EducInfo
│:5000  │   │:5000  │   │:5000  │    (Optionnelle)
└───┬───┘   └───┬───┘   └───┬───┘
    │           │           │
    └─────┬─────┴─────┬─────┘
          │           │
    ┌─────▼───┐   ┌───▼────┐
    │  Redis  │   │ PostGre│  ← Services partagés
    │ (Cache) │   │   SQL  │
    └─────────┘   └────────┘
```

### 🚀 Démarrage Rapide du Cluster

```bash
# Démarrage basique (2 instances + load balancer)
./start-cluster.sh
# ou
make cluster

# Démarrage complet (3 instances + monitoring Prometheus/Grafana)
./start-cluster.sh --full --monitoring
# ou
make cluster-full

# Aide et options disponibles
./start-cluster.sh --help
```

### 📊 Surveillance du Cluster

```bash
# Statut du cluster
make cluster-status
./start-cluster.sh --status

# Logs en temps réel
make cluster-logs
./start-cluster.sh --logs

# Logs d'un service spécifique
./start-cluster.sh --logs nginx
./start-cluster.sh --logs educinfo-1

# Arrêt du cluster
make cluster-stop
./start-cluster.sh --stop
```

### 🔧 Configuration du Cluster

1. **Copier la configuration :**
```bash
# Utiliser le template de configuration cluster
cp .env.cluster.example .env.cluster
nano .env.cluster
```

2. **Variables importantes :**
```env
# Redis obligatoire pour le cluster
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=educinfo_redis_2023

# PostgreSQL pour la production
POSTGRES_URL=postgresql://educinfo:educinfo_password@db:5432/educinfo

# Métriques cluster
METRICS_INSTANCE_TTL=300
METRICS_UPDATE_INTERVAL=60
```

3. **Démarrage personnalisé :**
```bash
# Cluster avec monitoring
docker-compose -f docker-compose.cluster.yml --profile monitoring up -d

# Cluster complet (3 instances)
docker-compose -f docker-compose.cluster.yml --profile full-cluster up -d

# Scaling manuel
docker-compose -f docker-compose.cluster.yml up -d --scale educinfo-2=2
```

### 📈 Métriques et Monitoring

Le mode cluster offre des métriques avancées :

- **Interface Admin** : `/admin/metrics` → Section "Cluster Load Balancing"
- **Health Check Load Balancer** : `http://localhost/health`
- **Métriques Nginx** : `http://localhost/nginx-status` (réseau local)
- **Prometheus** (si activé) : `http://localhost:9090`
- **Grafana** (si activé) : `http://localhost:3000` (admin/admin)

### 🛠️ Gestion Avancée

```bash
# Mise à jour rolling (zero downtime)
./start-cluster.sh --scale educinfo-1=0  # Désactiver instance 1
docker-compose -f docker-compose.cluster.yml build educinfo-1  # Rebuild
./start-cluster.sh --scale educinfo-1=1  # Réactiver instance 1

# Backup/Restauration
docker-compose -f docker-compose.cluster.yml exec db pg_dump -U educinfo educinfo > backup.sql
docker-compose -f docker-compose.cluster.yml exec -T db psql -U educinfo educinfo < backup.sql

# Redémarrage complet
./start-cluster.sh --restart
```

### 📋 Avantages du Mode Cluster

- ✅ **Haute disponibilité** : Pas d'interruption si une instance tombe
- ✅ **Performance** : Répartition de charge automatique
- ✅ **Monitoring** : Métriques agrégées de toutes les instances
- ✅ **Scalabilité** : Ajout/suppression d'instances à chaud
- ✅ **Production-ready** : PostgreSQL + Redis + monitoring intégré

📖 **Documentation complète** : Voir `docs/DEPLOYMENT_CLUSTER.md` pour tous les détails.

## Commandes CLI Avancées

### Gestion de la base de données

```bash
# Initialisation complète
flask init-db --admin-username admin --admin-password secretpass --cts-token your-token

# Réinitialisation (ATTENTION: efface tout)
flask reset-db

# Migration de la base de données
flask db init
flask db migrate -m "Description du changement"
flask db upgrade
```

### Gestion des utilisateurs

```bash
# Créer un utilisateur standard
flask add-user --username john --password securepass

# Créer un administrateur
flask add-user --username admin --password adminpass --admin

# Générer un code d'urgence pour reset admin
flask admin generate-emergency-code
```

### Données de démonstration

```bash
# Ajouter des données de test
flask add-demo-data
```

## Monitoring et Santé de l'Application

### Endpoints de monitoring

- **Health Check :** `GET /health`
- **Métriques Prometheus :** `GET /metrics` (si activé)
- **API Status :** `GET /api/version`

### Health Check Response
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": 1640995200,
  "database": "ok",
  "cache": "ok",
  "metrics": "available"
}
```

## API REST

EducInfo expose une API REST complète :

```bash
# Informations générales
GET /api/version

# Données de l'application
GET /api/absences      # Absences des professeurs
GET /api/events        # Événements à venir
GET /api/menu          # Menu de la cantine
GET /api/weather       # Données météo
GET /api/transports    # Horaires de transport
```

## Tests et Qualité du Code

### Exécution des tests

```bash
# Tests complets avec coverage
pytest --cov=app --cov-report=html

# Tests spécifiques
pytest tests/services/test_weather_service.py -v

# Tests d'intégration uniquement
pytest -m integration
```

### Outils de qualité

```bash
# Tests automatisés
pytest

# Coverage
pytest --cov=app --cov-report=html

# Linting simple (si installé)
flake8 app/ tests/ --max-line-length=100
```

## Dépannage et Maintenance

### Métriques Système
```bash
# Vérifier l'installation de psutil
python -c "import psutil; print('psutil OK:', psutil.version_info)"

# Tester les métriques manuellement
python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'RAM: {psutil.virtual_memory().percent}%')
print(f'Disque: {psutil.disk_usage(\"/\").percent}%')
"

# Vérifier l'accès aux métriques admin (nécessite login)
curl -b cookies.txt http://localhost:5000/admin/metrics
```

### Problèmes Courants
- **Métriques indisponibles** : Vérifier l'installation de psutil
- **Erreurs de permissions** : S'assurer que l'utilisateur peut lire les infos système
- **Performance lente** : Activer le cache Redis pour améliorer les performances
- **Données de test** : Utiliser `flask add-demo-data` pour populer la base

### Logs et Debugging
```bash
# Activer le mode debug
export FLASK_ENV=development
flask run --debug

# Voir les logs en temps réel
tail -f logs/app.log

# Tester la connectivité API
curl http://localhost:5000/health
```

Consultez `INSTALLATION_METRICS.md` pour un guide détaillé du système de métriques.

## Fonctionnalités

### 🎯 Fonctionnalités principales
- **Dashboard administrateur** : Gestion complète des données pour les responsables
- **Affichage temps réel** : Mise à jour automatique des informations sur écrans
- **Mode TV exclusif** : Interface spécialement conçue pour télévisions et écrans muraux
- **Mode sombre** : Interface adaptable automatiquement selon l'éclairage
- **Authentification sécurisée** : Protection des données sensibles côté administration
- **Cache intelligent** : Performance optimisée avec Redis pour affichage fluide

### 📺 Mode TV Spécialisé
- **Interface épurée** : Design minimal et lisible à distance
- **Auto-refresh** : Données mises à jour automatiquement
- **Polices XL** : Texte lisible depuis l'autre bout de la pièce
- **Contrôles simples** : Boutons Mode TV et Plein écran
- **Thème adaptatif** : Couleurs contrastées pour écrans larges

### 📊 Monitoring et observabilité
- **Métriques système temps réel** : CPU, RAM, disque avec psutil
- **Métriques base de données** : Compteurs automatiques des entités
- **Dashboard admin moderne** : Interface graphique avec barres de progression
- **Health checks** : Surveillance de la santé applicative
- **Cache monitoring** : Status et performance du système de cache
- **Logs structurés** : Traçabilité complète des actions
- **Métriques Prometheus** : Suivi des performances (optionnel)
- **Documentation complète** : Guide d'installation et dépannage

### 🔧 Administration
- **Gestion des utilisateurs** : Création et administration des comptes
- **Configuration dynamique** : Paramétrage en temps réel
- **Import/Export** : Sauvegarde et restauration des données
- **Audit trail** : Traçabilité des modifications

## Performance et Optimisation

### Cache Redis
- **Données météo** : Cache 30 minutes
- **Données transport** : Cache 1 minute
- **Données statiques** : Cache 24 heures
- **Fallback intelligent** : Dégradation gracieuse

### Optimisations Docker
- **Multi-stage build** : Images optimisées par environnement
- **Sécurité** : Utilisateur non-root, minimal attack surface
- **Performance** : Layers optimisés, dépendances cached

### Mode TV Performance
- **Rendu optimisé** : CSS spécialisé pour grandes résolutions
- **JavaScript efficient** : Gestion mémoire optimisée
- **Auto-refresh intelligent** : Refresh différencié par type de données

## Sécurité

### Mesures de sécurité implémentées
- **CSRF Protection** : Protection contre les attaques cross-site
- **Security Headers** : Content Security Policy, HSTS, X-Frame-Options
- **Input Validation** : Validation et sanitisation des entrées
- **Session Security** : Sessions sécurisées avec timeout
- **Rate Limiting** : Protection contre les attaques par déni de service

## Déploiement en Production

### Checklist de production

1. **Configuration**
   - [ ] Variables d'environnement sécurisées
   - [ ] Clé secrète unique et forte
   - [ ] Base de données externe (PostgreSQL/MySQL)
   - [ ] Redis pour le cache

2. **Sécurité**
   - [ ] HTTPS activé
   - [ ] Certificats SSL valides
   - [ ] Firewall configuré
   - [ ] Monitoring activé

3. **Performance**
   - [ ] Reverse proxy (Nginx/Apache)
   - [ ] Load balancer si nécessaire
   - [ ] CDN pour les assets statiques
   - [ ] Monitoring des performances

### Configuration Nginx (exemple)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /path/to/educinfo/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Optimisation pour TV en production

```nginx
# Règles spéciales pour les installations TV
location ~* \.(css|js)$ {
    expires 1h;  # Cache court pour permettre les mises à jour
    add_header Cache-Control "public, must-revalidate";
}

# Support WebSocket pour auto-refresh temps réel (optionnel)
location /socket.io/ {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_pass http://127.0.0.1:5000;
}
```

## 📁 Architecture des Fichiers Docker Compose

EducInfo utilise **deux fichiers Docker Compose distincts** pour s'adapter à différents besoins :

### 📦 `docker-compose.yml` (Instance Unique)
```yaml
# Architecture simple
services:
  educinfo:        # 1 instance EducInfo
    ports: ["5000:5000"]
    volumes: ["./instance", "./logs"]
```

**Utilisation :**
- ✅ **Développement** et prototypage
- ✅ **Petites installations** (1-50 utilisateurs)
- ✅ **Tests** et validation
- ✅ **Démarrage** : `docker-compose up -d`

### 🔗 `docker-compose.cluster.yml` (Production Load Balancé)
```yaml
# Architecture cluster
services:
  nginx:           # Load balancer
  educinfo-1:      # Instance 1
  educinfo-2:      # Instance 2  
  educinfo-3:      # Instance 3 (optionnelle)
  redis:           # Cache partagé
  db:              # PostgreSQL
  prometheus:      # Monitoring (optionnel)
  grafana:         # Dashboard (optionnel)
```

**Utilisation :**
- ✅ **Production** haute disponibilité
- ✅ **Charge élevée** (50+ utilisateurs)
- ✅ **Monitoring** avancé
- ✅ **Démarrage** : `./start-cluster.sh` ou `make cluster`

### 🎯 Comparaison Rapide

| Aspect | Instance Unique | Cluster Load Balancé |
|--------|----------------|---------------------|
| **Fichier** | `docker-compose.yml` | `docker-compose.cluster.yml` |
| **Instances** | 1 EducInfo | 2-3 EducInfo + Nginx LB |
| **Base de données** | SQLite locale | PostgreSQL partagée |
| **Cache** | Optionnel | Redis obligatoire |
| **Monitoring** | Basic health check | Prometheus + Grafana |
| **Complexité** | Simple | Avancée |
| **Cas d'usage** | Dev, test, petites installations | Production, haute disponibilité |
| **Commande** | `docker-compose up -d` | `./start-cluster.sh` |

### 🔄 Migration Instance → Cluster

Pour passer d'une instance unique au cluster :

```bash
# 1. Sauvegarder les données
docker-compose exec educinfo flask backup-data

# 2. Arrêter l'instance unique
docker-compose down

# 3. Configurer le cluster
cp .env.cluster.example .env.cluster

# 4. Démarrer le cluster
./start-cluster.sh

# 5. Restaurer les données
./start-cluster.sh --logs educinfo-1  # Vérifier démarrage
# Puis restaurer via interface admin
```

Cette architecture **double** permet une **évolutivité** maximale selon les besoins ! 🚀

## Contribuer

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/amazing-feature`)
3. **Commit** les changements (`git commit -m 'Add amazing feature'`)
4. **Push** vers la branche (`git push origin feature/amazing-feature`)
5. **Ouvrir** une Pull Request

### Standards de développement
- Tests unitaires requis pour les nouvelles fonctionnalités
- Documentation des APIs avec docstrings
- Respect des conventions de nommage Python

## Roadmap

### ✅ Version 2.0.0 (Juin 2025) - En cours
- [x] Système de métriques système complet avec psutil
- [x] Interface d'administration redesignée pour la gestion
- [x] Dashboard métriques avec visualisations
- [x] Documentation complète du monitoring
- [x] Amélioration des performances et stabilité pour affichage TV
- [ ] Finalisation optimisations mode TV

### Version 1.3.0 (Août 2025)
- [ ] Notifications visuelles pour les écrans TV
- [ ] Widgets configurables pour différents types d'écrans
- [ ] Dashboard analytics avec graphiques historiques
- [ ] Alerting automatique sur seuils de métriques
- [ ] Export des métriques et rapports (CSV, JSON, PDF)
- [ ] Support multi-résolutions d'écrans TV

### Version 1.4.0 (Octobre 2025)
- [ ] Support multi-établissements avec métriques centralisées
- [ ] Intégration calendrier externe (Google, Outlook)
- [ ] Thèmes personnalisables par établissement
- [ ] Support écrans tactiles pour l'administration
- [ ] Mode kiosque avancé pour écrans publics

### Version 1.5.0 (Janvier 2026)
- [ ] Intelligence artificielle pour optimisation d'affichage
- [ ] API WebSocket pour données temps réel
- [ ] Gestion avancée de contenu multimédia
- [ ] Intégration systèmes de gestion scolaire (ENT)
- [ ] Système de sauvegarde et synchronisation automatique

## Support et Documentation

- **Issues :** [GitHub Issues](https://github.com/doalou/educinfo/issues)
- **Discussions :** [GitHub Discussions](https://github.com/doalou/educinfo/discussions)
- **Email :** contact@doalo.fr

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Remerciements

- [Flask](https://flask.palletsprojects.com/) - Framework web moderne
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM Python de référence
- [Tailwind CSS](https://tailwindcss.com/) - Framework CSS utilitaire
- [Redis](https://redis.io/) - Base de données en mémoire haute performance
- [Prometheus](https://prometheus.io/) - Système de monitoring
- [Docker](https://www.docker.com/) - Plateforme de conteneurisation

---

**EducInfo v2.0.0** - Développé avec ❤️ pour l'éducation
*Système d'affichage spécialisé pour écrans de télévision dans les établissements scolaires !* 📺🏫
