"""Integration: schedule install gated by SafetyGate."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from loop_pilot.cli import app


def _config(tmp_path: Path, *, allow_install: bool) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "loop-pilot.yaml").write_text(
        "runtime:\n  state_backend: sqlite\n  state_dir: var/state\n  artifact_dir: var/artifacts\n  sqlite_path: var/state/loop_pilot.db\n  lock_dir: var/locks\n"
        f"schedule:\n  allow_install: {'true' if allow_install else 'false'}\n",
        encoding="utf-8",
    )
    return config_dir


def test_install_denied_without_policy(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["--config-dir", str(_config(tmp_path, allow_install=False)), "schedule", "install", "--yes", "--confirm-schedule", "--target", "cron"])
    assert result.exit_code != 0 and "SafetyGate denied" in result.output


def test_dry_run_unchanged(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["--config-dir", str(_config(tmp_path, allow_install=False)), "schedule", "install", "--dry-run", "--target", "cron"])
    assert result.exit_code == 0 and (tmp_path / "var/artifacts/schedule/schedule-preview.md").is_file()


def test_install_allowed_writes_marker(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["--config-dir", str(_config(tmp_path, allow_install=True)), "schedule", "install", "--yes", "--confirm-schedule", "--target", "cron"])
    assert result.exit_code == 0, result.output
    payload = json.loads((tmp_path / "var/artifacts/schedule/installed.json").read_text(encoding="utf-8"))
    assert "run daily --unattended --safe" in payload["command"]
