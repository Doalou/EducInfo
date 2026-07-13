"""Configuration fonctionnelle non sensible, stockée dans SQLite."""

from app.extensions import db


class AppSettings(db.Model):
    __tablename__ = "app_settings"

    id = db.Column(db.Integer, primary_key=True, default=1)
    site_name = db.Column(db.String(100), nullable=False, default="EducInfo")
    weather_city = db.Column(db.String(100), nullable=False, default="Strasbourg")
    show_weather = db.Column(db.Boolean, nullable=False, default=True)
    show_menu = db.Column(db.Boolean, nullable=False, default=True)
    show_transport = db.Column(db.Boolean, nullable=False, default=False)
    dark_mode = db.Column(db.Boolean, nullable=False, default=False)
    cts_stop_code = db.Column(db.String(20), nullable=False, default="")
    cts_stop_label = db.Column(db.String(100), nullable=False, default="")
    cts_vehicle_mode = db.Column(db.String(20), nullable=False, default="undefined")

    __table_args__ = (db.CheckConstraint("id = 1", name="settings_singleton"),)

    @classmethod
    def get(cls) -> "AppSettings":
        settings = db.session.get(cls, 1)
        if settings is None:
            settings = cls(id=1)
            db.session.add(settings)
            db.session.commit()
        return settings
