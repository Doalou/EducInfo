"""
Routes pour le blueprint public.
Ce module définit les routes publiques de l'application.
"""
from datetime import datetime
from flask import render_template, jsonify, current_app, send_from_directory
from app.blueprints.public import bp
from app.models import Absence, Event, MenuItem, WidgetConfig
from app.extensions import db, logger
from app.services import weather_service, transport_service, menu_service
import os

@bp.route('/')
def home():
    """Page d'accueil affichant les informations pour les visiteurs."""
    try:
        config = WidgetConfig.query.first() or WidgetConfig()
        context = {
            'config': config,
            'absences': Absence.query.all(),
            'events': Event.get_upcoming_events(),
            'menu_items': menu_service.get_todays_menu() if config.show_menu_cantine else [],
            'cts_arrivals': transport_service.get_stop_arrivals().get('arrivals', []) if config.has_valid_transport_config() else [],
            'active_widgets': config.get_all_active_widgets()
        }
        return render_template('public/home.html', **context)
    except Exception as e:
        logger.error(f'Erreur page d\'accueil: {str(e)}')
        return f"Erreur : {str(e)}", 500

@bp.route('/get_updates')
def get_updates():
    """Endpoint API JSON pour obtenir les mises à jour des absences et événements."""
    try:
        widget_config = WidgetConfig.query.first()
        if not widget_config:
            widget_config = WidgetConfig()
            db.session.add(widget_config)
            db.session.commit()
        config_data = {
            'show_menu_cantine': widget_config.show_menu_cantine
        }
        absences = [{
            'professeur': a.professeur,
            'lundi': a.lundi,
            'mardi': a.mardi,
            'mercredi': a.mercredi,
            'jeudi': a.jeudi,
            'vendredi': a.vendredi
        } for a in Absence.query.all()]
        events = [{
            'title': e.title,
            'date': e.date.strftime('%d/%m/%Y'),
            'description': e.description
        } for e in Event.get_upcoming_events()]
        return jsonify({
            'absences': absences,
            'events': events,
            'widget_config': config_data
        })
    except Exception as e:
        logger.error(f'Erreur dans get_updates: {str(e)}')
        return jsonify({'error': str(e)}), 500

@bp.route('/get_weather')
def get_weather():
    """Endpoint API JSON pour obtenir les données météo."""
    try:
        # Utiliser le service météo au lieu d'appeler directement l'API
        weather_data = weather_service.get_weather_data()
        
        # Vérifier si une erreur est survenue
        if 'error' in weather_data:
            logger.error(f"Erreur météo: {weather_data['error']}")
            return jsonify({'error': weather_data['error']}), 500
            
        return jsonify(weather_data)
    except Exception as e:
        logger.error(f'Erreur get_weather: {e}')
        return jsonify({'error': 'Erreur interne serveur météo'}), 500

@bp.route('/get_transports')
def get_transports():
    """Endpoint API JSON pour obtenir les données de transport."""
    try:
        # Utiliser le service transport au lieu d'appeler directement l'API
        transport_data = transport_service.get_stop_arrivals()
        
        # Vérifier si une erreur est survenue
        if 'error' in transport_data:
            logger.error(f"Erreur transport: {transport_data['error']}")
            return jsonify({'error': transport_data['error']}), 500
            
        return jsonify(transport_data)
    except Exception as e:
        logger.error(f'Erreur get_transports: {e}')
        return jsonify({'error': 'Erreur interne serveur transport'}), 500

@bp.route('/favicon.ico')
def favicon():
    """Route pour servir le favicon à la racine du site."""
    return send_from_directory(
        os.path.join(current_app.root_path, 'static', 'img'),
        'favicon.ico', mimetype='image/x-icon'
    ) 