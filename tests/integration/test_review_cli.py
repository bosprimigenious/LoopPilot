"""Review CLI integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from loop_pilot.app import App
from loop_pilot.cli import app
from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome, RunPhase


def _sqlite_config_dir(tmp_path: Path) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "loop-pilot.yaml").write_text(
        "\n".join(
            [
                "runtime:",
                "  state_backend: sqlite",
                f"  state_dir: {tmp_path / 'state'}",
                f"  artifact_dir: {tmp_path / 'artifacts'}",
                f"  sqlite_path: {tmp_path / 'state' / 'loop_pilot.db'}",
                f"  lock_dir: {tmp_path / 'locks'}",
                "  timezone: UTC",
            ]
        ),
        encoding="utf-8",
    )
    for name in ("intern.yaml", "paper.yaml", "daily_news.yaml", "policies.yaml", "sources.yaml", "models.yaml"):
        (config_dir / name).write_text("{}\n", encoding="utf-8")
    return config_dir


def _seed_waiting_run(tmp_path: Path) -> tuple[Path, str]:
    config_dir = _sqlite_config_dir(tmp_path)
    application = App.from_config_dir(config_dir)
    run_id = "review-cli-001"
    record = RunRecord(
        run_id=run_id,
        loop_type="intern",
        phase=RunPhase.WAITING_APPROVAL,
        outcome=RunOutcome.PARTIAL,
        review_status="pending",
    )
    application.state_store.save_run(record)
    run_dir = tmp_path / "artifacts" / "intern" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "review_required.md").write_text("# Review\n", encoding="utf-8")
    (run_dir / "gate_result.json").write_text('{"gate":"needs_review"}', encoding="utf-8")
    return config_dir, run_id


def test_review_list_and_reject(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_dir, run_id = _seed_waiting_run(tmp_path)
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    list_result = runner.invoke(app, ["--config-dir", str(config_dir), "review", "list"])
    assert list_result.exit_code == 0, list_result.output
    assert run_id in list_result.output

    reject_no_reason = runner.invoke(app, ["--config-dir", str(config_dir), "reject", run_id])
    assert reject_no_reason.exit_code != 0

    reject_result = runner.invoke(
        app,
        ["--config-dir", str(config_dir), "reject", run_id, "--reason", "too risky"],
    )
    assert reject_result.exit_code == 0, reject_result.output

    show_result = runner.invoke(app, ["--config-dir", str(config_dir), "review", "show", run_id])
    assert show_result.exit_code == 0
    assert "too risky" in show_result.output or "reject" in show_result.output
