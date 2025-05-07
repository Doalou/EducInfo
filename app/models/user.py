"""
Modèle d'utilisateur pour l'authentification et la gestion des droits.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    """
    Modèle utilisateur qui représente un utilisateur du système.
    Hérite de UserMixin pour l'intégration avec Flask-Login.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """Représentation de l'objet User"""
        return f'<User {self.username} ({"admin" if self.is_admin else "user"})>'

    def set_password(self, password):
        """
        Définit le mot de passe en le hashant.
        
        Args:
            password (str): Le mot de passe en clair
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Vérifie si le mot de passe correspond au hash stocké.
        
        Args:
            password (str): Le mot de passe à vérifier
            
        Returns:
            bool: True si le mot de passe est correct, False sinon
        """
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Met à jour la date de dernière connexion de l'utilisateur"""
        self.last_login = datetime.utcnow()
        db.session.commit() 