# EducInfo

EducInfo est un écran d’information auto-hébergé pour les établissements scolaires. Il regroupe sur une vue conçue pour une télévision les absences hebdomadaires, le menu de cantine, les événements, la météo et les prochains passages du réseau CTS.

La version 3 privilégie une exploitation simple : une application Flask, une base SQLite persistante et un seul conteneur Docker. Aucun CDN, service Redis, serveur PostgreSQL ou proxy web n’est nécessaire.

## Fonctionnalités

- écran public lisible à distance, optimisé pour un affichage 16:9 en continu ;
- absences organisées par semaine type, du lundi au samedi ;
- menu du jour avec catégories communes au stockage, aux formulaires et à l’affichage ;
- événements à venir sur 30 jours ;
- météo OpenWeather avec cache et conservation de la dernière donnée fiable ;
- prochains passages CTS avec filtre bus ou tram ;
- couleurs officielles des lignes CTS récupérées par `lines-discovery` et mises en cache ;
- thème clair ou sombre de l'écran, sélectionnable depuis l'administration ;
- administration séparée en contenu, configuration et comptes ;
- rôles `editor` et `admin` ;
- API JSON interne, même origine, réservée à l’écran EducInfo ;
- migrations Alembic, health checks et commande locale de récupération du compte admin ;
- interface entièrement locale, CSP stricte et mutations protégées par CSRF.

## Aperçu fonctionnel

L’écran public est accessible sans authentification. Il interroge automatiquement `GET /internal/display` toutes les 60 secondes, sans cache navigateur, et se rafraîchit immédiatement lorsqu’il revient au premier plan. Il conserve une interface exploitable lorsque les services externes sont lents ou indisponibles.

L’administration nécessite une connexion :

| Rôle | Contenus | Paramètres | Comptes |
|---|:---:|:---:|:---:|
| Éditeur | Oui | Non | Non |
| Administrateur | Oui | Oui | Oui |

Les contenus comprennent les absences, les événements et les menus. Les clés OpenWeather et CTS ne sont jamais lisibles ou modifiables depuis l’interface : elles restent dans l’environnement du serveur.

## Prérequis

Pour une installation de production :

- Docker Engine 24 ou une version plus récente ;
- Docker Compose v2 ;
- un port TCP accessible aux écrans de l’établissement, `5001` par défaut.

Pour le développement local, Python 3.13 est requis.

## Installation avec Docker

1. Copier la configuration d’exemple :

   ```bash
   cp .env.example .env
   ```

2. Générer une clé de session persistante :

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. Reporter le résultat dans `SECRET_KEY` du fichier `.env`, puis définir au minimum `ADMIN_PASSWORD` avec un mot de passe long.

4. Construire et démarrer EducInfo :

   ```bash
   docker compose up --build -d
   docker compose logs -f educinfo
   ```

5. Ouvrir les interfaces :

   - écran public : `http://localhost:5001/`
   - administration : `http://localhost:5001/auth/login`
   - état de l’application : `http://localhost:5001/health/ready`

Depuis un autre appareil du réseau, remplacer `localhost` par l’adresse IP ou le nom DNS de la machine Docker, par exemple `http://192.168.1.22:5001`.

Au premier démarrage, les migrations sont appliquées automatiquement. Si `ADMIN_PASSWORD` est vide, un mot de passe aléatoire est affiché une seule fois dans les logs. La valeur de `ADMIN_PASSWORD` sert uniquement à créer le premier compte : modifier ensuite `.env` ne remplace pas le mot de passe d’un compte existant.

## Configuration

Les variables sont lues par `compose.yml` depuis `.env`.

