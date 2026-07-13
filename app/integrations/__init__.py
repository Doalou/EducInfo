"""Adaptateurs des services externes."""

from app.integrations.cache import ExternalDataCache
from app.integrations.transport import TransportClient
from app.integrations.weather import WeatherClient

__all__ = ["ExternalDataCache", "TransportClient", "WeatherClient"]
