"""Cross-process file locks for Mini CLI safety."""

from __future__ import annotations

import ctypes
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from loop_pilot.domain.errors import ErrorCode, LoopPilotError


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True


def clear_stale_locks(lock_dir: Path) -> None:
    """Remove lock files left behind by dead processes."""
    if not lock_dir.is_dir():
        return
    store = FileLockStore(lock_dir, timeout_seconds=0.1)
    for lock_path in lock_dir.glob("*.lock"):
        store._clear_stale_lock(lock_path)


_REPO_LOCK_DIRS = (Path("var/state/locks"), Path("var/locks"))


def clear_repo_runtime_locks(repo_root: Path) -> None:
    """Clear stale locks under default repo runtime lock dirs."""
    for rel in _REPO_LOCK_DIRS:
        clear_stale_locks(repo_root / rel)


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

    def _encode_payload(self, holder: str) -> bytes:
        return f"{os.getpid()}:{holder}".encode("utf-8")

    def _lock_is_stale(self, path: Path) -> bool:
        try:
            raw = path.read_text(encoding="utf-8").strip()
        except OSError:
            return False
        if not raw:
            return False
        pid_part, _, holder = raw.partition(":")
        if not pid_part.isdigit() or not holder:
            return False
        pid = int(pid_part)
        if pid <= 0:
            return False
        return not _pid_alive(pid)

    def _clear_stale_lock(self, path: Path) -> None:
        if path.exists() and self._lock_is_stale(path):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass

    @contextmanager
    def acquire(self, key: str, holder: str) -> Generator[None, None, None]:
        path = self._lock_path(key)
        deadline = time.monotonic() + self.timeout_seconds
        fd: int | None = None
        while time.monotonic() < deadline:
            self._clear_stale_lock(path)
            try:
                fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, self._encode_payload(holder))
                self._held_paths.append(path)
                break
            except FileExistsError:
                self._clear_stale_lock(path)
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
                fd = None
            if path.exists():
                path.unlink(missing_ok=True)
            if path in self._held_paths:
                self._held_paths.remove(path)

    def is_held(self, key: str) -> bool:
        path = self._lock_path(key)
        self._clear_stale_lock(path)
        return path.exists()