| Variable | Obligatoire | Défaut | Description |
|---|:---:|---|---|
| `SECRET_KEY` | production | — | Clé persistante utilisée pour signer les sessions et les jetons CSRF. |
| `APP_PORT` | non | `5001` | Port HTTP publié sur la machine hôte. |
| `SESSION_COOKIE_SECURE` | non | `false` | Utiliser `true` uniquement lorsque le site est servi en HTTPS. |
| `ADMIN_USERNAME` | non | `admin` | Identifiant créé lors de la toute première initialisation. |
| `ADMIN_PASSWORD` | recommandé | généré | Mot de passe du premier administrateur. Minimum conseillé : 16 caractères. |
| `WEATHER_API_KEY` | non | vide | Clé serveur OpenWeather. Sans clé, la météo est indiquée indisponible. |
| `WEATHER_CITY` | non | `Strasbourg` | Ville météo initiale. Elle peut ensuite être changée dans l’administration. |
| `CTS_API_TOKEN` | non | vide | Jeton serveur de l’API CTS Strasbourg. |
| `DEMO_MODE` | non | `false` | Autorise explicitement les données météo de démonstration. Ne pas activer en production. |

Les variables avancées `DATABASE_URL`, `INSTANCE_PATH` et `CTS_BASE_URL` sont disponibles pour les tests et développements spécifiques. La seule base officiellement supportée en production est SQLite.

## Exploitation courante

### Démarrer, arrêter et consulter les logs

```bash
docker compose up -d
docker compose stop
docker compose logs --tail 100 educinfo
docker compose ps
```

### Mettre à jour l’image locale

```bash
docker compose build --pull educinfo
docker compose up -d
```

L’entrypoint valide la configuration, applique les migrations puis démarre Gunicorn avec un worker `gthread`. Le processus applicatif s’exécute avec l’utilisateur non privilégié `educinfo`.

### Réinitialiser un mot de passe administrateur

La récupération ne passe jamais par une URL web. La commande suivante génère un nouveau mot de passe, l’affiche une seule fois et invalide toutes les sessions du compte :

```bash
docker compose exec educinfo educinfo admin reset-password --username admin
```

### Sauvegarder SQLite

La base est stockée dans le volume Docker `educinfo_data`, sous `/app/instance/educinfo.db`. Pour obtenir une copie cohérente simple :

```bash
docker compose stop educinfo
docker compose cp educinfo:/app/instance/educinfo.db ./educinfo-backup.db
docker compose start educinfo
```

Conserver également une copie du fichier `.env` dans un emplacement sécurisé, séparément de la base. Ne jamais le committer.

Pour restaurer une sauvegarde, arrêter le service, copier la base vers `/app/instance/educinfo.db`, puis redémarrer. Une sauvegarde v2 peut être conservée à titre d’archive, mais EducInfo 3 ne réalise aucune migration automatique des données v2.

## Health checks

Deux endpoints volontairement minimaux sont exposés :

- `GET /health/live` confirme que le processus Flask répond et retourne la version ;
- `GET /health/ready` vérifie la connexion SQLite et la révision Alembic attendue.

Une réponse `503` de `/health/ready` signifie généralement que la base n’est pas accessible ou qu’une migration n’a pas été appliquée. Consulter alors `docker compose logs educinfo`.

## API interne

`GET /internal/display` fournit en une seule réponse les informations nécessaires à l’écran :

```json
{
  "generated_at": "2026-07-13T08:00:00+00:00",
  "site": {"name": "EducInfo", "theme": "dark"},
  "widgets": {"weather": true, "menu": true, "transport": false},
  "absences": {"lundi": [], "mardi": []},
  "events": [],
  "menu": [],
  "weather": {"status": "fresh", "updated_at": "…", "data": {}},
  "transport": {
    "status": "fresh",
    "data": {
      "arrivals": [{"line": "A", "line_color": "#E10D19", "line_text_color": "#FFFFFF"}]
    }
  }
}
```

Les sources externes utilisent les états `fresh`, `stale`, `unavailable`, `disabled` ou `demo`. Les métadonnées de lignes CTS sont conservées 24 heures et les passages 45 secondes. Une erreur distante n’est jamais renvoyée telle quelle afin d’éviter l’exposition accidentelle d’un token. Cet endpoint est public en lecture seule, de même origine, et ne constitue pas une API publique stable pour des intégrations tierces.

