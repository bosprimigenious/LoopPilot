"""Pytest fixtures shared across unit and integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.runtime.locks import clear_stale_locks
from tests.support import sqlite_config_dir as _sqlite_config_dir

_SHARED_LOCK_DIRS = (Path("var/state/locks"), Path("var/locks"))


@pytest.fixture(scope="session", autouse=True)
def _clean_shared_runtime_locks() -> None:
    for lock_dir in _SHARED_LOCK_DIRS:
        clear_stale_locks(lock_dir)
    yield
    for lock_dir in _SHARED_LOCK_DIRS:
        clear_stale_locks(lock_dir)


@pytest.fixture
def sqlite_config_dir(tmp_path: Path) -> Path:
    return _sqlite_config_dir(tmp_path)
