"""Client temps réel CTS configuré uniquement côté serveur."""

from __future__ import annotations

import re
from datetime import UTC, datetime

import requests
from dateutil.parser import isoparse
from requests.auth import HTTPBasicAuth

from app.integrations.cache import ExternalDataCache


class TransportClient:
    def __init__(self, cache: ExternalDataCache, base_url: str, api_token: str) -> None:
        self.cache = cache
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token

    def arrivals(self, stop_code: str, vehicle_mode: str = "undefined") -> dict:
        if not self.api_token or not stop_code:
            return {
                "status": "unavailable",
                "data": None,
                "updated_at": None,
                "error": "Transport non configuré",
            }
        key = f"transport:{stop_code}:{vehicle_mode}"
        return self.cache.get_or_fetch(key, 45, lambda: self._fetch(stop_code, vehicle_mode))

    def _fetch(self, stop_code: str, vehicle_mode: str) -> dict:
        params = {
            "MonitoringRef": stop_code,
            "MaximumStopVisits": 8,
            "PreviewInterval": "PT90M",
        }
        if vehicle_mode != "undefined":
            params["VehicleMode"] = vehicle_mode
        response = requests.get(
            f"{self.base_url}/v1/siri/2.0/stop-monitoring",
            params=params,
            auth=HTTPBasicAuth(self.api_token, ""),
            headers={"Accept": "application/json", "User-Agent": "EducInfo/3.0.0"},
            timeout=8,
        )
        response.raise_for_status()
        deliveries = response.json().get("ServiceDelivery", {}).get("StopMonitoringDelivery", [])
        visits = deliveries[0].get("MonitoredStopVisit", []) if deliveries else []
        line_styles = self._line_styles()
        arrivals = []
        now = datetime.now(UTC)
        for visit in visits:
            journey = visit.get("MonitoredVehicleJourney", {})
            call = journey.get("MonitoredCall", {})
            expected = call.get("ExpectedDepartureTime") or call.get("ExpectedArrivalTime")
            if not expected:
                continue
            when = isoparse(expected)
            minutes = max(0, int((when.astimezone(UTC) - now).total_seconds() / 60))
            line_ref = str(journey.get("LineRef") or "").split(":")[-1]
            line_name = str(journey.get("PublishedLineName") or line_ref or "—")
            style = line_styles.get(line_ref.casefold()) or line_styles.get(line_name.casefold()) or {}
            arrivals.append(
                {
                    "line": line_name,
                    "line_color": style.get("background"),
                    "line_text_color": style.get("foreground"),
                    "destination": str(journey.get("DestinationName") or "Destination inconnue"),
                    "minutes": minutes,
                    "expected_at": when.isoformat(),
                    "realtime": bool(call.get("Extension", {}).get("IsRealTime", False)),
                }
            )
        arrivals.sort(key=lambda item: item["minutes"])
        return {"stop_code": stop_code, "arrivals": arrivals[:5]}

    def _line_styles(self) -> dict[str, dict[str, str]]:
        result = self.cache.get_or_fetch("transport:line-styles", 86400, self._fetch_line_styles)
        return result.get("data") or {}

    def _fetch_line_styles(self) -> dict[str, dict[str, str]]:
        response = requests.get(
            f"{self.base_url}/v1/siri/2.0/lines-discovery",
            auth=HTTPBasicAuth(self.api_token, ""),
            headers={"Accept": "application/json", "User-Agent": "EducInfo/3.0.0"},
            timeout=8,
        )
        response.raise_for_status()
        delivery = response.json().get("LinesDelivery", {})
        lines = delivery.get("AnnotatedLineRef", []) if isinstance(delivery, dict) else []
        styles = {}
        for line in lines:
            extension = line.get("Extension") or {}
            background = self._color(extension.get("RouteColor"))
            foreground = self._color(extension.get("RouteTextColor"))
            reference = str(line.get("LineRef") or "").strip()
            if reference and background and foreground:
                styles[reference.casefold()] = {
                    "background": background,
                    "foreground": foreground,
                }
        return styles

    @staticmethod
    def _color(value) -> str | None:
        color = str(value or "").strip().lstrip("#")
        return f"#{color.upper()}" if re.fullmatch(r"[0-9a-fA-F]{6}", color) else None
