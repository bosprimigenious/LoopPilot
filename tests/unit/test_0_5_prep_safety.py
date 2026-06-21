"""0.5-prep fail-closed safety tests (Codex review)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from loop_pilot.cli import app
from loop_pilot.config import LoopPilotConfig
from loop_pilot.review.store import ReviewStore
from loop_pilot.scheduler.installer import install_schedule, schedule_status, uninstall_schedule
from loop_pilot.scheduler.install_status import InstallStatus
from loop_pilot.safety.gate import SafetyGate
from loop_pilot.safety.readiness import PREP_STAGE_BLOCKED
from loop_pilot.safety.levels import SafetyLevel


def _config_dir(tmp_path: Path, *, stage: str = "prep", allow_install: bool = True) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "loop-pilot.yaml").write_text(
        "runtime:\n"
        "  state_backend: sqlite\n"
        "  state_dir: var/state\n"
        "  artifact_dir: var/artifacts\n"
        "  sqlite_path: var/state/loop_pilot.db\n"
        "  lock_dir: var/locks\n"
        f"safety:\n  stage: {stage}\n"
        f"schedule:\n  allow_install: {'true' if allow_install else 'false'}\n",
        encoding="utf-8",
    )
    return config_dir


def test_windows_schedule_install_blocked_in_prep(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    config_dir = _config_dir(tmp_path, stage="prep", allow_install=True)
    cfg = LoopPilotConfig(
        safety={"stage": "prep"},
        schedule={"allow_install": True},
        config_dir=config_dir,
    )
    with patch("loop_pilot.scheduler.installer.subprocess.run") as mock_run:
        with pytest.raises(RuntimeError, match="BLOCKED"):
            install_schedule(
                yes=True,
                target="windows-task-scheduler",
                cwd=tmp_path,
                config_dir=config_dir,
                config=cfg,
            )
        mock_run.assert_not_called()


def test_windows_schedule_uninstall_blocked_in_prep(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    cfg = LoopPilotConfig(safety={"stage": "prep"})
    with patch("loop_pilot.scheduler.installer.subprocess.run") as mock_run:
        with pytest.raises(RuntimeError, match="BLOCKED"):
            uninstall_schedule(cwd=tmp_path, config=cfg)
        mock_run.assert_not_called()


def test_cron_marker_only_not_installed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    config_dir = _config_dir(tmp_path, stage="ready", allow_install=True)
    cfg = LoopPilotConfig(
        safety={"stage": "ready"},
        schedule={"allow_install": True},
        config_dir=config_dir,
    )
    result = install_schedule(
        yes=True,
        target="cron",
        cwd=tmp_path,
        config_dir=config_dir,
        config=cfg,
    )
    assert result.install_status == InstallStatus.PREVIEWED
    status = schedule_status(cwd=tmp_path)
    assert status["installed"] is False
    assert status["install_status"] == InstallStatus.PREVIEWED.value
    payload = json.loads((tmp_path / "var/artifacts/schedule/installed.json").read_text(encoding="utf-8"))
    assert payload["install_status"] == InstallStatus.PREVIEWED.value


def test_unattended_daily_blocked_in_prep(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    config_dir = _config_dir(tmp_path, stage="prep")
    result = CliRunner().invoke(
        app,
        [
            "--config-dir",
            str(config_dir),
            "run",
            "daily",
            "--unattended",
            "--safe",
            "--no-dry-run",
        ],
    )
    assert result.exit_code != 0
    assert "BLOCKED" in result.output
    assert PREP_STAGE_BLOCKED in result.output or "0.5-prep" in result.output


def test_deferred_review_preserved_during_sync(tmp_path: Path) -> None:
    db_path = tmp_path / "loop_pilot.db"
    store = ReviewStore(db_path)
    store.upsert_pending(run_id="run-defer", loop_type="intern", artifact_path="/tmp/a")
    store.record_decision(
        "run-defer",
        decision="defer",
        status="deferred",
        reason="later",
        deferred_until="2099-12-31",
    )
    synced = store.upsert_pending(run_id="run-defer", loop_type="intern", artifact_path="/tmp/b")
    assert synced.status == "deferred"
    assert synced.deferred_until == "2099-12-31"
    assert synced.artifact_path == "/tmp/b"


def test_prep_blocks_schedule_install_via_gate(tmp_path: Path) -> None:
    gate = SafetyGate.from_config(
        LoopPilotConfig(
            safety={"stage": "prep"},
            schedule={"allow_install": True},
            runtime={"state_dir": str(tmp_path / "state")},
        )
    )
    result = gate.check("schedule.install", confirm=True)
    assert result.denied and result.reason_code == PREP_STAGE_BLOCKED


def test_prep_blocks_level_3_adapter_invoke(tmp_path: Path) -> None:
    gate = SafetyGate.from_config(
        LoopPilotConfig(
            safety={"stage": "prep"},
            runtime={"state_dir": str(tmp_path / "state")},
        )
    )
    result = gate.check("adapter.invoke", level=SafetyLevel.REAL_GUARDED)
    assert result.denied and result.reason_code == PREP_STAGE_BLOCKED
