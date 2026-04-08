# Scripts EducInfo

Ce dossier contient les scripts utilitaires pour EducInfo v2.0.0.

## 📋 Scripts disponibles

### 🔧 Initialisation

#### `setup.sh` - Initialisation complète
Script d'initialisation générale pour configurer EducInfo de zéro.

```bash
# Installation complète interactive
./scripts/setup.sh

# Installation développement
./scripts/setup.sh --dev

# Installation minimale
./scripts/setup.sh --minimal

# Vérification des prérequis seulement
./scripts/setup.sh --check-only
```

**Options :**
- `-h, --help` : Affiche l'aide
- `--dev` : Configuration développement complète
- `--cluster` : Configuration cluster (Docker)
- `--minimal` : Installation minimale
- `--check-only` : Vérifie les prérequis uniquement

### 🖥️ Développement

#### `dev.sh` - Script de développement
Script principal pour le développement local d'EducInfo.

```bash
# Démarrage simple
./scripts/dev.sh

# Avec options
./scripts/dev.sh --port 8000 --init
./scripts/dev.sh --reset --test
./scripts/dev.sh --install
```

**Options :**
- `-h, --help` : Affiche l'aide
- `-p, --port PORT` : Port d'écoute (défaut: 5000)
- `--host HOST` : Host d'écoute (défaut: 0.0.0.0)
- `--init` : Initialise la base de données
- `--reset` : Remet à zéro la base de données
- `--install` : Installe les dépendances
- `--test` : Lance les tests

### 🔄 Load Balancing

#### `cluster.sh` - Gestion du cluster
Script pour démarrer et gérer EducInfo en mode cluster load balancé.

```bash
# Démarrage cluster basique (2 instances)
./scripts/cluster.sh

# Cluster complet avec monitoring
./scripts/cluster.sh --full --monitoring

# Gestion du cluster
./scripts/cluster.sh --stop
./scripts/cluster.sh --restart
./scripts/cluster.sh --status
./scripts/cluster.sh --logs nginx
```

**Options :**
- `-h, --help` : Affiche l'aide
- `-f, --full` : Démarre avec 3 instances (au lieu de 2)
- `-m, --monitoring` : Active Prometheus + Grafana
- `-d, --dev` : Mode développement avec logs détaillés
- `--stop` : Arrête le cluster
- `--restart` : Redémarre le cluster
- `--status` : Affiche le statut du cluster
- `--logs [service]` : Affiche les logs
- `--scale instances=N` : Scale le nombre d'instances

### 🧪 Tests

#### `test-docker.sh` - Tests Docker
Script de test pour vérifier le bon fonctionnement d'EducInfo dans Docker.

```bash
# Utilisation dans un conteneur Docker
docker run --rm educinfo ./scripts/test-docker.sh
```

Ce script vérifie :
- Installation de Python et Flask
- Configuration FLASK_APP
- Structure de l'application
- Initialisation de la base de données
- Démarrage de l'application

## 🚀 Utilisation rapide

### Première installation
```bash
# Installation complète interactive
./scripts/setup.sh

# Installation développement automatique
./scripts/setup.sh --dev
```

### Développement local
```bash
# Installation et démarrage
./scripts/dev.sh --install --init

# Développement quotidien
./scripts/dev.sh
```

### Déploiement cluster
```bash
# Cluster de base
./scripts/cluster.sh

# Cluster complet avec monitoring
./scripts/cluster.sh --full --monitoring
```

### Tests
```bash
# Tests locaux
./scripts/dev.sh --test

# Tests Docker
docker run --rm educinfo ./scripts/test-docker.sh
```

## 📝 Notes importantes

1. **Permissions** : Assurez-vous que les scripts sont exécutables :
   ```bash
   chmod +x scripts/*.sh
   ```

2. **Dépendances** :
   - `dev.sh` : Python 3, pip
   - `cluster.sh` : Docker, Docker Compose
   - `test-docker.sh` : Utilisation dans un conteneur Docker

3. **Variables d'environnement** : 
   - Les scripts utilisent les fichiers `.env` et `.env.cluster.example`
   - Copiez et modifiez ces fichiers selon vos besoins

4. **Logs** : 
   - Tous les scripts utilisent un système de logging coloré
   - Les erreurs sont clairement identifiées

## 🔧 Personnalisation

Vous pouvez modifier les variables par défaut en éditant les scripts :
- Ports d'écoute
- Configurations Docker
- Paramètres de base de données
- Options de monitoring

## 🆘 Dépannage

- **Permission denied** : Vérifiez les permissions avec `chmod +x`
- **Docker non trouvé** : Installez Docker et Docker Compose
- **Python non trouvé** : Installez Python 3
- **Port occupé** : Changez le port avec `--port` 