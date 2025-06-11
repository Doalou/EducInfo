"""Modèle pour la gestion des absences des professeurs optimisé."""
from app.extensions import db


class Absence(db.Model):
    """Modèle d'absence d'un professeur avec optimisations de performance."""
    __tablename__ = 'absences'
    
    id = db.Column(db.Integer, primary_key=True)
    professeur = db.Column(db.String(100), nullable=False, index=True)
    lundi = db.Column(db.Boolean, default=False, index=True)
    mardi = db.Column(db.Boolean, default=False, index=True)
    mercredi = db.Column(db.Boolean, default=False, index=True)
    jeudi = db.Column(db.Boolean, default=False, index=True)
    vendredi = db.Column(db.Boolean, default=False, index=True)
    samedi = db.Column(db.Boolean, default=False, index=True)
    
    # Index composite optimisé pour les requêtes
    __table_args__ = (
        db.Index('idx_professeur_jours', 'professeur', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'),
    )
    
    # Cache statique des jours pour éviter la répétition
    _JOURS = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
    
    def __repr__(self):
        days = [d for d in self._JOURS if getattr(self, d)]
        return f'<Absence Prof={self.professeur} Jours={",".join(days) or "Aucun"}>'
    
    def get_days_as_list(self):
        """Retourne la liste des jours d'absence."""
        return [day for day in self._JOURS if getattr(self, day)]
    
    def get_days_as_text(self):
        """Retourne une représentation textuelle des jours d'absence."""
        days = self.get_days_as_list()
        return "Aucun jour" if not days else ", ".join(day.title() for day in days)
    
    @classmethod
    def get_absences_by_day(cls, day):
        """Retourne toutes les absences pour un jour donné."""
        return cls.query.filter(getattr(cls, day) == True).all()
    
    @classmethod
    def get_all_active_absences(cls):
        """Retourne toutes les absences actives."""
        return cls.query.filter(
            db.or_(
                cls.lundi == True,
                cls.mardi == True,
                cls.mercredi == True,
                cls.jeudi == True,
                cls.vendredi == True,
                cls.samedi == True
            )
        ).all() 