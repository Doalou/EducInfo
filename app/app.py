from datetime import datetime, date, timedelta
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app.config import Config
from app.extensions import db, csrf, login_manager, logger
from app.models import User, Absence, WidgetConfig, Event, SiteConfig, WeatherConfig, MenuItem
from app.forms import (LoginForm, AbsenceForm, WidgetConfigForm, EventForm, 
                  ChangePasswordForm, SiteConfigForm, WeatherConfigForm, CTSForm, MenuItemForm)
import requests

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def initialize_database():
    """Initialise la base de données avec les configurations par défaut"""
    try:
        with app.app_context():
            db.create_all()
            
            # Initialisation de l'utilisateur admin
            admin = User.query.filter_by(identifiant=app.config.get('DEFAULT_ADMIN_ID', 'admin')).first()
            if not admin:
                admin = User(
                    identifiant=app.config.get('DEFAULT_ADMIN_ID', 'admin'), 
                    role='admin'
                )
                admin.set_password(app.config.get('DEFAULT_ADMIN_PASSWORD', 'admin123'))
                db.session.add(admin)
            
            # Initialisation des configurations si elles n'existent pas
            configs_to_check = {
                WeatherConfig: WeatherConfig(),
                SiteConfig: SiteConfig(),
                WidgetConfig: WidgetConfig()
            }
            for config_class, default_instance in configs_to_check.items():
                if not config_class.query.first():
                    db.session.add(default_instance)
            
            # Commit des changements initiaux (admin, configs)
            db.session.commit()
            logger.info('Base de données initialisée ou vérifiée avec succès')
                
    except Exception as e:
        db.session.rollback() # Assurer le rollback en cas d'erreur
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}", exc_info=True)
        # Rendre l'erreur fatale pour l'exécution
        raise SystemExit(f"Erreur BDD: {e}")

@app.context_processor
def utility_processor():
    def get_absence_status(absence, jour):
        return getattr(absence, jour, False)
    return {'get_absence_status': get_absence_status}

@app.context_processor
def inject_config():
    return {
        'site_config': SiteConfig.get_config(),
        'weather_city': app.config['WEATHER_CITY'],
        'current_datetime': datetime.now()
    }

@app.context_processor
def inject_models():
    """Injecte les modèles nécessaires dans les templates"""
    return {
        'MenuItem': MenuItem
    }

@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f'Page non trouvée: {request.url}')
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Erreur serveur: {error}')
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    logger.warning(f'Accès interdit: {request.url} par {current_user.identifiant if not current_user.is_anonymous else "anonyme"}')
    return render_template('errors/403.html'), 403

@app.errorhandler(401)
def unauthorized_error(error):
    logger.warning(f'Accès non autorisé: {request.url}')
    return render_template('errors/401.html'), 401

@app.errorhandler(405)
def method_not_allowed_error(error):
    logger.warning(f'Méthode non autorisée: {request.method} {request.url}')
    return render_template('errors/405.html'), 405

@app.errorhandler(Exception)
def handle_unhandled_error(error):
    logger.error(f'Erreur non gérée: {error}', exc_info=True)
    return render_template('errors/500.html'), 500

@app.route('/')
def home():
    try:
        config = WidgetConfig.query.first() or WidgetConfig()
        context = {
            'config': config,
            'absences': Absence.query.all(),
            'events': Event.get_upcoming_events(),
            'menu_items': MenuItem.get_todays_menu() if config.show_menu_cantine else [],
            'cts_arrivals': get_cts_arrivals(config) if config.has_valid_transport_config() else [],
            'active_widgets': config.get_all_active_widgets()
        }
        return render_template('home.html', **context)
    except Exception as e:
        logger.error(f'Erreur page d\'accueil: {str(e)}')
        return f"Erreur : {str(e)}", 500

# Constantes CTS
CTS_API_TIMEOUT = 5
CTS_PREVIEW_INTERVAL = "PT2H"
CTS_MAX_VISITS = 10
CTS_ADMIN_PREVIEW_INTERVAL = "PT30M"
CTS_ADMIN_MAX_VISITS = 5

