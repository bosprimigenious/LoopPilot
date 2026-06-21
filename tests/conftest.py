"""Pytest fixtures shared across unit and integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from loop_pilot.runtime.locks import clear_stale_locks
from tests.support import sqlite_config_dir as _sqlite_config_dir


@pytest.fixture(scope="session", autouse=True)
def _clean_shared_runtime_locks() -> None:
    clear_stale_locks(Path("var/state/locks"))
    yield


@pytest.fixture
def sqlite_config_dir(tmp_path: Path) -> Path:
    return _sqlite_config_dir(tmp_path)
