# EducInfo - Plateforme d'Information Scolaire

**Version 1.1.0**

EducInfo est une application web Flask qui centralise et affiche des informations essentielles pour les établissements scolaires:
- Absences des professeurs
- Menus de la cantine
- Informations météo
- Horaires des transports en commun
- Événements à venir

## Structure du Projet

Le projet est organisé selon une architecture modulaire:

```
EducInfo/
├── app/                           # Code de l'application
│   ├── __init__.py                # Factory pattern
│   ├── blueprints/                # Routes organisées par fonctionnalité
│   ├── models/                    # Modèles de données
│   ├── services/                  # Services et logique métier
│   ├── static/                    # Ressources statiques
│   ├── templates/                 # Templates HTML
│   └── utils/                     # Fonctions utilitaires
├── docker/                        # Configuration Docker
├── instance/                      # Données spécifiques à l'instance
├── logs/                          # Fichiers de logs
├── tests/                         # Tests unitaires et d'intégration
├── .env.example                   # Exemple de variables d'environnement
├── requirements.txt               # Dépendances Python
└── run.py                         # Point d'entrée de l'application
```

**Note importante pour la mise à jour depuis une version < 1.1.0 :**
Avec la version 1.1.0, le système d'authentification a été modifié pour utiliser un nom d'utilisateur au lieu d'une adresse e-mail comme identifiant principal. Si vous mettez à jour depuis une version antérieure, vous **devez supprimer votre ancien fichier de base de données** (par exemple, `instance/educinfo.db`) et réinitialiser la base de données avec `python run.py init-db` pour appliquer les nouveaux changements de structure.

## Installation et Configuration

### Prérequis
- Python 3.12+
- pip
- Un environnement virtuel Python (recommandé)

### Installation

1. Cloner le dépôt:
```bash
git clone https://github.com/votre-utilisateur/educinfo.git
cd educinfo
```

2. Créer et activer un environnement virtuel:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. Installer les dépendances:
```bash
pip install -r requirements.txt
```

4. Créer le fichier `.env` à partir du modèle:
```bash
cp .env.example .env
```

5. Personnaliser le fichier `.env` avec vos informations.

### Initialisation de la base de données

Avant de lancer l'application pour la première fois, ou après avoir supprimé la base de données pour une mise à jour, vous devez l'initialiser. Assurez-vous d'avoir activé votre environnement virtuel.

1. Définissez la variable d'environnement `FLASK_APP` (une seule fois par session de terminal, ou ajoutez-la à votre `.env` ou `.flaskenv`):
```powershell
# Pour PowerShell
$env:FLASK_APP = "run:app"

# Pour bash/zsh (Linux/macOS)
export FLASK_APP="run:app"
```

2. Initialisez la base de données:
```bash
flask init-db
```
Cette commande crée les tables nécessaires, le dossier `instance/` (s'il n'existe pas), et quelques configurations par défaut.

### Création d'un utilisateur administrateur

Pour créer un compte administrateur (ou un utilisateur standard), utilisez la commande CLI `add-user` après avoir initialisé la base de données (assurez-vous que `FLASK_APP` est défini) :

```bash
# Pour un administrateur
flask add-user --username votre_nom_admin --admin

# Pour un utilisateur standard
flask add-user --username votre_nom_user
```
Suivez les invites pour définir le mot de passe.

**(Obsolète)** L'ancienne commande `create-admin` est dépréciée.

### Configuration

Modifiez le fichier `.env` pour configurer votre instance:
- Clés API (OpenWeatherMap, CTS)
- Paramètres de l'application
- Configuration de la base de données

## Utilisation

### Mode Développement

Après avoir initialisé la base de données et créé un utilisateur (voir ci-dessus) :

1. Assurez-vous que la variable d'environnement `FLASK_APP` est définie (voir section Initialisation).
2. Lancez l'application en mode développement:
```bash
flask run
```

Accéder à l'application: http://localhost:5000

(L'ancienne méthode `python run.py` pour lancer directement le serveur n'est plus recommandée pour le développement afin de permettre une meilleure gestion des commandes CLI.)

### Mode Production

1. Configuration des variables d'environnement:
```
FLASK_ENV=production
FLASK_DEBUG=0
```

2. Lancement avec Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 3 run:app
```

### Docker

Construire et exécuter avec Docker (assurez-vous d'avoir initialisé la base de données localement ou via un script d'entrée Docker si nécessaire):
```bash
docker build -t educinfo .
docker run -p 5000:5000 -v ./instance:/app/instance --env-file .env educinfo
```

## Tests

Exécuter les tests unitaires et d'intégration:
```bash
pip install -r tests/requirements.txt
pytest
```

## Fonctionnalités

- **Affichage des absences**: Visualisation claire des absences des enseignants
- **Menu cantine**: Affichage du menu du jour avec icônes et catégories
- **Météo**: Informations météorologiques en temps réel
- **Transports**: Prochains passages de bus/tram à proximité de l'établissement
- **Événements**: Calendrier des événements à venir
- **Mode sombre**: Interface adaptable à la luminosité ambiante
- **Authentification**: Connexion par nom d'utilisateur et mot de passe.

## Licence

Ce projet est distribué sous licence MIT.

## Remerciements

- [Flask](https://flask.palletsprojects.com/) - Framework web
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM pour la base de données
- [Tailwind CSS](https://tailwindcss.com/) - Framework CSS
