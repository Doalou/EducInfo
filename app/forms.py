from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, DateField, SubmitField, SelectField
from wtforms.fields import SelectMultipleField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp, EqualTo, Optional
from datetime import date
from app.models import ThemeConfig, MenuItem

class LoginForm(FlaskForm):
    identifiant = StringField('Identifiant', validators=[
        DataRequired(),
        Length(max=120)
    ])
    password = PasswordField('Mot de Passe', validators=[
        DataRequired(),
        Length(min=8, message="Le mot de passe doit contenir au moins 8 caractères"),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', 
               message="Le mot de passe doit contenir au moins une lettre et un chiffre")
    ])
    submit = SubmitField('Connexion')

class AbsenceForm(FlaskForm):
    professeur = StringField('Professeur', validators=[DataRequired()])
    jours = SelectMultipleField('Jours d\'absence', choices=[
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
    ])
    submit_absence = SubmitField('Ajouter / Modifier')
    
    def validate_professeur(self, field):
        if len(field.data.strip()) < 2:
            raise ValidationError('Le nom du professeur doit contenir au moins 2 caractères')

class WidgetConfigForm(FlaskForm):
    show_menu_cantine = BooleanField('Afficher le menu de la cantine')
    show_transports = BooleanField('Afficher les transports')
    cts_stop_code = StringField("Code d'arrêt CTS", validators=[Optional()])
    cts_vehicle_mode = SelectField(
        "Mode de transport",
        choices=[("undefined", "Indéfini"), ("bus", "Bus"), ("tram", "Tram")],
        default="undefined"
    )
    cts_api_token = StringField("Clé API CTS", validators=[Optional()])
    cts_stop_display = StringField("Texte à afficher (ex: 'Lycée')", validators=[Optional()])
    submit_widget = SubmitField('Enregistrer les paramètres')

class EventForm(FlaskForm):
    title = StringField('Titre', validators=[
        DataRequired(),
        Length(min=3, max=200)
    ])
    date = DateField('Date', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit_event = SubmitField('Ajouter l\'Événement')
    
    def validate_date(self, field):
        if field.data < date.today():
            raise ValidationError('La date doit être future')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mot de passe actuel', validators=[DataRequired()])
    new_password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(),
        Length(min=8, message="Le mot de passe doit contenir au moins 8 caractères"),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', 
               message="Le mot de passe doit contenir au moins une lettre et un chiffre")
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('new_password', message='Les mots de passe doivent correspondre')
    ])
    submit_password = SubmitField('Changer le mot de passe')

class ThemeConfigForm(FlaskForm):
    primary_color = SelectField('Couleur principale', 
                              choices=ThemeConfig.get_color_choices(),
                              validators=[DataRequired()])
    submit_theme = SubmitField('Enregistrer')

class SiteConfigForm(FlaskForm):
    site_name = StringField('Nom de l\'établissement', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    submit_site = SubmitField('Enregistrer')

class WeatherConfigForm(FlaskForm):
    api_key = StringField('Clé API OpenWeather', validators=[
        DataRequired(),
        Length(min=32, max=32, message="La clé API doit faire exactement 32 caractères")
    ])
    city = StringField('Ville', validators=[
        DataRequired(),
        Length(min=2, max=100, message="Le nom de la ville doit faire entre 2 et 100 caractères")
    ])
    show_weather = BooleanField('Afficher la météo')
    submit_weather = SubmitField('Mettre à jour la configuration météo')

# Formulaire pour la recherche CTS (pour prévisualiser des résultats)
class CTSForm(FlaskForm):
    stop_code = StringField("Code d'arrêt", validators=[DataRequired()])
    vehicle_mode = SelectField(
        "Mode de transport",
        choices=[("bus", "Bus"), ("tram", "Tram"), ("undefined", "Indéfini")],
        default="undefined"
    )
    submit_cts = SubmitField("Rechercher")
    submit_cts_save = SubmitField("Utiliser ce stop pour l'affichage")

class MenuItemForm(FlaskForm):
    category = SelectField('Catégorie', validators=[DataRequired()], 
                         choices=lambda: [(c[0], c[1]) for c in MenuItem.get_menu_categories()])
    name = StringField('Nom du plat', validators=[DataRequired(), Length(max=100)])
    description = StringField('Description', validators=[Optional(), Length(max=200)])
    icons = SelectMultipleField('Caractéristiques', 
                              choices=lambda: [(i[0], f"{i[0]} {i[1]}") for i in MenuItem.get_icons()])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    submit_menu_item = SubmitField('Ajouter au menu')