## Développement

### Installation

Sous Linux ou macOS :

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
export APP_ENV=development
export SECRET_KEY=development-only
.venv/bin/flask --app run:app db upgrade
.venv/bin/educinfo admin ensure
.venv/bin/flask --app run:app run --debug
```

Sous PowerShell :

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
$env:APP_ENV = "development"
$env:SECRET_KEY = "development-only"
.venv\Scripts\python.exe -m flask --app run:app db upgrade
.venv\Scripts\educinfo.exe admin ensure
.venv\Scripts\python.exe -m flask --app run:app run --debug
```

### Qualité

```bash
ruff check .
ruff format --check .
pytest
pip-audit --requirement requirements.lock
```

La CI exige au moins 80 % de couverture, vérifie que `requirements.lock` correspond à `pyproject.toml`, construit l’image de production et exécute un smoke test Docker.

Pour régénérer le verrou de production avec Python 3.13 :

```bash
python -m piptools compile pyproject.toml --output-file=requirements.lock --strip-extras
```

`pyproject.toml` reste l’unique fichier à modifier manuellement pour les dépendances. `requirements.lock` est un artefact généré utilisé par Docker.

## Architecture

```text
app/
├── blueprints/
│   ├── auth/          connexion et déconnexion
│   ├── content/       absences, événements et menus
│   ├── display/       écran public et API interne
│   └── settings/      configuration et comptes
├── integrations/      cache, OpenWeather et CTS
├── migrations/        schéma Alembic embarqué
├── models/            modèles SQLAlchemy
├── services/          assemblage des données d’affichage
├── static/            CSS, JavaScript et icônes locaux
└── templates/         vues Jinja publiques et administratives
```

La factory `create_app` initialise explicitement les extensions et services. Les adaptateurs météo et transport ne lisent leurs secrets que depuis la configuration serveur. `DisplayService` assemble les données métier et les états des intégrations pour l’écran.

## Sécurité

- `SECRET_KEY` est obligatoire en production ;
- les cookies de session sont `HttpOnly` et `SameSite=Lax` ;
- les opérations de modification et la déconnexion utilisent POST avec CSRF ;
- les redirections après connexion sont limitées aux URL locales ;
- la CSP n’autorise ni CDN ni script ou style inline ;
- les changements de mot de passe et de rôle invalident les sessions existantes ;
- les clés OpenWeather et CTS ne sont ni stockées dans SQLite, ni affichées dans l’administration ;
- le conteneur s’exécute sans privilèges root.

En cas d’exposition sur Internet, placer EducInfo derrière un reverse proxy HTTPS, activer `SESSION_COOKIE_SECURE=true` et restreindre l’administration au réseau ou au VPN de l’établissement.

## Dépannage

### Le site ne répond pas

```bash
docker compose ps
docker compose logs --tail 100 educinfo
curl http://localhost:5001/health/ready
```

Vérifier `APP_PORT`, le pare-feu de la machine et l’absence d’un autre service sur ce port. Depuis le réseau local, utiliser l’adresse IP de la machine Docker plutôt que `localhost`.

### La connexion admin échoue après modification de `.env`

`ADMIN_PASSWORD` n’écrase pas un compte déjà présent dans le volume persistant. Utiliser la commande `educinfo admin reset-password` décrite plus haut.

### La météo ou les transports sont indisponibles

Vérifier la présence des clés dans `.env`, redémarrer le conteneur après leur modification, puis consulter leur état dans **Administration → Paramètres**. EducInfo ne présente jamais une donnée fictive comme réelle lorsque `DEMO_MODE=false`.

### Le health check indique `migration_required`

Relancer l’initialisation dans le conteneur :

```bash
docker compose exec educinfo educinfo init
```

## Licence

EducInfo est distribué sous licence MIT. Voir [LICENSE](LICENSE).
