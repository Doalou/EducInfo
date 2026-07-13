from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, Regexp


class SettingsForm(FlaskForm):
    site_name = StringField("Nom de l'établissement", validators=[DataRequired(), Length(max=100)])
    weather_city = StringField("Ville météo", validators=[DataRequired(), Length(max=100)])
    show_weather = BooleanField("Afficher la météo")
    show_menu = BooleanField("Afficher le menu")
    show_transport = BooleanField("Afficher les transports")
    dark_mode = BooleanField("Mode sombre de l’écran")
    cts_stop_code = StringField(
        "Code arrêt CTS",
        validators=[Optional(), Regexp(r"^\d{3}$", message="Le code doit contenir 3 chiffres.")],
    )
    cts_stop_label = StringField("Nom de l'arrêt", validators=[Optional(), Length(max=100)])
    cts_vehicle_mode = SelectField("Mode", choices=[("undefined", "Tous"), ("bus", "Bus"), ("tram", "Tram")])
    submit = SubmitField("Enregistrer")


class UserForm(FlaskForm):
    username = StringField("Identifiant", validators=[DataRequired(), Length(min=3, max=80)])
    role = SelectField("Rôle", choices=[("editor", "Éditeur"), ("admin", "Administrateur")])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=12)])
    password_confirm = PasswordField("Confirmation", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Créer")


class UserUpdateForm(FlaskForm):
    role = SelectField("Rôle", choices=[("editor", "Éditeur"), ("admin", "Administrateur")])
    is_active = BooleanField("Compte actif")
    submit = SubmitField("Enregistrer")


class UserPasswordForm(FlaskForm):
    password = PasswordField("Nouveau mot de passe", validators=[DataRequired(), Length(min=12)])
    password_confirm = PasswordField("Confirmation", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Changer le mot de passe")
