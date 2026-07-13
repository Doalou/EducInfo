from datetime import UTC, datetime

from app.integrations.cache import ExternalDataCache
from app.integrations.transport import TransportClient
from app.integrations.weather import WeatherClient


def test_cache_returns_fresh_and_then_stale(monkeypatch):
    cache = ExternalDataCache()
    assert cache.get_or_fetch("key", 60, lambda: {"value": 1})["status"] == "fresh"
    entry = cache._entries["key"]
    entry.updated_at = datetime(2000, 1, 1, tzinfo=UTC)
    result = cache.get_or_fetch("key", 1, lambda: (_ for _ in ()).throw(RuntimeError("offline")))
    assert result["status"] == "stale"
    assert result["data"] == {"value": 1}


def test_cache_unavailable_without_previous_value():
    result = ExternalDataCache().get_or_fetch(
        "key", 1, lambda: (_ for _ in ()).throw(RuntimeError("offline"))
    )
    assert result["status"] == "unavailable"
    assert result["error"] == "external_service_error"


def test_cache_never_exposes_external_exception_details():
    api_key = "super-secret-api-key"
    result = ExternalDataCache().get_or_fetch(
        "weather", 1, lambda: (_ for _ in ()).throw(RuntimeError(f"url?appid={api_key}"))
    )
    assert api_key not in str(result)


def test_weather_requires_key_and_demo_is_explicit():
    cache = ExternalDataCache()
    assert WeatherClient(cache, "").current("Strasbourg")["status"] == "unavailable"
    demo = WeatherClient(cache, "", demo_mode=True).current("Strasbourg")
    assert demo["status"] == "demo"
    assert "démonstration" in demo["data"]["description"]


def test_weather_formats_remote_payload(mocker):
    response = mocker.Mock()
    response.json.return_value = {
        "name": "Strasbourg",
        "main": {"temp": 19.6, "feels_like": 19.2, "humidity": 62},
        "weather": [{"id": 800, "description": "ciel clair"}],
    }
    mocker.patch("requests.get", return_value=response)
    result = WeatherClient(ExternalDataCache(), "key").current("Strasbourg")
    assert result["data"]["temperature"] == 20
    assert result["data"]["icon"] == "☀️"


def test_transport_requires_server_configuration():
    result = TransportClient(ExternalDataCache(), "https://example.test", "").arrivals("123")
    assert result["status"] == "unavailable"


def test_transport_formats_arrivals(mocker):
    response = mocker.Mock()
    response.json.return_value = {
        "ServiceDelivery": {
            "StopMonitoringDelivery": [
                {
                    "MonitoredStopVisit": [
                        {
                            "MonitoredVehicleJourney": {
                                "PublishedLineName": "A",
                                "DestinationName": "Centre",
                                "MonitoredCall": {
                                    "ExpectedDepartureTime": "2099-01-01T12:00:00+00:00",
                                    "Extension": {"IsRealTime": True},
                                },
                            }
                        }
                    ]
                }
            ]
        }
    }
    mocker.patch("requests.get", return_value=response)
    result = TransportClient(ExternalDataCache(), "https://example.test", "secret").arrivals("123")
    assert result["status"] == "fresh"
    assert result["data"]["arrivals"][0]["line"] == "A"


def test_transport_uses_official_line_colors(mocker):
    stop_response = mocker.Mock()
    stop_response.json.return_value = {
        "ServiceDelivery": {
            "StopMonitoringDelivery": [
                {
                    "MonitoredStopVisit": [
                        {
                            "MonitoredVehicleJourney": {
                                "LineRef": "A",
                                "PublishedLineName": "A",
                                "DestinationName": "Parc des Sports",
                                "MonitoredCall": {"ExpectedDepartureTime": "2099-01-01T12:00:00+00:00"},
                            }
                        }
                    ]
                }
            ]
        }
    }
    lines_response = mocker.Mock()
    lines_response.json.return_value = {
        "LinesDelivery": {
            "AnnotatedLineRef": [
                {
                    "LineRef": "A",
                    "Extension": {"RouteColor": "E10D19", "RouteTextColor": "FFFFFF"},
                }
            ]
        }
    }
    mocker.patch("requests.get", side_effect=[stop_response, lines_response])
    result = TransportClient(ExternalDataCache(), "https://example.test", "secret").arrivals("123")
    arrival = result["data"]["arrivals"][0]
    assert arrival["line_color"] == "#E10D19"
    assert arrival["line_text_color"] == "#FFFFFF"


def test_transport_rejects_invalid_colors():
    assert TransportClient._color("not-a-color") is None
