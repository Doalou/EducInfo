"""
Tests unitaires pour le modèle User.
"""
import pytest
from app.models.user import User
from app.extensions import db


def test_new_user():
    """
    ETANT DONNE un modèle User
    QUAND un nouvel utilisateur est créé
    ALORS ses attributs doivent être correctement définis
    """
    user = User(email='user@test.com', username='testuser')
    user.set_password('password123')
    
    assert user.email == 'user@test.com'
    assert user.username == 'testuser'
    assert user.is_admin is False  # Par défaut, l'utilisateur n'est pas admin
    assert user.check_password('password123') is True
    assert user.check_password('wrongpassword') is False


def test_user_model_str_representation(app):
    """
    ETANT DONNE un modèle User
    QUAND la méthode __repr__ est appelée
    ALORS elle doit retourner une représentation string correcte
    """
    with app.app_context():
        user = User(email='user@test.com', username='testuser')
        assert str(user) == f'<User {user.username}>'


def test_user_is_active(app):
    """
    ETANT DONNE un modèle User
    QUAND la propriété is_active est vérifiée
    ALORS elle doit retourner True pour un utilisateur actif
    """
    with app.app_context():
        user = User(email='user@test.com', username='testuser')
        assert user.is_active is True 