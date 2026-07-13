from flask import current_app, flash, redirect, render_template, url_for

from app.blueprints.content import bp
from app.blueprints.content.forms import AbsenceForm, EventForm, MenuForm
from app.extensions import db
from app.models import Absence, Event, MenuItem
from app.utils.decorators import editor_required


@bp.get("")
@editor_required
def index():
    return render_template(
        "admin/content.html",
        absences=Absence.query.order_by(Absence.professeur).all(),
        events=Event.query.order_by(Event.date).all(),
        menu_items=MenuItem.query.order_by(MenuItem.date.desc(), MenuItem.category).limit(50).all(),
        absence_form=AbsenceForm(),
        event_form=EventForm(),
        menu_form=MenuForm(),
    )


@bp.post("/absences")
@editor_required
def save_absence():
    form = AbsenceForm()
    if form.validate_on_submit():
        name = form.professeur.data.strip()
        item = Absence.query.filter(db.func.lower(Absence.professeur) == name.lower()).first()
        if item is None:
            item = Absence(professeur=name)
            db.session.add(item)
        for day in ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"):
            setattr(item, day, getattr(form, day).data)
        db.session.commit()
        flash("Absence enregistrée.", "success")
    else:
        flash("Formulaire d'absence invalide.", "error")
    return redirect(url_for("content.index"))


@bp.post("/absences/<int:item_id>/delete")
@editor_required
def delete_absence(item_id):
    db.session.delete(db.get_or_404(Absence, item_id))
    db.session.commit()
    flash("Absence supprimée.", "success")
    return redirect(url_for("content.index"))


@bp.post("/events")
@editor_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        db.session.add(
            Event(title=form.title.data.strip(), date=form.date.data, description=form.description.data or "")
        )
        db.session.commit()
        flash("Événement ajouté.", "success")
    else:
        flash("Formulaire d'événement invalide.", "error")
    return redirect(url_for("content.index"))


@bp.post("/events/<int:item_id>/delete")
@editor_required
def delete_event(item_id):
    db.session.delete(db.get_or_404(Event, item_id))
    db.session.commit()
    return redirect(url_for("content.index"))


@bp.post("/menu")
@editor_required
def create_menu_item():
    form = MenuForm()
    if form.validate_on_submit():
        db.session.add(
            MenuItem(
                name=form.name.data.strip(),
                category=form.category.data,
                date=form.date.data,
                description=form.description.data or "",
                icons=form.icons.data or "",
            )
        )
        db.session.commit()
        flash("Plat ajouté.", "success")
    else:
        flash("Formulaire de menu invalide.", "error")
    return redirect(url_for("content.index"))


@bp.post("/menu/<int:item_id>/delete")
@editor_required
def delete_menu_item(item_id):
    db.session.delete(db.get_or_404(MenuItem, item_id))
    db.session.commit()
    current_app.extensions["external_cache"].clear()
    return redirect(url_for("content.index"))
