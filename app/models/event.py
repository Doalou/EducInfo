"""
Modèle pour la gestion des événements scolaires.
"""
from datetime import date, timedelta
from app.extensions import db


class Event(db.Model):
    """
    Modèle représentant un événement scolaire (sortie, réunion, etc.).
    """
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, default="")

    def __repr__(self):
        """Représentation de l'objet Event"""
        return f'<Event {self.title} Date={self.date.strftime("%Y-%m-%d")}>'

    def is_future(self):
        """
        Vérifie si l'événement est dans le futur.
        
        Returns:
            bool: True si l'événement est aujourd'hui ou dans le futur
        """
        return self.date >= date.today()

    @staticmethod
    def get_upcoming_events(days=30):
        """
        Récupère les événements à venir dans les prochains jours.
        
        Args:
            days (int): Nombre de jours à considérer (par défaut 30)
            
        Returns:
            list: Liste des événements à venir triés par date
        """
        future_date = date.today() + timedelta(days=days)
        return Event.query.filter(
            Event.date >= date.today(),
            Event.date <= future_date
        ).order_by(Event.date).all() 