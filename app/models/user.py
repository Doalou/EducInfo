"""Modèle d'utilisateur optimisé pour l'authentification."""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    """Modèle utilisateur avec intégration Flask-Login optimisée."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_admin = db.Column(db.Boolean, default=False, index=True)

    def __repr__(self):
        return f'<User {self.username} ({"admin" if self.is_admin else "user"})>'

    @property
    def role(self):
        """Retourne le rôle de l'utilisateur."""
        return "admin" if self.is_admin else "user"

    @property
    def identifiant(self):
        """Alias pour username."""
        return self.username

    @property
    def password(self):
        """Alias pour password_hash."""
        return self.password_hash

    def set_password(self, password):
        """Définit le mot de passe en le hashant."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie si le mot de passe correspond au hash stocké."""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Met à jour la date de dernière connexion."""
        self.last_login = datetime.utcnow() 