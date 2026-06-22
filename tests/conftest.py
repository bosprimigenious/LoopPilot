"""Pytest fixtures shared across unit and integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.runtime.locks import clear_repo_runtime_locks, clear_stale_locks
from tests.support import sqlite_config_dir as _sqlite_config_dir

_SHARED_LOCK_DIRS = (Path("var/state/locks"), Path("var/locks"))
_REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def _clean_shared_runtime_locks() -> None:
    clear_repo_runtime_locks(_REPO_ROOT)
    for lock_dir in _SHARED_LOCK_DIRS:
        clear_stale_locks(lock_dir)
    yield
    clear_repo_runtime_locks(_REPO_ROOT)
    for lock_dir in _SHARED_LOCK_DIRS:
        clear_stale_locks(lock_dir)


@pytest.fixture(autouse=True)
def _clean_runtime_locks_per_test() -> None:
    clear_repo_runtime_locks(_REPO_ROOT)
    yield
    clear_repo_runtime_locks(_REPO_ROOT)


@pytest.fixture
def sqlite_config_dir(tmp_path: Path) -> Path:
    return _sqlite_config_dir(tmp_path)