def _fetch_cts_data(stop_code, vehicle_mode, api_token, base_url, preview_interval, max_visits):
    """Fonction helper pour interroger l'API CTS."""
    if not stop_code or not stop_code.strip():
        logger.warning("Code d'arrêt CTS manquant ou vide")
        return []
    
    effective_api_token = api_token or app.config.get('CTS_API_TOKEN')
    if not effective_api_token:
        logger.error("Token API CTS manquant (ni dans config widget, ni dans config app)")
        return []

    endpoint = f"{base_url}/v1/siri/2.0/stop-monitoring"
    params = {
        "MonitoringRef": stop_code,
        "VehicleMode": vehicle_mode or "undefined",
        "PreviewInterval": preview_interval,
        "MaximumStopVisits": max_visits
    }

    logger.info(f"Requête CTS: {endpoint} avec params {params}")
    try:
        response = requests.get(
            endpoint, 
            params=params,
            auth=(effective_api_token, ""),
            timeout=CTS_API_TIMEOUT
        )
        response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP
        
        data = response.json()
        # Utilisation de .get() pour éviter les KeyError
        delivery = data.get("ServiceDelivery", {}).get("StopMonitoringDelivery", [{}])[0]
        visits = delivery.get("MonitoredStopVisit", [])
        logger.info(f"Nombre de passages CTS trouvés: {len(visits)}")
        return visits
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'appel API CTS: {e}")
        return []
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Erreur lors du parsing de la réponse CTS: {e} - Réponse: {response.text if 'response' in locals() else 'N/A'}")
        return []
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la récupération CTS: {e}")
        return []

def get_cts_arrivals(config):
    if not config.show_transports:
        logger.info("Widget transport désactivé")
        return []

    return _fetch_cts_data(
        stop_code=config.cts_stop_code,
        vehicle_mode=config.cts_vehicle_mode,
        api_token=config.cts_api_token, # Le token spécifique au widget
        base_url=app.config['CTS_BASE_URL'],
        preview_interval=CTS_PREVIEW_INTERVAL,
        max_visits=CTS_MAX_VISITS
    )

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(identifiant=form.identifiant.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Identifiants invalides', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin-dashboard', methods=['GET','POST'])
@login_required
def admin_dashboard():
    forms = {
        'absence_form': AbsenceForm(),
        'event_form': EventForm(),
        'password_form': ChangePasswordForm(),
        'site_form': SiteConfigForm(),
        'weather_form': WeatherConfigForm(),
        'widget_form': WidgetConfigForm(),
        'cts_form': CTSForm(),
        'menu_form': MenuItemForm()
    }
    
    configs = {
        'widget': WidgetConfig.query.first_or_404(), # Use first_or_404 for required configs
        'site': SiteConfig.get_config(),
        'weather': WeatherConfig.get_config()
    }
    
    # Pré-remplissage des formulaires via l'argument obj si pas soumis
    if not forms['widget_form'].is_submitted():
        forms['widget_form'] = WidgetConfigForm(obj=configs['widget'])
    if not forms['site_form'].is_submitted():
        forms['site_form'] = SiteConfigForm(obj=configs['site'])
    if not forms['weather_form'].is_submitted():
        forms['weather_form'] = WeatherConfigForm(obj=configs['weather'])

    # Variables pour la prévisualisation CTS
    cts_results = None
    searched_cts_stop = None
    searched_vehicle_mode = None

    # Traitement du POST
    if request.method == 'POST':
        # Traitement du formulaire de recherche CTS pour prévisualisation
        if 'submit_cts' in request.form or 'submit_cts_save' in request.form:
            if forms['cts_form'].validate_on_submit(): # Valider le formulaire CTS
                searched_cts_stop = forms['cts_form'].stop_code.data
                searched_vehicle_mode = forms['cts_form'].vehicle_mode.data
                
                cts_results = _fetch_cts_data(
                    stop_code=searched_cts_stop,
                    vehicle_mode=searched_vehicle_mode,
                    api_token=configs['widget'].cts_api_token, # Utilise le token du widget pour la prévisualisation
                    base_url=app.config['CTS_BASE_URL'],
                    preview_interval=CTS_ADMIN_PREVIEW_INTERVAL,
                    max_visits=CTS_ADMIN_MAX_VISITS
                )
                
                if not cts_results and searched_cts_stop:
                    flash("Aucune donnée trouvée pour cet arrêt ou erreur API", "warning")
                elif cts_results:
                     flash(f"{len(cts_results)} passages trouvés pour l'arrêt {searched_cts_stop}.", "info")
                
                # Si l'admin clique sur "Utiliser ce stop", on enregistre
                if 'submit_cts_save' in request.form and searched_cts_stop:
                    widget_config = configs['widget']
                    widget_config.cts_stop_code = searched_cts_stop
                    widget_config.cts_vehicle_mode = searched_vehicle_mode
                    # Ne pas écraser le token ici, il est géré par le form widget
                    db.session.commit()
                    flash("Code d'arrêt CTS enregistré pour l'affichage.", 'success')
                    return redirect(url_for('admin_dashboard'))
            else:
                flash("Erreur dans le formulaire de recherche CTS.", "danger")
                # Ne pas rediriger, afficher les erreurs du formulaire

        # Traitement du formulaire de configuration des widgets
        elif 'submit_widget' in request.form:
            form = forms['widget_form'] # Alias pour la clarté
            if form.validate_on_submit():
                widget_config = configs['widget']
                
                # Mettre à jour la config depuis les données validées du formulaire
                widget_config.show_menu_cantine = form.show_menu_cantine.data
                widget_config.show_transports = form.show_transports.data
                widget_config.cts_stop_display = form.cts_stop_display.data
                
                # Mettre à jour les champs CTS seulement si le widget transport est activé
                if widget_config.show_transports:
                    widget_config.cts_stop_code = form.cts_stop_code.data
                    widget_config.cts_vehicle_mode = form.cts_vehicle_mode.data
                    widget_config.cts_api_token = form.cts_api_token.data
                else:
                    # Optionnel: Réinitialiser les champs CTS si le widget est désactivé
                    # widget_config.cts_stop_code = ""
                    # widget_config.cts_vehicle_mode = "undefined"
                    # widget_config.cts_api_token = ""
                    pass # Garder les valeurs précédentes si désactivé

                try:
                    db.session.commit()
                    flash('Configuration widgets mise à jour', 'success')
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Erreur lors de la sauvegarde config widget: {e}")
                    flash('Erreur lors de la mise à jour de la configuration.', 'danger')
                
                return redirect(url_for('admin_dashboard'))
            else:
                 # Afficher les erreurs de validation du formulaire Widget
                 flash('Erreur dans le formulaire de configuration des widgets.', 'danger')
                 # Ne pas rediriger pour voir les erreurs

        # Traitement des autres formulaires (absences, événements, site, météo, etc.)
        else:
            form_handlers = {
                'delete_absence': handle_absence_deletion,
                'submit_absence': handle_absence_update,
                'submit_password': handle_password_change,
                'submit_event': handle_event_creation,
                'delete_event': handle_event_deletion,
                'submit_site': handle_site_config,
                'submit_weather': handle_weather_config,
                'submit_menu_item': handle_menu_item_creation,
                'delete_menu_item': handle_menu_item_deletion
            }
            action_handled = False
            for action, handler in form_handlers.items():
                if action in request.form:
                    action_handled = True
                    return handler(request, forms, configs)
            if not action_handled:
                 # Gérer le cas où aucun bouton connu n'a été soumis (peut arriver si le HTML change)
                 logger.warning("Formulaire POST reçu sans action connue dans admin_dashboard")
                 flash("Action non reconnue.", "warning")

    # Rendu pour GET ou si POST non redirigé (ex: erreur form CTS ou Widget)
    return render_template(
        'admin_dashboard.html',
        absences=Absence.query.all(),
        widget_config=configs['widget'], # Peut-être redondant si forms['widget_form'].obj est utilisé dans le template
        future_events=Event.get_upcoming_events(),
        menu_items=MenuItem.get_todays_menu(),
        **forms,
        # Passer les résultats CTS même si None
        cts_results=cts_results,
        searched_cts_stop=searched_cts_stop,
        searched_vehicle_mode=searched_vehicle_mode
    )

