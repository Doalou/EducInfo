"""
Tests unitaires pour les routes publiques.
"""
import pytest
from flask import url_for


def test_home_page(client):
    """
    ETANT DONNE un client HTTP
    QUAND une requête GET est envoyée à la page d'accueil
    ALORS le statut de la réponse doit être 200 OK
    """
    response = client.get(url_for('public.home'))
    assert response.status_code == 200
    assert b'EducInfo' in response.data


def test_home_page_shows_absences(client, app):
    """
    ETANT DONNE une base de données contenant des absences
    QUAND un utilisateur visite la page d'accueil
    ALORS les absences doivent être affichées
    """
    from app.models.absence import Absence
    from app.extensions import db

    with app.app_context():
        absence = Absence(professeur="Prof Test", lundi=True)
        db.session.add(absence)
        db.session.commit()

    response = client.get(url_for('public.home'))
    assert response.status_code == 200
    assert b'Prof Test' in response.data


def test_get_updates_endpoint(client):
    """
    ETANT DONNE un client HTTP
    QUAND une requête GET est envoyée à /get_updates
    ALORS le statut de la réponse doit être 200 et retourner du JSON
    """
    response = client.get(url_for('public.get_updates'))
    assert response.status_code == 200
    data = response.get_json()
    assert 'absences' in data
    assert 'events' in data


def test_offline_page(client):
    """
    ETANT DONNE un client HTTP
    QUAND une requête GET est envoyée à /offline
    ALORS le statut de la réponse doit être 200
    """
    response = client.get(url_for('public.offline'))
    assert response.status_code == 200
