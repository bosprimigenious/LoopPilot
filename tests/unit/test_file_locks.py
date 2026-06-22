"""File lock stale detection and cleanup."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from loop_pilot.runtime.locks import FileLockStore, _pid_alive, clear_stale_locks


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


def test_unknown_legacy_lock_payload_is_not_treated_as_stale(tmp_path: Path) -> None:
    lock_dir = tmp_path / "locks"
    lock_dir.mkdir()
    legacy = lock_dir / "loop_legacy.lock"
    legacy.write_text("legacy-holder-only", encoding="utf-8")

    clear_stale_locks(lock_dir)

    assert legacy.exists()


def test_dead_pid_lock_is_stale(tmp_path: Path) -> None:
    lock_dir = tmp_path / "locks"
    lock_dir.mkdir()
    stale = lock_dir / "loop_dead.lock"
    stale.write_text("999999:dead-run", encoding="utf-8")

    store = FileLockStore(lock_dir, timeout_seconds=0.1)
    assert store._lock_is_stale(stale)
    clear_stale_locks(lock_dir)
    assert not stale.exists()


def test_live_pid_lock_is_not_stale(tmp_path: Path) -> None:
    lock_dir = tmp_path / "locks"
    store = FileLockStore(lock_dir, timeout_seconds=1.0)
    with store.acquire("loop:live", "holder"):
        live = lock_dir / "loop_live.lock"
        assert live.exists()
        assert not store._lock_is_stale(live)


@pytest.mark.skipif(os.name == "nt", reason="os.kill PID probe is Unix-only")
def test_permission_error_pid_treated_as_alive(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_kill(pid: int, sig: int) -> None:
        raise PermissionError("Operation not permitted")

    monkeypatch.setattr(os, "kill", fake_kill)
    assert _pid_alive(12345) is True


@pytest.mark.skipif(os.name == "nt", reason="os.kill PID probe is Unix-only")
def test_permission_error_pid_treated_as_alive_lock_not_stale(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_kill(pid: int, sig: int) -> None:
        raise PermissionError("Operation not permitted")

    monkeypatch.setattr(os, "kill", fake_kill)
    lock_dir = tmp_path / "locks"
    lock_dir.mkdir()
    lock = lock_dir / "loop_perm.lock"
    lock.write_text("12345:other-user", encoding="utf-8")

    store = FileLockStore(lock_dir, timeout_seconds=0.1)
    assert not store._lock_is_stale(lock)
    clear_stale_locks(lock_dir)
    assert lock.exists()
