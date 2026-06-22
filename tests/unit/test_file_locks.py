"""File lock stale detection and cleanup."""

from __future__ import annotations

import os
from pathlib import Path

from loop_pilot.runtime.locks import FileLockStore, clear_stale_locks


def test_stale_lock_from_dead_pid_is_cleared(tmp_path: Path) -> None:
    lock_dir = tmp_path / "locks"
    lock_dir.mkdir()
    stale = lock_dir / "loop_daily_news.lock"
    stale.write_text("999999:dead-run", encoding="utf-8")

    clear_stale_locks(lock_dir)

    assert not stale.exists()


def test_live_lock_is_not_cleared(tmp_path: Path) -> None:
    lock_dir = tmp_path / "locks"
    store = FileLockStore(lock_dir, timeout_seconds=1.0)
    with store.acquire("loop:intern", "test-run"):
        live = lock_dir / "loop_intern.lock"
        assert live.exists()
        clear_stale_locks(lock_dir)
        assert live.exists()


def test_acquire_writes_pid_payload(tmp_path: Path) -> None:
    lock_dir = tmp_path / "locks"
    store = FileLockStore(lock_dir, timeout_seconds=1.0)
    with store.acquire("loop:paper", "holder"):
        payload = (lock_dir / "loop_paper.lock").read_text(encoding="utf-8")
    assert payload.startswith(f"{os.getpid()}:")
