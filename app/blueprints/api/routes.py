"""
Routes pour le blueprint API.
Ce module définit les endpoints de l'API REST.
"""
from flask import jsonify
from app.blueprints.api import bp
from app.models import Absence, Event
from app.extensions import logger
from app.services import menu_service, weather_service, transport_service

@bp.route('/version')
def version():
    """Retourne la version de l'API."""
    return jsonify({
        'name': 'EducInfo API',
        'version': '1.0.0'
    })

@bp.route('/absences')
def absences():
    """Retourne la liste des absences au format JSON."""
    try:
        absences = [{
            'id': a.id,
            'professeur': a.professeur,
            'lundi': a.lundi,
            'mardi': a.mardi,
            'mercredi': a.mercredi,
            'jeudi': a.jeudi,
            'vendredi': a.vendredi,
            'samedi': a.samedi
        } for a in Absence.query.all()]
        return jsonify({
            'success': True,
            'count': len(absences),
            'data': absences
        })
    except Exception as e:
        logger.error(f'Erreur API absences: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'An internal error has occurred.'
        }), 500

@bp.route('/events')
def events():
    """Retourne la liste des événements au format JSON."""
    try:
        events = [{
            'id': e.id,
            'title': e.title,
            'date': e.date.strftime('%Y-%m-%d'),
            'description': e.description,
            'is_future': e.is_future()
        } for e in Event.get_upcoming_events()]
        return jsonify({
            'success': True,
            'count': len(events),
            'data': events
        })
    except Exception as e:
        logger.error(f'Erreur API events: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'An internal error has occurred.'
        }), 500

@bp.route('/menu')
def menu():
    """Retourne le menu du jour au format JSON."""
    try:
        # Utiliser le service menu
        menu_items = menu_service.get_todays_menu()
        
        # Formater les données pour l'API
        formatted_items = [{
            'id': m.id,
            'category': m.category,
            'name': m.name,
            'description': m.description,
            'icons': m.icons,
            'date': m.date.strftime('%Y-%m-%d')
        } for m in menu_items]
        
        # Organiser les plats par catégorie en utilisant le service
        categories = menu_service.organize_menu_by_category(menu_items)
        formatted_categories = {}
        
        for category, items in categories.items():
            formatted_categories[category] = [{
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'icons': item.icons
            } for item in items]
        
        return jsonify({
            'success': True,
            'count': len(formatted_items),
            'categories': formatted_categories,
            'data': formatted_items
        })
    except Exception as e:
        logger.error(f'Erreur API menu: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'An internal error has occurred.'
        }), 500

@bp.route('/weather')
def weather():
    """Retourne les données météo actuelles au format JSON."""
    try:
        # Utiliser le service météo
        weather_data = weather_service.get_weather_data()
        
        # Vérifier si une erreur est survenue
        if 'error' in weather_data:
            logger.error(f"Erreur API weather: {weather_data['error']}")
            return jsonify({
                'success': False,
                'error': 'An internal error has occurred.'
            }), 500
        
        return jsonify({
            'success': True,
            'data': weather_data
        })
    except Exception as e:
        logger.error(f'Erreur API weather: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/transports')
def transports():
    """Retourne les données de transport au format JSON."""
    try:
        # Utiliser le service transport
        transport_data = transport_service.get_stop_arrivals()
        
        # Vérifier si une erreur est survenue
        if 'error' in transport_data:
            return jsonify({
                'success': False,
                'error': transport_data['error']
            }), 500
        
        return jsonify({
            'success': True,
            'count': transport_data.get('count', 0),
            'stop_code': transport_data.get('stop_code', ''),
            'data': transport_data.get('arrivals', [])
        })
    except Exception as e:
        logger.error(f'Erreur API transports: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 