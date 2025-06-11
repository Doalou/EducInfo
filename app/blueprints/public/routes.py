"""Routes publiques optimisées pour EducInfo."""
from datetime import datetime, date
from flask import render_template, jsonify, current_app, send_from_directory, request, redirect, url_for
from app.blueprints.public import bp
from app.models import Absence, Event, MenuItem, WidgetConfig, WeatherConfig
from app.extensions import db, logger
from app.services import weather_service, transport_service, menu_service
import os

@bp.route('/')
def home():
    """Page d'accueil optimisée pour affichage TV."""
    try:
        widget_config = WidgetConfig.query.first() or WidgetConfig()
        weather_config = WeatherConfig.get_config()
        cts_api_token = current_app.config.get('CTS_API_TOKEN')
        
        # Récupération optimisée des données
        absences = Absence.query.all()
        events = Event.get_upcoming_events()
        menu_items = menu_service.get_todays_menu() if widget_config.show_menu_cantine else []
        
        # Transport avec gestion d'erreur optimisée
        cts_arrivals = []
        if widget_config.has_valid_transport_config(cts_api_token):
            try:
                transport_data = transport_service.get_stop_arrivals(
                    stop_code=widget_config.cts_stop_code,
                    vehicle_mode=widget_config.cts_vehicle_mode,
                    api_token=widget_config.cts_api_token or cts_api_token
                )
                cts_arrivals = transport_data.get('arrivals', [])
            except Exception as e:
                logger.error(f'Erreur transport: {e}')
        
        # Organisation optimisée des absences
        days_order = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
        absences_by_day = {day.title(): [] for day in days_order}
        
        for absence in absences:
            for day in days_order:
                if getattr(absence, day, False):
                    absences_by_day[day.title()].append(absence.professeur)
        
        # Organisation optimisée du menu
        todays_menu = {}
        categories = {1: 'Entrée', 2: 'Plat principal', 3: 'Fromage', 4: 'Dessert'}
        
        for menu_item in menu_items:
            category_name = categories.get(menu_item.category, 'Autre')
            todays_menu.setdefault(category_name, []).append(menu_item)
        
        context = {
            'widget_config': widget_config,
            'weather_config': weather_config,
            'cts_api_token': cts_api_token,
            'absences': absences,
            'events': events,
            'menu_items': menu_items,
            'cts_arrivals': cts_arrivals,
            'active_widgets': widget_config.get_all_active_widgets(cts_api_token),
            'menu_service': menu_service,
            'weather_service': weather_service,
            'today': date.today(),
            'now': datetime.now(),
            'absences_by_day': absences_by_day,
            'todays_menu': todays_menu,
            'upcoming_events': events,
            'site_config': {'site_name': 'EducInfo'}
        }
        
        return render_template('public/home.html', **context)
        
    except Exception as e:
        logger.error(f'Erreur page d\'accueil: {str(e)}')
        return "Erreur interne du serveur.", 500

@bp.route('/admin')
def admin_redirect():
    """Redirection vers l'interface d'administration."""
    return redirect(url_for('admin.dashboard'))

@bp.route('/get_updates')
def get_updates():
    """API JSON pour mises à jour des données."""
    try:
        widget_config = WidgetConfig.query.first()
        if not widget_config:
            widget_config = WidgetConfig()
            db.session.add(widget_config)
            db.session.commit()
            
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
            'date_formatted': e.date.strftime('%d/%m/%Y'),
            'description': e.description
        } for e in Event.get_upcoming_events()]
        
        # Récupération du menu de cantine si activé
        menu_items = []
        if widget_config.show_menu_cantine:
            menu_items = menu_service.get_todays_menu()
            
        # Formatage du menu pour l'API JSON
        menu_data = [{
            'id': item.id,
            'name': item.name,
            'category': item.category,
            'icons': getattr(item, 'icons', ''),
            'date': item.date.strftime('%Y-%m-%d') if item.date else None
        } for item in menu_items]
        
        return jsonify({
            'absences': absences,
            'events': events,
            'menu': menu_data,
            'widget_config': {'show_menu_cantine': widget_config.show_menu_cantine}
        })
    except Exception as e:
        logger.error(f'Erreur get_updates: {str(e)}')
        return jsonify({'error': 'Erreur interne serveur'}), 500

