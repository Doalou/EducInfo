"""
Routes pour le blueprint d'administration.
Ce module définit les routes et la logique d'administration du site.
"""
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime

from app.blueprints.admin import bp
from app.blueprints.auth.routes import handle_password_change
from app.blueprints.auth.forms import ChangePasswordForm
from app.blueprints.admin.forms import (AbsenceForm, EventForm, 
                                      ConfigForm as SiteConfigForm, 
                                      WeatherConfigForm, TransportConfigForm as WidgetConfigForm,
                                      MenuItemForm,
                                      CTSForm)

from app.models.absence import Absence
from app.models.event import Event
from app.models.menu import MenuItem
from app.models.config import WidgetConfig, SiteConfig, WeatherConfig
from app.extensions import db, logger
from app.services import transport_service, menu_service

# Constantes CTS pour l'admin
CTS_ADMIN_PREVIEW_INTERVAL = "PT30M"
CTS_ADMIN_MAX_VISITS = 5

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """Tableau de bord d'administration."""
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
        'widget': WidgetConfig.query.first_or_404(),
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
            if forms['cts_form'].validate_on_submit():
                searched_cts_stop = forms['cts_form'].stop_code.data
                searched_vehicle_mode = forms['cts_form'].vehicle_mode.data
                
                # Récupérer les passages via le service transport
                transport_data = transport_service.get_stop_arrivals(
                    stop_code=searched_cts_stop,
                    vehicle_mode=searched_vehicle_mode,
                    preview_interval=CTS_ADMIN_PREVIEW_INTERVAL,
                    max_visits=CTS_ADMIN_MAX_VISITS
                )
                
                # Vérifier si une erreur est survenue
                if 'error' in transport_data:
                    flash(f"Erreur: {transport_data['error']}", "danger")
                    cts_results = []
                else:
                    cts_results = transport_data.get('arrivals', [])
                    if not cts_results:
                        flash("Aucune donnée trouvée pour cet arrêt", "warning")
                    else:
                        flash(f"{len(cts_results)} passages trouvés pour l'arrêt {searched_cts_stop}.", "info")
                
                # Si l'admin clique sur "Utiliser ce stop", on enregistre
                if 'submit_cts_save' in request.form and searched_cts_stop:
                    widget_config = configs['widget']
                    widget_config.cts_stop_code = searched_cts_stop
                    widget_config.cts_vehicle_mode = searched_vehicle_mode
                    db.session.commit()
                    flash("Code d'arrêt CTS enregistré pour l'affichage.", 'success')
                    return redirect(url_for('admin.dashboard'))
            else:
                flash("Erreur dans le formulaire de recherche CTS.", "danger")

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

                try:
                    db.session.commit()
                    flash('Configuration widgets mise à jour', 'success')
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Erreur lors de la sauvegarde config widget: {e}")
                    flash('Erreur lors de la mise à jour de la configuration.', 'danger')
                
                return redirect(url_for('admin.dashboard'))
            else:
                 flash('Erreur dans le formulaire de configuration des widgets.', 'danger')

        # Traitement des autres formulaires
        else:
            form_handlers = {
                'delete_absence': handle_absence_deletion,
                'submit_absence': handle_absence_update,
                'submit_password': handle_password_form,
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
                 logger.warning("Formulaire POST reçu sans action connue dans admin_dashboard")
                 flash("Action non reconnue.", "warning")

    # Rendu pour GET ou si POST non redirigé
    return render_template(
        'admin/dashboard.html',
        absences=Absence.query.all(),
        widget_config=configs['widget'],
        future_events=Event.get_upcoming_events(),
        menu_items=menu_service.get_todays_menu(),
        **forms,
        cts_results=cts_results,
        searched_cts_stop=searched_cts_stop,
        searched_vehicle_mode=searched_vehicle_mode
    )

def handle_absence_deletion(request, forms, configs):
    """Gère la suppression d'une absence."""
    absence_id = request.form.get('delete_absence')
    absence = Absence.query.get(absence_id)
    if absence:
        db.session.delete(absence)
        db.session.commit()
        flash('Absence supprimée avec succès', 'success')
    return redirect(url_for('admin.dashboard'))

def handle_absence_update(request, forms, configs):
    """Gère l'ajout ou la mise à jour d'une absence."""
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
        absence.samedi = 'samedi' in jours
        db.session.commit()
    return redirect(url_for('admin.dashboard'))

def handle_password_form(request, forms, configs):
    """Gère le formulaire de changement de mot de passe."""
    if handle_password_change(forms['password_form']):
        flash('Mot de passe modifié avec succès', 'success')
        return redirect(url_for('auth.logout'))
    else:
        flash('Mot de passe actuel incorrect', 'error')
    return redirect(url_for('admin.dashboard'))

def handle_event_creation(request, forms, configs):
    """Gère la création d'un événement."""
    if forms['event_form'].validate_on_submit():
        date_str = forms['event_form'].date.data
        try:
            # Assurez-vous que date_str est bien une chaîne au format JJ/MM/AAAA
            # DateField de WTForms devrait retourner un objet date si format est spécifié,
            # mais si c'est une chaîne, nous la convertissons.
            if isinstance(date_str, str):
                parsed_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            else: # Supposons que c'est déjà un objet date/datetime
                parsed_date = date_str 
                if hasattr(parsed_date, 'date'): # Si c'est un objet datetime, prendre la partie date
                    parsed_date = parsed_date.date()

            evt = Event(
                title=forms['event_form'].title.data,
                date=parsed_date,
                description=forms['event_form'].description.data
            )
            db.session.add(evt)
            db.session.commit()
            flash('Événement ajouté', 'success')
        except ValueError:
            flash('Format de date invalide. Utilisez JJ/MM/AAAA.', 'danger')
            # Il est important de faire un rollback si la conversion de date échoue avant le commit
            db.session.rollback()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de l'événement: {e}")
            flash(f"Erreur lors de la création de l'événement: {e}", 'danger')
            
    return redirect(url_for('admin.dashboard'))

def handle_event_deletion(request, forms, configs):
    """Gère la suppression d'un événement."""
    event_id = request.form.get('delete_event')
    evt = Event.query.get(event_id)
    if evt:
        db.session.delete(evt)
        db.session.commit()
        flash('Événement supprimé', 'warning')
    return redirect(url_for('admin.dashboard'))

def handle_site_config(request, forms, configs):
    """Gère la mise à jour de la configuration du site."""
    if forms['site_form'].validate_on_submit():
        site_config = configs['site']
        site_config.site_name = forms['site_form'].site_name.data
        db.session.commit()
        flash('Nom de l\'établissement mis à jour', 'success')
    return redirect(url_for('admin.dashboard'))

def handle_weather_config(request, forms, configs):
    """Gère la mise à jour de la configuration météo."""
    if forms['weather_form'].validate_on_submit():
        weather_config = configs['weather']
        weather_config.api_key = forms['weather_form'].api_key.data
        weather_config.city = forms['weather_form'].city.data
        weather_config.show_weather = forms['weather_form'].show_weather.data
        db.session.commit()
        current_app.config['WEATHER_API_KEY'] = weather_config.api_key
        current_app.config['WEATHER_CITY'] = weather_config.city
        flash('Configuration météo mise à jour', 'success')
    return redirect(url_for('admin.dashboard'))

def handle_menu_item_creation(request, forms, configs):
    """Gère la création d'un élément de menu."""
    if forms['menu_form'].validate_on_submit():
        # Utiliser le service menu pour ajouter l'élément
        menu_item = menu_service.add_menu_item(
            category=forms['menu_form'].category.data,
            name=forms['menu_form'].name.data,
            description=forms['menu_form'].description.data,
            icons=''.join(forms['menu_form'].icons.data),
            menu_date=forms['menu_form'].date.data
        )
        if menu_item:
            flash('Plat ajouté au menu', 'success')
        else:
            flash('Erreur lors de l\'ajout du plat', 'danger')
    return redirect(url_for('admin.dashboard'))

def handle_menu_item_deletion(request, forms, configs):
    """Gère la suppression d'un élément de menu."""
    item_id = request.form.get('delete_menu_item')
    
    # Utiliser le service menu pour supprimer l'élément
    if menu_service.delete_menu_item(item_id):
        flash('Plat supprimé du menu', 'success')
    else:
        flash('Erreur lors de la suppression du plat', 'danger')
    
    return redirect(url_for('admin.dashboard')) 