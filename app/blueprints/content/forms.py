from datetime import date

from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Optional

from app.models import MENU_CATEGORIES


class AbsenceForm(FlaskForm):
    professeur = StringField("Professeur", validators=[DataRequired(), Length(max=100)])
    lundi = BooleanField("Lundi")
    mardi = BooleanField("Mardi")
    mercredi = BooleanField("Mercredi")
    jeudi = BooleanField("Jeudi")
    vendredi = BooleanField("Vendredi")
    samedi = BooleanField("Samedi")
    submit = SubmitField("Enregistrer")

    def validate(self, extra_validators=None):
        valid = super().validate(extra_validators)
        if not any(
            getattr(self, day).data for day in ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi")
        ):
            self.professeur.errors.append("Sélectionnez au moins un jour.")
            return False
        return valid


class EventForm(FlaskForm):
    title = StringField("Titre", validators=[DataRequired(), Length(max=200)])
    date = DateField("Date", validators=[DataRequired()], default=date.today)
    description = TextAreaField("Description", validators=[Optional()])
    submit = SubmitField("Ajouter")


class MenuForm(FlaskForm):
    name = StringField("Plat", validators=[DataRequired(), Length(max=120)])
    category = SelectField(
        "Catégorie",
        coerce=int,
        choices=[(key, f"{value['icon']} {value['label']}") for key, value in MENU_CATEGORIES.items()],
    )
    date = DateField("Date", validators=[DataRequired()], default=date.today)
    description = TextAreaField("Description", validators=[Optional()])
    icons = StringField("Repères", validators=[Optional(), Length(max=32)])
    submit = SubmitField("Ajouter")
