"""
Formulaires pour le blueprint d'administration.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired, Optional, URL, ValidationError


class AbsenceForm(FlaskForm):
    """Formulaire de gestion des absences des professeurs."""
    professeur = StringField('Professeur', validators=[DataRequired(message="Le nom du professeur est requis")])
    lundi = BooleanField('Lundi')
    mardi = BooleanField('Mardi')
    mercredi = BooleanField('Mercredi')
    jeudi = BooleanField('Jeudi')
    vendredi = BooleanField('Vendredi')
    samedi = BooleanField('Samedi')
    submit = SubmitField('Ajouter')
    
    def validate_on_submit(self):
        result = super().validate_on_submit()
        if result and not any([self.lundi.data, self.mardi.data, self.mercredi.data, 
                              self.jeudi.data, self.vendredi.data, self.samedi.data]):
            self.lundi.errors = ["Veuillez sélectionner au moins un jour d'absence"]
            return False
        return result


class EventForm(FlaskForm):
    """Formulaire de gestion des événements."""
    title = StringField('Titre', validators=[DataRequired(message="Le titre de l'événement est requis")])
    date = DateField('Date', format='%d/%m/%Y', validators=[DataRequired(message="La date de l'événement est requise (format JJ/MM/AAAA).")])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Ajouter')


class MenuItemForm(FlaskForm):
    """Formulaire d'ajout d'élément au menu de la cantine."""
    name = StringField('Nom du plat', validators=[DataRequired(message="Le nom du plat est requis")])
    category = SelectField('Catégorie', choices=[
        (1, '🥗 Entrée'), 
        (2, '🍖 Plat principal'), 
        (3, '🧀 Fromage'), 
        (4, '🍦 Dessert')
    ], coerce=int)
    icons = SelectField('Icône (optionnel)', choices=[
        ('', 'Aucune'),
        ('🌱', '🌱 Végétarien'),
        ('🌿', '🌿 Végétalien'),
        ('🌶️', '🌶️ Épicé'),
        ('🚫🥜', '🚫🥜 Sans Arachide'),
        ('🐟', '🐟 Poisson'),
        ('🥬', '🥬 Bio')
    ], validators=[Optional()])
    submit = SubmitField('Ajouter')


class ConfigForm(FlaskForm):
    """Formulaire de configuration du site."""
    site_name = StringField('Nom du site', validators=[DataRequired()])
    show_weather = BooleanField('Afficher le widget météo')
    show_menu_cantine = BooleanField('Afficher le menu de la cantine')
    default_theme = SelectField('Thème par défaut', choices=[
        ('light', 'Clair'), 
        ('dark', 'Sombre'), 
        ('auto', 'Automatique (selon les préférences du système)')
    ])
    submit_config = SubmitField('Enregistrer')


class WeatherConfigForm(FlaskForm):
    """Formulaire de configuration du widget météo."""
    weather_api_key = StringField('Clé API OpenWeatherMap', validators=[DataRequired()])
    weather_city = StringField('Ville', validators=[DataRequired()])
    show_weather = BooleanField("Afficher le widget Météo sur la page d'accueil")
    submit_weather = SubmitField('Enregistrer')


class TransportConfigForm(FlaskForm):
    """Formulaire de configuration du widget transport."""
    show_transports = BooleanField('Afficher le widget Transports CTS')
    cts_api_token = StringField('Token API CTS', validators=[Optional()])
    cts_stop_code = StringField('Code arrêt CTS', validators=[Optional()])
    cts_stop_display = StringField('Nom à afficher pour l\'arrêt (optionnel)', validators=[Optional()])
    cts_vehicle_mode = SelectField('Mode de transport par défaut', choices=[
        ('bus', 'Bus'),
        ('tram', 'Tram'),
        ('undefined', 'Tous (Bus & Tram)')
    ], default='undefined', validators=[Optional()])
    show_menu_cantine = BooleanField('Afficher le widget Menu Cantine')
    submit_transport = SubmitField('Enregistrer')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        if self.show_transports.data:
            if not self.cts_api_token.data:
                self.cts_api_token.errors.append("Le token API CTS est requis si le widget transport est affiché.")
                return False
            if not self.cts_stop_code.data:
                self.cts_stop_code.errors.append("Le code d'arrêt CTS est requis si le widget transport est affiché.")
                return False
        return True 


class CTSForm(FlaskForm):
    """Formulaire de recherche et prévisualisation pour les arrêts CTS."""
    stop_code = StringField('Code Arrêt CTS', validators=[Optional()])
    vehicle_mode = SelectField('Mode de transport', choices=[
        ('', 'Tous'),
        ('bus', 'Bus'),
        ('tram', 'Tram'),
        ('undefined', 'Indéfini (Défaut API)')
    ], default='', validators=[Optional()])
    submit_cts = SubmitField('Prévisualiser')
    submit_cts_save = SubmitField('Utiliser cet arrêt') 