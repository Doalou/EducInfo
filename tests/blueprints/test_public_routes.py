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
        # Ajouter une absence de test
        absence = Absence(professeur="Prof Test", lundi=True)
        db.session.add(absence)
        db.session.commit()
    
    response = client.get(url_for('public.home'))
    assert response.status_code == 200
    assert b'Prof Test' in response.data


def test_home_page_shows_weather(client, monkeypatch):
    """
    ETANT DONNE un service météo qui retourne des données
    QUAND un utilisateur visite la page d'accueil
    ALORS les informations météo doivent être affichées
    """
    # Créer une fonction mock pour get_weather_data
    def mock_get_weather_data(*args, **kwargs):
        return {
            "city": "Test City",
            "temp": 20.5,
            "feels_like": 19.8,
            "humidity": 55,
            "wind_speed": 3.5,
            "description": "ciel dégagé",
            "icon": "01d"
        }
    
    # Appliquer le patch avec monkeypatch
    monkeypatch.setattr("app.blueprints.public.routes.get_weather_data", mock_get_weather_data)
    
    response = client.get(url_for('public.home'))
    assert response.status_code == 200
    assert b'Test City' in response.data
    assert b'20.5' in response.data
    assert b'ciel d\xc3\xa9gag\xc3\xa9' in response.data  # ciel dégagé encodé en UTF-8 