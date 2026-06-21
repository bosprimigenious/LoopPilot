"""Inbox CLI integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from loop_pilot.cli import app


@pytest.fixture
def runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CliRunner:
    monkeypatch.chdir(tmp_path)
    return CliRunner()


def test_inbox_add_and_list_cli(runner: CliRunner, sqlite_config_dir: Path) -> None:
    config_dir = sqlite_config_dir
    add_result = runner.invoke(
        app,
        [
            "--config-dir",
            str(config_dir),
            "inbox",
            "add",
            "fix bug",
            "--source",
            "manual",
            "--loop",
            "intern",
            "--priority",
            "2",
        ],
    )
    assert add_result.exit_code == 0, add_result.output
    assert "Inbox item created:" in add_result.output

    list_result = runner.invoke(app, ["--config-dir", str(config_dir), "inbox", "list"])
    assert list_result.exit_code == 0, list_result.output
    assert "fix bug" in list_result.output
    assert "manual" in list_result.output


def test_inbox_requires_sqlite_backend(runner: CliRunner, tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "loop-pilot.yaml").write_text("runtime:\n  state_backend: json\n", encoding="utf-8")
    for name in ("intern.yaml", "paper.yaml", "daily_news.yaml", "policies.yaml", "sources.yaml", "models.yaml"):
        (config_dir / name).write_text("{}\n", encoding="utf-8")

    result = runner.invoke(app, ["--config-dir", str(config_dir), "inbox", "list"])
    assert result.exit_code != 0
    assert "state_backend=sqlite" in result.output
