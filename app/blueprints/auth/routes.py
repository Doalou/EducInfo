"""
Routes pour le blueprint d'authentification.
Ce module définit les routes et la logique d'authentification des utilisateurs.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse

from app.blueprints.auth import bp
from app.blueprints.auth.forms import LoginForm, ChangePasswordForm
from app.models.user import User
from app.extensions import db, logger

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Route pour la connexion des utilisateurs."""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.identifiant.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            user.update_last_login()
            logger.info(f"Connexion réussie de l'utilisateur: {user.username}")
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Identifiants invalides', 'danger')
            logger.warning(f"Tentative de connexion échouée pour: {form.identifiant.data}")
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Route pour la déconnexion des utilisateurs."""
    logger.info(f"Déconnexion de l'utilisateur: {current_user.username}")
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('public.home'))

def handle_password_change(form):
    """
    Gère le changement de mot de passe d'un utilisateur.
    
    Args:
        form (ChangePasswordForm): Formulaire de changement de mot de passe validé
        
    Returns:
        bool: True si le changement a réussi, False sinon
    """
    if form.validate_on_submit():
        if current_user and current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            logger.info(f"Mot de passe modifié pour l'utilisateur: {current_user.username}")
            return True
        else:
            logger.warning(f"Échec du changement de mot de passe pour l'utilisateur: {current_user.username}")
            flash('Le mot de passe actuel est incorrect.', 'danger')
            return False
    return False 