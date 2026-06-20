"""Timeout and cancellation boundaries for Mini."""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class TimeoutBoundary:
    """Run a callable with a hard timeout. Mini uses thread join, not process groups."""

    def run(self, func: Callable[[], T], timeout_seconds: float) -> T:
        result: list[T] = []
        error: list[BaseException] = []

        def target() -> None:
            try:
                result.append(func())
            except BaseException as exc:  # noqa: BLE001
                error.append(exc)

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout_seconds)
        if thread.is_alive():
            raise TimeoutError(f"Operation exceeded {timeout_seconds}s")
        if error:
            raise error[0]
        if not result:
            raise RuntimeError("Operation produced no result")
        return result[0]


class CancellationToken:
    def __init__(self) -> None:
        self._cancelled = threading.Event()

    def cancel(self) -> None:
        self._cancelled.set()

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled.is_set()

    def check(self) -> None:
        if self.is_cancelled:
            raise InterruptedError("Operation cancelled")
