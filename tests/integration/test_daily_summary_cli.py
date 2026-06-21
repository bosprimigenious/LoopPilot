"""0.4-d summary and daily run CLI integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from loop_pilot.cli import app


def _sqlite_config_dir(tmp_path: Path) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "loop-pilot.yaml").write_text(
        "\n".join(
            [
                "runtime:",
                "  state_backend: sqlite",
                "  timezone: UTC",
                f"  state_dir: {tmp_path / 'state'}",
                f"  artifact_dir: {tmp_path / 'artifacts'}",
                f"  sqlite_path: {tmp_path / 'state' / 'loop_pilot.db'}",
                f"  lock_dir: {tmp_path / 'locks'}",
            ]
        ),
        encoding="utf-8",
    )
    for name in ("intern.yaml", "paper.yaml", "daily_news.yaml", "policies.yaml", "sources.yaml", "models.yaml"):
        (config_dir / name).write_text("{}\n", encoding="utf-8")
    return config_dir


def test_summary_today_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_dir = _sqlite_config_dir(tmp_path)
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["--config-dir", str(config_dir), "summary", "today"])
    assert result.exit_code == 0, result.output
    assert "Daily summary:" in result.output
    summaries = list((tmp_path / "artifacts" / "daily").rglob("daily-summary.md"))
    assert summaries


def test_summary_week_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_dir = _sqlite_config_dir(tmp_path)
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["--config-dir", str(config_dir), "summary", "week"])
    assert result.exit_code == 0, result.output
    assert "Weekly summary:" in result.output


def test_schedule_print_and_install_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_dir = _sqlite_config_dir(tmp_path)
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    for args in (
        ["--config-dir", str(config_dir), "schedule", "print"],
        ["--config-dir", str(config_dir), "schedule", "print", "--target", "cron"],
        ["--config-dir", str(config_dir), "schedule", "install", "--dry-run"],
    ):
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output


def test_run_daily_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_dir = _sqlite_config_dir(tmp_path)
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["--config-dir", str(config_dir), "run", "daily", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Daily run (dry-run)" in result.output
    assert "summary:" in result.output
