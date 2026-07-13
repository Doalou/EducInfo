"""Cache mémoire borné avec repli sur la dernière donnée fiable."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import RLock
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    updated_at: datetime


class ExternalDataCache:
    def __init__(self) -> None:
        self._entries: dict[str, CacheEntry] = {}
        self._lock = RLock()

    def get_or_fetch(self, key: str, ttl: int, fetcher: Callable[[], Any]) -> dict[str, Any]:
        now = datetime.now(UTC)
        with self._lock:
            entry = self._entries.get(key)
            if entry and now - entry.updated_at < timedelta(seconds=ttl):
                return self._result("fresh", entry)

        try:
            value = fetcher()
            entry = CacheEntry(value=value, updated_at=now)
            with self._lock:
                self._entries[key] = entry
            return self._result("fresh", entry)
        except Exception:
            with self._lock:
                stale = self._entries.get(key)
            if stale:
                result = self._result("stale", stale)
                result["error"] = "external_service_error"
                return result
            return {
                "status": "unavailable",
                "data": None,
                "updated_at": None,
                "error": "external_service_error",
            }

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()

    @staticmethod
    def _result(status: str, entry: CacheEntry) -> dict[str, Any]:
        return {
            "status": status,
            "data": entry.value,
            "updated_at": entry.updated_at.isoformat(),
        }
