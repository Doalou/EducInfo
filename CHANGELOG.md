# Changelog

Toutes les evolutions notables du projet seront documentees ici.

Le format s'inspire de Keep a Changelog et le versioning suit SemVer.

## [3.0.0] - 2026-07-13

### Refonte
- Nouvelle architecture Flask organisée par domaines : affichage, contenu, paramètres et authentification.
- Nouvelle identité de signalétique publique pour l'écran TV et administration assortie, en CSS et JavaScript locaux sans CDN.
- API interne agrégée `GET /internal/display` avec états de fraîcheur météo et transport.
- Rôles `admin` et `editor`, invalidation des sessions et récupération du mot de passe uniquement en CLI.
- Documentation complète de l'installation, de l'exploitation, des sauvegardes, de l'architecture et du dépannage.
- Mode sombre configurable pour l'écran public et amélioration de la lisibilité interne des modules.
- Couleurs officielles des lignes CTS récupérées depuis `lines-discovery` avec cache de 24 heures.

### Exploitation
- Déploiement recentré sur une instance Docker avec SQLite et migrations Alembic.
- Dépendances de production verrouillées et migrations embarquées pour rendre la CLI installable autonome.
- Suppression du mode cluster, de Redis, PostgreSQL, Nginx, Prometheus et Grafana.
- Configuration de production stricte, health checks séparés et journalisation sur stdout.

### Sécurité et qualité
- Mise à jour vers Flask 3.1.3 et suppression des secrets dans les URL, la base et les journaux.
- Neutralisation des erreurs des services externes afin qu'aucune clé ne puisse apparaître dans l'API.
- Gestion des rôles, de l'activation et des mots de passe depuis l'administration.
- CSP sans scripts ou styles inline, mutations POST protégées par CSRF.
- CI unifiée avec Ruff, pytest, couverture, audit des dépendances et smoke test Docker.

## [2.0.0] - 2026-07-13

### Sécurité
- Suppression du mot de passe admin en dur (`admin123`) dans toute la codebase : config, CLI, scripts, Docker et fichiers d'environnement.
- Generation automatique d'un mot de passe securise via `secrets.token_urlsafe` a chaque initialisation ou reinitialisation.
- Protection des routes de diagnostic (`/debug/weather`, `/debug/transport`) deplacees derriere `@login_required` dans le blueprint admin.
- Suppression des mots de passe Redis et PostgreSQL en dur dans les fichiers d'exemple ; remplacement par des placeholders a renseigner.
- Suppression de `SECRET_KEY` par defaut dans `docker-compose.yml` (champ laisse vide pour forcer la definition).
- Remplacement des `except:` generiques par `except Exception:` dans les services et utilitaires.

### Interface
- Refonte visuelle globale : suppression du glassmorphisme, des gradients omnipresents, des animations decoratives (glow, float, bounce, barre arc-en-ciel).
- Nouvelle direction sobre et lisible : fonds opaques, bordures fines, ombres subtiles, couleurs plates sur les headers de cartes.
- Palette recentree sur le bleu (`#2563eb`) comme couleur primaire, en remplacement de l'indigo/violet.
- Sidebar admin simplifiee : items compacts, icones carrees, suppression du logo etoile et du label "Dashboard Admin v1.2.0".
- Allègement typographique : tailles et graisses reduites pour une lecture plus naturelle a distance.
- Nouvelle composition de l'ecran public avec grille editorialisee, cartes plus lisibles et hierarchie de lecture renforcee.
- Page de connexion epuree et coherente avec le nouveau style.
- Externalisation du style de la page publique dans `app/static/css/tv-mode.css`.
- Nettoyage de `style.css` : suppression des keyframes inutilisees, effets de particules, shimmer de badges.
- Harmonisation de `darkmode.css` avec la nouvelle palette et amelioration du contraste des alertes en mode sombre.

### Infrastructure et Docker
- Dockerfile optimise : suppression de `dos2unix` (fins de ligne gerees par `.gitattributes`), nombre de workers Gunicorn auto-calcule selon les CPU.
- Suppression de la directive `VOLUME` du Dockerfile (geree par docker-compose).
- Separation des dependances dev dans `requirements-dev.txt` ; suppression de pytest/black/flake8 du `requirements.txt` de production.
- Gunicorn ajoute directement dans `requirements.txt` au lieu d'une installation separee dans le Dockerfile.
- Port par defaut du docker-compose passe de `5000:5000` a `5001:5000` pour eviter le conflit avec AirPlay Receiver sur macOS.
- Mots de passe cluster (`POSTGRES_PASSWORD`, `REDIS_PASSWORD`) injectes via variables d'environnement avec fallback `changeme`.
- Mot de passe Redis configure dynamiquement au demarrage via `--requirepass` au lieu d'un `requirepass` statique dans `redis.conf`.

### Technique
- Passage de la version applicative a `2.0.0` dans la configuration, pyproject.toml, Dockerfile, README, scripts et fichiers d'environnement.
- Correction des appels `db.session.execute('SELECT 1')` en `db.session.execute(text('SELECT 1'))` pour compatibilite SQLAlchemy 2.x.
- Ajout de l'import `sqlalchemy.text` dans `extensions.py` et `api/routes.py`.
- Route de diagnostic meteo/transport deplacee de `public/routes.py` vers `admin/routes.py` avec authentification obligatoire.
- Message de reinitialisation d'urgence mis a jour pour ne plus mentionner un mot de passe fixe.

### CI et documentation
- Mise a jour des actions GitHub : `docker/build-push-action` `v6.18.0`, `docker/setup-buildx-action` `v3.11.1`, `docker/login-action` `v3.6.0`, `docker/metadata-action` `v5.8.0`, `sigstore/cosign-installer` `v4.0.0`.
- README et documentation alignes sur la version 2.0.0.

## [1.4.0] - 2025-12-16

### Added
- Refonte complète de l'interface d'administration ("Obsidian Glass").
- Nouvelle barre de navigation latérale (Sidebar) pour une navigation fluide par sections.
- Tableau de bord restructuré en sections : Overview, Content, Configuration, System.
- Système de notifications toast modernes.
- Métriques système détaillées avec graphiques dynamiques (Chart.js).
- Interface de diagnostic utilisateurs améliorée avec analyse de sécurité.
- Page de réinitialisation d'urgence remise à neuf.
- Support mobile complet avec sidebar responsive.
- Widgets de prévisualisation live pour la Météo et les Transports.

### Changed
- Passage à Tailwind CSS pour l'ensemble de la console d'administration.
- Amélioration de la réactivité et de l'accessibilité du dashboard.

## [1.3.1] - 2025-12-15

### Added
- Refonte du système météo avec données enrichies (AQI, UV, Sunrise/Sunset).
- Nouveau widget météo moderne sur la page d'accueil.
- Système de cache météo intelligent avec bouton de rafraîchissement manuel.

## [1.2.1] - 2025-06-11

### Fixed
- Correctifs mineurs post-release 1.2.0.

## [1.2.0] - 2025-06-11

### Added
- Ajout du mode Cluster (Load Balancing).
- Système de métriques avancé (psutil).
- Support Multi-stage Docker builds.
- Mode TV amélioré.
