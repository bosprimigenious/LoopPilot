"""Queue CLI integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from loop_pilot.cli import app


def test_queue_promote_and_list_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, sqlite_config_dir: Path) -> None:
    monkeypatch.chdir(tmp_path)
    config_dir = sqlite_config_dir
    runner = CliRunner()

    add_result = runner.invoke(
        app,
        ["--config-dir", str(config_dir), "inbox", "add", "fix login test", "--loop", "intern"],
    )
    assert add_result.exit_code == 0, add_result.output
    inbox_id = add_result.output.strip().split(": ")[-1]

    promote_result = runner.invoke(
        app,
        ["--config-dir", str(config_dir), "queue", "promote", inbox_id, "--loop", "intern"],
    )
    assert promote_result.exit_code == 0, promote_result.output
    assert "Queue item created:" in promote_result.output

    list_result = runner.invoke(app, ["--config-dir", str(config_dir), "queue", "list"])
    assert list_result.exit_code == 0, list_result.output
    assert "fix login test" in list_result.output
    assert "intern" in list_result.output
