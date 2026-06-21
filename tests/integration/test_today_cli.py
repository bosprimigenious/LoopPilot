"""Today CLI integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from loop_pilot.cli import app


def test_today_add_queue_and_show(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, sqlite_config_dir: Path) -> None:
    monkeypatch.chdir(tmp_path)
    config_dir = sqlite_config_dir
    runner = CliRunner()

    add_result = runner.invoke(
        app,
        ["--config-dir", str(config_dir), "inbox", "add", "today focus", "--loop", "intern"],
    )
    inbox_id = add_result.output.strip().split(": ")[-1]

    promote_result = runner.invoke(
        app,
        ["--config-dir", str(config_dir), "queue", "promote", inbox_id, "--loop", "intern"],
    )
    queue_id = promote_result.output.strip().split("Queue item created: ")[1].split()[0]

    schedule_result = runner.invoke(
        app,
        ["--config-dir", str(config_dir), "today", "add-queue", queue_id],
    )
    assert schedule_result.exit_code == 0, schedule_result.output

    today_result = runner.invoke(app, ["--config-dir", str(config_dir), "today"])
    assert today_result.exit_code == 0, today_result.output
    assert "Today:" in today_result.output
    assert "today focus" in today_result.output
