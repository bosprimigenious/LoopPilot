"""Local locks suitable for tests and Mini."""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Generator

from loop_pilot.domain.errors import ErrorCode, LoopPilotError


class LocalLockStore:
    def __init__(self) -> None:
        self._locks: dict[str, threading.Lock] = {}
        self._holders: dict[str, str] = {}
        self._meta = threading.Lock()

    def _get_lock(self, key: str) -> threading.Lock:
        with self._meta:
            if key not in self._locks:
                self._locks[key] = threading.Lock()
            return self._locks[key]

    @contextmanager
    def acquire(self, key: str, holder: str) -> Generator[None, None, None]:
        lock = self._get_lock(key)
        acquired = lock.acquire(blocking=False)
        if not acquired:
            raise LoopPilotError(
                code=ErrorCode.TOOL_FAILED,
                component="locks",
                message=f"Lock already held: {key}",
                retryable=False,
            )
        with self._meta:
            self._holders[key] = holder
        try:
            yield
        finally:
            with self._meta:
                self._holders.pop(key, None)
            lock.release()

    def is_held(self, key: str) -> bool:
        lock = self._get_lock(key)
        return lock.locked()

    def holder(self, key: str) -> str | None:
        return self._holders.get(key)

    def release_all(self) -> None:
        with self._meta:
            self._holders.clear()
