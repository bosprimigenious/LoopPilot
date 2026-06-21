"""V1 SQLite StateStore contract tests."""

from __future__ import annotations

from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.storage.sqlite import SQLiteStateStore


def test_sqlite_store_persists_runs_checkpoints_and_reviews(tmp_path) -> None:
    store = SQLiteStateStore(tmp_path / "state.db")
    record = RunRecord(
        run_id="v1-sqlite-001",
        loop_type="intern",
        phase=RunPhase.WAITING_APPROVAL,
        outcome=None,
        last_checkpoint_id="cp-001",
    )

    store.save_run(record)
    store.save_checkpoint(
        record.run_id,
        checkpoint_id="cp-001",
        phase=RunPhase.WAITING_APPROVAL.value,
        payload={"pending_action": "approve"},
    )
    store.record_review(record.run_id, decision="needs_more_info", reason="need focused diff")

    loaded = store.get_run(record.run_id)
    checkpoint = store.latest_checkpoint(record.run_id)
    reviews = store.list_reviews(record.run_id)

    assert loaded is not None
    assert loaded.phase == RunPhase.WAITING_APPROVAL
    assert loaded.last_checkpoint_id == "cp-001"
    assert checkpoint is not None
    assert checkpoint["checkpoint_id"] == "cp-001"
    assert checkpoint["payload"]["pending_action"] == "approve"
    assert reviews[-1]["decision"] == "needs_more_info"
    assert reviews[-1]["reason"] == "need focused diff"


def test_sqlite_store_lists_recent_runs_by_update_order(tmp_path) -> None:
    store = SQLiteStateStore(tmp_path / "state.db")
    first = RunRecord(run_id="run-1", loop_type="intern", phase=RunPhase.TERMINATED)
    second = RunRecord(
        run_id="run-2",
        loop_type="paper",
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.BLOCKED,
    )

    store.save_run(first)
    store.save_run(second)

    assert [record.run_id for record in store.list_runs(limit=2)] == ["run-2", "run-1"]
