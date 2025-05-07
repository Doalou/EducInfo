"""
Configuration pytest pour les tests de l'application EducInfo.
"""
import os
import tempfile
import pytest
from app import create_app
from app.extensions import db
from app.models.user import User


@pytest.fixture
def app():
    """Fixture qui crée et configure une application Flask pour les tests."""
    # Création d'un fichier temporaire comme base de données de test
    db_fd, db_path = tempfile.mkstemp()
    
    # Configuration de l'application en mode test
    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'WEATHER_API_KEY': 'test_key',
        'WEATHER_CITY': 'Test City',
        'CTS_API_TOKEN': 'test_token',
        'CTS_STOP_CODE': 'test_stop'
    })
    
    # Création du contexte d'application
    with app.app_context():
        # Création des tables dans la base de données de test
        db.create_all()
        
        # Création d'un utilisateur de test
        test_user = User(email='test@example.com', username='testuser')
        test_user.set_password('password')
        test_user.is_admin = True
        db.session.add(test_user)
        db.session.commit()
    
    yield app
    
    # Nettoyage après les tests
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Fixture qui crée un client de test pour envoyer des requêtes à l'application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Fixture qui crée un runner pour tester les commandes CLI."""
    return app.test_cli_runner()


@pytest.fixture
def auth(client):
    """Fixture qui fournit des méthodes pour se connecter et se déconnecter."""
    class AuthActions:
        def login(self, email='test@example.com', password='password'):
            return client.post(
                '/auth/login',
                data={'identifiant': email, 'password': password},
                follow_redirects=True
            )
        
        def logout(self):
            return client.get('/auth/logout', follow_redirects=True)
    
    return AuthActions() 