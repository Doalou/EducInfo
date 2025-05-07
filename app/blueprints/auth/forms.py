"""
Formulaires pour le blueprint d'authentification.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    """Formulaire de connexion à l'application."""
    identifiant = StringField('Nom d\'utilisateur', validators=[
        DataRequired(message="Le nom d'utilisateur est requis")
    ])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(message="Le mot de passe est requis")
    ])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion')


class ChangePasswordForm(FlaskForm):
    """Formulaire de changement de mot de passe."""
    current_password = PasswordField('Mot de passe actuel', validators=[
        DataRequired(message="Le mot de passe actuel est requis")
    ])
    new_password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(message="Le nouveau mot de passe est requis"),
        Length(min=8, message="Le mot de passe doit contenir au moins 8 caractères")
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(message="La confirmation du mot de passe est requise"),
        EqualTo('new_password', message="Les mots de passe ne correspondent pas")
    ])
    submit = SubmitField('Changer le mot de passe') 