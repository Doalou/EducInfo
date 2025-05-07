"""
Modèle pour la gestion des absences des professeurs.
"""
from app.extensions import db


class Absence(db.Model):
    """
    Modèle qui représente l'absence d'un professeur sur différents jours de la semaine.
    """
    __tablename__ = 'absences'
    
    id = db.Column(db.Integer, primary_key=True)
    professeur = db.Column(db.String(100), nullable=False)
    lundi = db.Column(db.Boolean, default=False)
    mardi = db.Column(db.Boolean, default=False)
    mercredi = db.Column(db.Boolean, default=False)
    jeudi = db.Column(db.Boolean, default=False)
    vendredi = db.Column(db.Boolean, default=False)
    samedi = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        """Représentation de l'objet Absence"""
        days = [d for d in ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'] if getattr(self, d)]
        return f'<Absence Prof={self.professeur} Jours={",".join(days) or "Aucun"}>'
    
    def get_days_as_list(self):
        """
        Retourne la liste des jours d'absence.
        
        Returns:
            list: Liste des jours d'absence
        """
        return [
            day for day in ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'] 
            if getattr(self, day)
        ]
    
    def get_days_as_text(self):
        """
        Retourne une représentation textuelle des jours d'absence.
        
        Returns:
            str: Texte formaté des jours d'absence
        """
        days = self.get_days_as_list()
        if not days:
            return "Aucun jour"
        return ", ".join(day.title() for day in days)
    
    @classmethod
    def get_absences_by_day(cls, day):
        """
        Retourne toutes les absences pour un jour donné.
        
        Args:
            day (str): Jour de la semaine (lundi, mardi, etc.)
            
        Returns:
            list: Liste des absences pour ce jour
        """
        return cls.query.filter(getattr(cls, day) == True).all()
    
    @classmethod
    def get_all_active_absences(cls):
        """
        Retourne toutes les absences actives (au moins un jour sélectionné).
        
        Returns:
            list: Liste des absences actives
        """
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