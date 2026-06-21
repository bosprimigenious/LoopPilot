"""Cross-process file locks for Mini CLI safety."""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from loop_pilot.domain.errors import ErrorCode, LoopPilotError


class FileLockStore:
    """Exclusive lock files — safe across processes on the same machine."""

    def __init__(self, lock_dir: Path, timeout_seconds: float = 30.0, poll_seconds: float = 0.05) -> None:
        self.lock_dir = lock_dir
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = timeout_seconds
        self.poll_seconds = poll_seconds
        self._held_paths: list[Path] = []

    def _lock_path(self, key: str) -> Path:
        safe = key.replace(":", "_").replace("/", "_").replace("\\", "_")
        return self.lock_dir / f"{safe}.lock"

    @contextmanager
    def acquire(self, key: str, holder: str) -> Generator[None, None, None]:
        path = self._lock_path(key)
        deadline = time.monotonic() + self.timeout_seconds
        fd: int | None = None
        while time.monotonic() < deadline:
            try:
                fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, holder.encode("utf-8"))
                self._held_paths.append(path)
                break
            except FileExistsError:
                time.sleep(self.poll_seconds)
        else:
            raise LoopPilotError(
                code=ErrorCode.TOOL_FAILED,
                component="locks",
                message=f"Lock timeout for key: {key}",
                retryable=False,
            )
        try:
            yield
        finally:
            if fd is not None:
                os.close(fd)
            if path.exists():
                path.unlink(missing_ok=True)
            if path in self._held_paths:
                self._held_paths.remove(path)

    def is_held(self, key: str) -> bool:
        return self._lock_path(key).exists()


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def clear_stale_locks(lock_dir: Path) -> None:
    """Remove lock files left by dead processes; skip locks held by live PIDs."""
    if not lock_dir.is_dir():
        return
    for lock_path in lock_dir.glob("*.lock"):
        try:
            payload = lock_path.read_text(encoding="utf-8").strip()
            if ":" in payload:
                pid_str, _holder = payload.split(":", 1)
                try:
                    pid = int(pid_str)
                except ValueError:
                    pid = None
                if pid is not None and _pid_alive(pid):
                    continue
            lock_path.unlink(missing_ok=True)
        except PermissionError:
            pass
        except OSError:
            pass
