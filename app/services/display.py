"""Assemblage des données destinées à l'écran d'information."""

from datetime import UTC, date, datetime

from app.models import MENU_CATEGORIES, Absence, AppSettings, Event, MenuItem

DAYS = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi")


class DisplayService:
    def __init__(self, weather, transport) -> None:
        self.weather = weather
        self.transport = transport

    def snapshot(self) -> dict:
        settings = AppSettings.get()
        absences = {day: [] for day in DAYS}
        for record in Absence.query.order_by(Absence.professeur).all():
            for day in DAYS:
                if getattr(record, day):
                    absences[day].append({"id": record.id, "teacher": record.professeur})

        events = [
            {
                "id": item.id,
                "title": item.title,
                "date": item.date.isoformat(),
                "description": item.description,
            }
            for item in Event.get_upcoming_events(days=30)[:5]
        ]
        menu = (
            [
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "icons": item.icons,
                    "category": item.category,
                    "category_label": MENU_CATEGORIES[item.category]["label"],
                    "category_icon": MENU_CATEGORIES[item.category]["icon"],
                }
                for item in MenuItem.for_date(date.today())
            ]
            if settings.show_menu
            else []
        )

        weather = (
            self.weather.current(settings.weather_city)
            if settings.show_weather
            else {"status": "disabled", "data": None}
        )
        transport = (
            self.transport.arrivals(settings.cts_stop_code, settings.cts_vehicle_mode)
            if settings.show_transport
            else {"status": "disabled", "data": None}
        )
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "site": {"name": settings.site_name, "theme": "dark" if settings.dark_mode else "light"},
            "widgets": {
                "weather": settings.show_weather,
                "menu": settings.show_menu,
                "transport": settings.show_transport,
            },
            "absences": absences,
            "events": events,
            "menu": menu,
            "weather": weather,
            "transport": transport,
        }