def handle_absence_deletion(request, forms, configs):
    absence_id = request.form.get('delete_absence')
    absence = Absence.query.get(absence_id)
    if absence:
        db.session.delete(absence)
        db.session.commit()
        flash('Absence supprimée avec succès', 'success')
    return redirect(url_for('admin_dashboard'))

def handle_absence_update(request, forms, configs):
    if forms['absence_form'].validate_on_submit():
        professeur = forms['absence_form'].professeur.data
        jours = request.form.getlist('jours')
        absence = Absence.query.filter_by(professeur=professeur).first()
        if not absence:
            absence = Absence(professeur=professeur)
            db.session.add(absence)
            flash(f'Nouvelle absence ajoutée pour {professeur}', 'success')
        else:
            flash(f'Absence mise à jour pour {professeur}', 'info')
        absence.lundi = 'lundi' in jours
        absence.mardi = 'mardi' in jours
        absence.mercredi = 'mercredi' in jours
        absence.jeudi = 'jeudi' in jours
        absence.vendredi = 'vendredi' in jours
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

def handle_weather_config(request, forms, configs):
    if forms['weather_form'].validate_on_submit():
        weather_config = configs['weather']
        weather_config.api_key = forms['weather_form'].api_key.data
        weather_config.city = forms['weather_form'].city.data
        weather_config.show_weather = forms['weather_form'].show_weather.data
        db.session.commit()
        app.config['WEATHER_API_KEY'] = weather_config.api_key
        app.config['WEATHER_CITY'] = weather_config.city
        flash('Configuration météo mise à jour', 'success')
    return redirect(url_for('admin_dashboard'))