@bp.route('/get_weather')
def get_weather():
    """API JSON pour données météo."""
    try:
        weather_data = weather_service.get_weather_data()
        
        if 'error' in weather_data:
            logger.error(f"Erreur météo: {weather_data['error']}")
            return jsonify({'error': 'Erreur récupération données météo'}), 500
            
        return jsonify(weather_data)
    except Exception as e:
        logger.error(f'Erreur get_weather: {e}')
        return jsonify({'error': 'Erreur interne serveur météo'}), 500

@bp.route('/get_transports')
def get_transports():
    """API JSON pour données de transport."""
    try:
        widget_config = WidgetConfig.query.first()
        if not widget_config:
            return jsonify({'error': 'Configuration widget manquante'}), 500
        
        cts_api_token = widget_config.cts_api_token or current_app.config.get('CTS_API_TOKEN')
        
        if not widget_config.has_valid_transport_config(cts_api_token):
            return jsonify({'error': 'Configuration transport manquante'}), 400
        
        transport_data = transport_service.get_stop_arrivals(
            stop_code=widget_config.cts_stop_code,
            vehicle_mode=widget_config.cts_vehicle_mode,
            api_token=cts_api_token
        )
        
        if 'error' in transport_data:
            logger.error(f"Erreur transport: {transport_data['error']}")
            return jsonify({'error': 'Erreur récupération données transport'}), 500
            
        return jsonify(transport_data)
    except Exception as e:
        logger.error(f'Erreur get_transports: {e}')
        return jsonify({'error': 'Erreur interne serveur transport'}), 500

@bp.route('/debug/weather')
def debug_weather():
    """Route de diagnostic pour la météo."""
    try:
        weather_config = WeatherConfig.get_config()
        weather_data = weather_service.get_weather_data()
        
        debug_info = {
            'weather_config': {
                'show_weather': weather_config.show_weather if weather_config else None,
                'city': weather_config.city if weather_config else None,
                'has_api_key': bool(weather_config.api_key if weather_config else False),
                'api_key_length': len(weather_config.api_key) if weather_config and weather_config.api_key else 0
            },
            'environment_config': {
                'WEATHER_API_KEY': bool(current_app.config.get('WEATHER_API_KEY')),
                'WEATHER_CITY': current_app.config.get('WEATHER_CITY', 'Non défini')
            },
            'weather_data': weather_data,
            'cache_status': 'Actif' if hasattr(current_app, 'cache') else 'Inactif'
        }
        
        return jsonify(debug_info)
    except Exception as e:
        logger.error(f'Erreur debug_weather: {e}')
        return jsonify({'error': str(e)}), 500

@bp.route('/debug/transport')
def debug_transport():
    """Route de diagnostic pour le transport."""
    try:
        widget_config = WidgetConfig.query.first()
        config_data = {
            'show_transports': widget_config.show_transports if widget_config else False,
            'cts_stop_code': widget_config.cts_stop_code if widget_config else None,
            'cts_vehicle_mode': widget_config.cts_vehicle_mode if widget_config else None,
            'has_api_token': bool(widget_config.cts_api_token if widget_config else False)
        }
        
        environment_data = {
            'CTS_API_TOKEN': bool(current_app.config.get('CTS_API_TOKEN')),
            'CTS_BASE_URL': current_app.config.get('CTS_BASE_URL', 'Non défini')
        }
        
        transport_data = {}
        if widget_config and widget_config.has_valid_transport_config():
            try:
                transport_data = transport_service.get_stop_arrivals(
                    stop_code=widget_config.cts_stop_code,
                    vehicle_mode=widget_config.cts_vehicle_mode,
                    api_token=widget_config.cts_api_token or current_app.config.get('CTS_API_TOKEN')
                )
            except Exception as e:
                transport_data = {'error': str(e)}
        
        debug_info = {
            'widget_config': config_data,
            'environment_config': environment_data,
            'transport_data': transport_data,
            'cache_status': 'Actif' if hasattr(current_app, 'cache') else 'Inactif'
        }
        
        return jsonify(debug_info)
    except Exception as e:
        logger.error(f'Erreur debug_transport: {e}')
        return jsonify({'error': str(e)}), 500

@bp.route('/favicon.ico')
def favicon():
    """Sert le favicon."""
    try:
        return send_from_directory(
            os.path.join(current_app.root_path, 'static', 'img'),
            'favicon.svg', mimetype='image/svg+xml'
        )
    except Exception:
        return '', 404

@bp.route('/offline')
def offline():
    """Page hors ligne."""
    return render_template('public/offline.html') 