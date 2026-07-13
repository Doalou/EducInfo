from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Identifiant", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    remember = BooleanField("Rester connecté")
    submit = SubmitField("Se connecter")
