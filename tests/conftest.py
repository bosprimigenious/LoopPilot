"""Pytest fixtures shared across unit and integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import sqlite_config_dir as _sqlite_config_dir


@pytest.fixture
def sqlite_config_dir(tmp_path: Path) -> Path:
    return _sqlite_config_dir(tmp_path)
