"""Pytest fixtures shared across unit and integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import sqlite_config_dir as _sqlite_config_dir


@pytest.fixture(scope="session", autouse=True)
def _clean_shared_runtime_locks() -> None:
    lock_dir = Path("var/state/locks")
    if lock_dir.is_dir():
        for lock_path in lock_dir.glob("*.lock"):
            lock_path.unlink(missing_ok=True)
    yield


@pytest.fixture
def sqlite_config_dir(tmp_path: Path) -> Path:
    return _sqlite_config_dir(tmp_path)
