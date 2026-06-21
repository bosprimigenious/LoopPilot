"""0.4-a recovery scan tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.runtime.recovery_scan import scan_recovery
from loop_pilot.storage.sqlite import SQLiteStateStore


def test_scan_finds_waiting_approval_and_acting_runs(tmp_path: Path) -> None:
    store = SQLiteStateStore(tmp_path / "state.db")
    waiting = RunRecord(
        run_id="wait-001",
        loop_type="intern",
        phase=RunPhase.WAITING_APPROVAL,
    )
    acting = RunRecord(
        run_id="act-001",
        loop_type="intern",
        phase=RunPhase.ACTING,
    )
    store.save_run(waiting)
    store.save_run(acting)

    findings = scan_recovery(store, lock_dir=tmp_path / "locks")
    by_id = {item.run_id: item for item in findings}

    assert by_id["wait-001"].category == "waiting_approval"
    assert by_id["wait-001"].recommended_action == "needs_human"
    assert by_id["act-001"].category == "acting_interrupted"
    assert by_id["act-001"].recommended_action == "manual_review_required"


def test_scan_finds_failed_and_stale_lock(tmp_path: Path) -> None:
    store = SQLiteStateStore(tmp_path / "state.db")
    failed = RunRecord(
        run_id="fail-001",
        loop_type="paper",
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.FAILED,
        terminal_reason="simulated failure",
    )
    store.save_run(failed)

    lock_dir = tmp_path / "locks"
    lock_dir.mkdir()
    (lock_dir / "loop_intern.lock").write_text("stale-run", encoding="utf-8")

    findings = scan_recovery(store, lock_dir=lock_dir)
    categories = {item.category for item in findings}
    assert "failed_run" in categories
    assert "stale_lock" in categories


def test_scan_flags_stale_non_terminal_run(tmp_path: Path) -> None:
    store = SQLiteStateStore(tmp_path / "state.db")
    stale_time = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    record = RunRecord(
        run_id="stale-001",
        loop_type="intern",
        phase=RunPhase.PLANNING,
        started_at=stale_time,
    )
    store.save_run(record)

    findings = scan_recovery(
        store,
        lock_dir=tmp_path / "locks",
        stale_after=timedelta(hours=24),
    )
    assert any(item.run_id == "stale-001" and item.category == "stale_run" for item in findings)


def test_scan_returns_empty_for_json_store(tmp_path: Path) -> None:
    from loop_pilot.storage.json_store import JsonStateStore

    store = JsonStateStore(tmp_path / "state")
    assert scan_recovery(store, lock_dir=tmp_path / "locks") == []
