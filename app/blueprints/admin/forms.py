"""
Formulaires pour le blueprint d'administration.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, PasswordField
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired, Optional, URL, ValidationError, Length, EqualTo


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
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired(message="La date de l'événement est requise.")])
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
    description = TextAreaField('Description', validators=[Optional()])
    icons = SelectField('Icône (optionnel)', choices=[
        ('', 'Aucune'),
        ('🌱', '🌱 Végétarien'),
        ('🌿', '🌿 Végétalien'),
        ('🌶️', '🌶️ Épicé'),
        ('🚫🥜', '🚫🥜 Sans Arachide'),
        ('🐟', '🐟 Poisson'),
        ('🥬', '🥬 Bio')
    ], validators=[Optional()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired(message="La date est requise")])
    submit = SubmitField('Ajouter')


class ConfigForm(FlaskForm):
    """Formulaire de configuration du site."""
    site_name = StringField('Nom du site', validators=[DataRequired()])
    default_theme = SelectField('Thème par défaut', choices=[
        ('light', 'Clair'), 
        ('dark', 'Sombre'), 
        ('auto', 'Automatique (selon les préférences du système)')
    ])
    submit_config = SubmitField('Enregistrer')


class WeatherConfigForm(FlaskForm):
    """Formulaire de configuration du widget météo."""
    api_key = StringField('Clé API OpenWeatherMap', validators=[Optional()])
    city = StringField('Ville', validators=[Optional()])
    show_weather = BooleanField("Afficher le widget Météo sur la page d'accueil")
    submit_weather = SubmitField('Enregistrer')


class TransportConfigForm(FlaskForm):
    """Formulaire de configuration du widget transport."""
    show_transports = BooleanField('Afficher le widget Transports CTS')
    cts_api_token = StringField('Token API CTS', validators=[Optional()])
    cts_stop_code = StringField('Code arrêt CTS (3 chiffres)', validators=[Optional()], 
                               description='Format: 3 chiffres numériques (ex: 366 pour Lycée Couffignal)')
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
            # Validation du format du code d'arrêt (3 chiffres)
            if self.cts_stop_code.data and not (self.cts_stop_code.data.isdigit() and len(self.cts_stop_code.data) == 3):
                self.cts_stop_code.errors.append("Le code d'arrêt CTS doit être composé de 3 chiffres exactement (ex: 366).")
                return False
        return True 


class CTSForm(FlaskForm):
    """Formulaire de recherche et prévisualisation pour les arrêts CTS."""
    stop_code = StringField('Code Arrêt CTS (3 chiffres)', validators=[Optional()],
                           description='Format: 3 chiffres numériques (ex: 366, 001, 123)')
    vehicle_mode = SelectField('Mode de transport', choices=[
        ('', 'Tous'),
        ('bus', 'Bus'),
        ('tram', 'Tram'),
        ('undefined', 'Indéfini (Défaut API)')
    ], default='', validators=[Optional()])
    api_token = StringField('Token API CTS', validators=[Optional()])
    stop_display = StringField('Nom à afficher pour l\'arrêt', validators=[Optional()])
    submit_cts = SubmitField('Prévisualiser')
    submit_cts_save = SubmitField('Utiliser cet arrêt')


class ClearCacheForm(FlaskForm):
    """Formulaire pour vider le cache système."""
    submit = SubmitField('Vider le Cache')


class TestNotificationForm(FlaskForm):
    """Formulaire pour tester les notifications."""
    submit = SubmitField('Test Notifications')


class CreateUserForm(FlaskForm):
    """Formulaire de création d'un nouvel utilisateur."""
    identifiant = StringField('Identifiant', 
                             validators=[DataRequired(message="L'identifiant est requis"),
                                       Length(min=3, max=50, message="L'identifiant doit contenir entre 3 et 50 caractères")])
    password = PasswordField('Mot de passe', 
                            validators=[DataRequired(message="Le mot de passe est requis"),
                                      Length(min=6, message="Le mot de passe doit contenir au moins 6 caractères")])
    password_confirm = PasswordField('Confirmer le mot de passe',
                                   validators=[DataRequired(message="Veuillez confirmer le mot de passe"),
                                             EqualTo('password', message="Les mots de passe ne correspondent pas")])
    is_admin = BooleanField('Privilèges administrateur')
    is_active = BooleanField('Compte actif', default=True)
    submit = SubmitField('Créer l\'utilisateur')

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        # Par défaut, le compte est actif
        if not self.is_active.data and not self.errors:
            self.is_active.data = True


class EditUserForm(FlaskForm):
    """Formulaire d'édition d'un utilisateur existant."""
    identifiant = StringField('Identifiant', 
                             validators=[DataRequired(message="L'identifiant est requis"),
                                       Length(min=3, max=50, message="L'identifiant doit contenir entre 3 et 50 caractères")])
    new_password = PasswordField('Nouveau mot de passe (optionnel)', 
                                validators=[Optional(),
                                          Length(min=6, message="Le mot de passe doit contenir au moins 6 caractères")])
    new_password_confirm = PasswordField('Confirmer le nouveau mot de passe',
                                       validators=[Optional(),
                                                 EqualTo('new_password', message="Les mots de passe ne correspondent pas")])
    is_admin = BooleanField('Privilèges administrateur')
    is_active = BooleanField('Compte actif')
    submit = SubmitField('Modifier l\'utilisateur')


class DeleteUserForm(FlaskForm):
    """Formulaire de confirmation de suppression d'utilisateur."""
    user_id = IntegerField('ID Utilisateur', validators=[DataRequired()])
    confirm_delete = BooleanField('Je confirme vouloir supprimer cet utilisateur', 
                                 validators=[DataRequired(message="Vous devez confirmer la suppression")])
    submit = SubmitField('Supprimer définitivement') 