"""Protections applicatives légères adaptées à une instance unique."""

from collections import defaultdict, deque
from threading import RLock
from time import monotonic


class LoginThrottle:
    def __init__(self, limit: int = 5, window: int = 60) -> None:
        self.limit = limit
        self.window = window
        self._attempts = defaultdict(deque)
        self._lock = RLock()

    def allowed(self, key: str) -> bool:
        with self._lock:
            self._prune(key)
            return len(self._attempts[key]) < self.limit

    def failed(self, key: str) -> None:
        with self._lock:
            self._prune(key)
            self._attempts[key].append(monotonic())

    def succeeded(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)

    def _prune(self, key: str) -> None:
        threshold = monotonic() - self.window
        attempts = self._attempts[key]
        while attempts and attempts[0] < threshold:
            attempts.popleft()