def handle_password_change(request, forms, configs):
    if forms['password_form'].validate_on_submit():
        user = User.query.filter_by(identifiant=current_user.identifiant).first()
        if user and user.check_password(forms['password_form'].current_password.data):
            user.set_password(forms['password_form'].new_password.data)
            db.session.commit()
            flash('Mot de passe modifié avec succès', 'success')
            return redirect(url_for('logout'))
        else:
            flash('Mot de passe actuel incorrect', 'error')
    return redirect(url_for('admin_dashboard'))

def handle_event_creation(request, forms, configs):
    if forms['event_form'].validate_on_submit():
        evt = Event(
            title=forms['event_form'].title.data,
            date=forms['event_form'].date.data,
            description=forms['event_form'].description.data
        )
        db.session.add(evt)
        db.session.commit()
        flash('Événement ajouté', 'success')
    return redirect(url_for('admin_dashboard'))

def handle_event_deletion(request, forms, configs):
    event_id = request.form.get('delete_event')
    evt = Event.query.get(event_id)
    if evt:
        db.session.delete(evt)
        db.session.commit()
        flash('Événement supprimé', 'warning')
    return redirect(url_for('admin_dashboard'))

def handle_site_config(request, forms, configs):
    if forms['site_form'].validate_on_submit():
        site_config = configs['site']
        site_config.site_name = forms['site_form'].site_name.data
        db.session.commit()
        flash('Nom de l\'établissement mis à jour', 'success')
    return redirect(url_for('admin_dashboard'))

def handle_menu_item_creation(request, forms, configs):
    if forms['menu_form'].validate_on_submit():
        menu_item = MenuItem(
            category=forms['menu_form'].category.data,
            name=forms['menu_form'].name.data,
            description=forms['menu_form'].description.data,
            icons=''.join(forms['menu_form'].icons.data),
            date=forms['menu_form'].date.data
        )
        db.session.add(menu_item)
        db.session.commit()
        flash('Plat ajouté au menu', 'success')
    return redirect(url_for('admin_dashboard'))

def handle_menu_item_deletion(request, forms, configs):
    item_id = request.form.get('delete_menu_item')
    menu_item = MenuItem.query.get(item_id)
    if menu_item:
        db.session.delete(menu_item)
        db.session.commit()
        flash('Plat supprimé du menu', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/get_updates')
def get_updates():
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
        logger.error(f'Error in get_updates: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/get_weather')
def get_weather():
    try:
        weather_config = WeatherConfig.get_config()
        if not weather_config.show_weather:
            return jsonify({'error': 'Météo désactivée'}), 200

        # Utilisation de config directement
        api_key = weather_config.api_key or app.config.get('WEATHER_API_KEY')
        city = weather_config.city or app.config.get('WEATHER_CITY')
        
        if not api_key or not city:
             logger.error("Clé API ou ville manquante pour la météo")
             return jsonify({'error': 'Configuration météo incomplète'}), 500

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": api_key,
                "units": "metric",
                "lang": "fr"
            },
            timeout=CTS_API_TIMEOUT # Réutiliser le timeout
        )
        response.raise_for_status()

        data = response.json()
        # Accès sécurisé aux données
        weather_data = data.get('weather', [{}])[0]
        main_data = data.get('main', {})
        temp = main_data.get('temp')
        description = weather_data.get('description', 'N/A')
        icon = weather_data.get('icon', 'N/A')

        if temp is not None:
            description = description[:1].upper() + description[1:]
            return jsonify({
                'temp': round(temp),
                'description': description,
                'icon': icon
            })
        else:
             logger.error(f"Données de température manquantes dans la réponse OpenWeather: {data}")
             return jsonify({'error': 'Données météo invalides'}), 500

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur API OpenWeather: {e}")
        return jsonify({'error': 'Erreur de communication météo'}), 500
    except Exception as e:
        logger.error(f'Erreur get_weather: {e}')
        return jsonify({'error': 'Erreur interne serveur météo'}), 500

def get_weather_description(weather_code):
    weather_codes = {
        0: "Soleil",
        1: "Peu nuageux",
        2: "Ciel voilé",
        3: "Nuageux",
        4: "Très nuageux",
        5: "Couvert",
        6: "Brouillard",
        7: "Brouillard givrant",
        10: "Pluie faible",
        11: "Pluie modérée",
        12: "Pluie forte",
        13: "Neige faible",
        14: "Neige modérée",
        15: "Neige forte",
    }
    return weather_codes.get(weather_code, "Météo indéterminée")

def get_weather_icon(weather_code):
    weather_icons = {
        0: "☀️",
        1: "🌤️",
        2: "⛅",
        3: "☁️",
        4: "☁️",
        5: "☁️",
        6: "🌫️",
        7: "🌫️",
        10: "🌦️",
        11: "🌧️",
        12: "⛈️",
        13: "🌨️",
        14: "🌨️",
        15: "🌨️",
    }
    return weather_icons.get(weather_code, "🌡️")