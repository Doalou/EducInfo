"""Client OpenWeather sans données fictives implicites."""

from __future__ import annotations

from datetime import UTC, datetime

import requests

from app.integrations.cache import ExternalDataCache


class WeatherClient:
    def __init__(self, cache: ExternalDataCache, api_key: str, demo_mode: bool = False) -> None:
        self.cache = cache
        self.api_key = api_key
        self.demo_mode = demo_mode

    def current(self, city: str) -> dict:
        if self.demo_mode:
            return {
                "status": "demo",
                "updated_at": datetime.now(UTC).isoformat(),
                "data": {
                    "city": city,
                    "temperature": 20,
                    "feels_like": 20,
                    "humidity": 50,
                    "description": "Données de démonstration",
                    "icon": "☀️",
                },
            }
        if not self.api_key:
            return {
                "status": "unavailable",
                "data": None,
                "updated_at": None,
                "error": "Clé OpenWeather non configurée",
            }
        return self.cache.get_or_fetch(f"weather:{city.lower()}", 900, lambda: self._fetch(city))

    def _fetch(self, city: str) -> dict:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": self.api_key, "units": "metric", "lang": "fr"},
            timeout=8,
        )
        response.raise_for_status()
        payload = response.json()
        weather = payload["weather"][0]
        return {
            "city": payload.get("name", city),
            "temperature": round(payload["main"]["temp"]),
            "feels_like": round(payload["main"]["feels_like"]),
            "humidity": payload["main"]["humidity"],
            "description": weather["description"].capitalize(),
            "icon": self._icon(weather.get("id", 800)),
        }

    @staticmethod
    def _icon(code: int) -> str:
        if code < 300:
            return "⛈️"
        if code < 600:
            return "🌧️"
        if code < 700:
            return "❄️"
        if code < 800:
            return "🌫️"
        if code == 800:
            return "☀️"
        return "☁️"
