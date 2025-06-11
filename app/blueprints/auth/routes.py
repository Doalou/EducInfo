"""
Routes pour le blueprint d'authentification.
Ce module définit les routes et la logique d'authentification des utilisateurs.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.blueprints.auth import bp
from app.blueprints.auth.forms import LoginForm, ChangePasswordForm
from app.models.user import User
from app.extensions import db, logger

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Connexion d'un utilisateur."""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.identifiant.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            user.update_last_login()
            db.session.commit()  # Sauvegarder la date de dernière connexion
            
            # Redirection vers l'interface d'administration après connexion
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('admin.dashboard')
            return redirect(next_page)
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
    
    return render_template('auth/login.html', title='Connexion', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Déconnexion de l'utilisateur."""
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'info')
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