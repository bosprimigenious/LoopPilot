"""0.4-a database operations tests."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from click.testing import CliRunner

from loop_pilot.cli import app
from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.storage.db_ops import (
    get_db_status,
    migrate_database,
    plan_backup,
    verify_database,
)
from loop_pilot.storage.migrations import CURRENT_SCHEMA_VERSION, plan_migrations
from loop_pilot.storage.sqlite import SQLiteStateStore


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
            ]
        ),
        encoding="utf-8",
    )
    for name in ("intern.yaml", "paper.yaml", "daily_news.yaml", "policies.yaml", "sources.yaml", "models.yaml"):
        (config_dir / name).write_text("{}\n", encoding="utf-8")
    return config_dir


def test_migrate_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    first = migrate_database(db_path, dry_run=False)
    second = migrate_database(db_path, dry_run=False)
    dry_run_pending = migrate_database(db_path, dry_run=True)

    assert first == list(range(1, CURRENT_SCHEMA_VERSION + 1))
    assert second == []
    assert dry_run_pending == []

    with __import__("sqlite3").connect(db_path) as conn:
        assert plan_migrations(conn) == []
        from loop_pilot.storage.migrations import get_current_schema_version

        assert get_current_schema_version(conn) == CURRENT_SCHEMA_VERSION


def test_verify_detects_orphan_checkpoint(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    migrate_database(db_path)
    store = SQLiteStateStore(db_path)
    store.save_checkpoint(
        "missing-run",
        checkpoint_id="cp-orphan",
        phase=RunPhase.ACTING.value,
        payload={"resume_allowed": False},
    )

    report = verify_database(db_path, tmp_path / "artifacts")
    codes = {issue.code for issue in report.issues}
    assert "orphan_checkpoint" in codes
    assert report.ok is False


def test_verify_ok_after_valid_run(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    migrate_database(db_path)
    store = SQLiteStateStore(db_path)
    record = RunRecord(
        run_id="verify-001",
        loop_type="intern",
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.SUCCEEDED,
    )
    store.save_run(record)
    store.save_artifact_manifest(record.run_id, {"run_id": record.run_id, "loop_type": "intern"})

    report = verify_database(db_path, tmp_path / "artifacts")
    assert report.ok is True


def test_backup_plan_never_overwrites_existing_root(tmp_path: Path) -> None:
    db_path = tmp_path / "loop_pilot.db"
    migrate_database(db_path)
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    stamp = "20260621T120000"
    existing = backup_dir / stamp
    existing.mkdir()

    plan_one = plan_backup(
        db_path=db_path,
        state_dir=tmp_path / "state",
        config_dir=tmp_path / "config",
        backup_dir=backup_dir,
        dry_run=False,
    )
    # Force same-second collision behavior by pre-creating the first candidate path.
    first_root = backup_dir / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    first_root.mkdir(parents=True, exist_ok=True)

    plan_two = plan_backup(
        db_path=db_path,
        state_dir=tmp_path / "state",
        config_dir=tmp_path / "config",
        backup_dir=backup_dir,
        dry_run=False,
    )

    assert plan_one.sources
    assert plan_two.sources
    assert plan_two.sources[0][1].parent != first_root
    assert existing.exists()


def test_db_status_reports_schema_and_locks(tmp_path: Path) -> None:
    db_path = tmp_path / "state" / "loop_pilot.db"
    lock_dir = tmp_path / "locks"
    lock_dir.mkdir(parents=True)
    (lock_dir / "loop_intern.lock").write_text("run-1", encoding="utf-8")
    migrate_database(db_path)

    status = get_db_status(backend="sqlite", db_path=db_path, lock_dir=lock_dir)
    assert status.schema_version == CURRENT_SCHEMA_VERSION
    assert status.pending_migrations == []
    assert "loop_intern.lock" in status.lock_files


def test_db_cli_requires_sqlite_backend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "loop-pilot.yaml").write_text("runtime:\n  state_backend: json\n", encoding="utf-8")
    for name in ("intern.yaml", "paper.yaml", "daily_news.yaml", "policies.yaml", "sources.yaml", "models.yaml"):
        (config_dir / name).write_text("{}\n", encoding="utf-8")

    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["--config-dir", str(config_dir), "db", "migrate"])
    assert result.exit_code != 0
    assert "state_backend=sqlite" in result.output


def test_db_cli_migrate_and_verify(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_dir = _sqlite_config_dir(tmp_path)
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    migrate_result = runner.invoke(app, ["--config-dir", str(config_dir), "db", "migrate"])
    assert migrate_result.exit_code == 0
    assert "Applied migrations" in migrate_result.output or "up to date" in migrate_result.output

    verify_result = runner.invoke(app, ["--config-dir", str(config_dir), "db", "verify"])
    assert verify_result.exit_code == 0
    assert "Verify: OK" in verify_result.output

    status_result = runner.invoke(app, ["--config-dir", str(config_dir), "db", "status"])
    assert status_result.exit_code == 0
    assert "backend: sqlite" in status_result.output
