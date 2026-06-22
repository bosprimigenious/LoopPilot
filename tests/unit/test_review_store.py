"""Review store unit tests."""

from __future__ import annotations

from pathlib import Path

from loop_pilot.review.store import ReviewStore


def test_review_store_pending_and_decision(tmp_path: Path) -> None:
    db_path = tmp_path / "loop_pilot.db"
    store = ReviewStore(db_path)

    item = store.upsert_pending(run_id="run-001", loop_type="intern", artifact_path="/tmp/run")
    assert item.status == "pending"
    assert item.run_id == "run-001"

    pending = store.list_pending()
    assert len(pending) == 1

    decided = store.record_decision(
        "run-001",
        decision="approve",
        status="approved",
        reason="checked",
    )
    assert decided.decision == "approve"
    assert decided.decided_at is not None

    store.append_event(run_id="run-001", event_type="review_approved", payload={"note": "ok"})


def test_deferred_review_item_survives_sync_until_due_date(tmp_path: Path) -> None:
    from datetime import date, timedelta

    db_path = tmp_path / "loop_pilot.db"
    store = ReviewStore(db_path)

    future = (date.today() + timedelta(days=7)).isoformat()
    store.upsert_pending(run_id="run-deferred", loop_type="intern", artifact_path="/tmp/run")
    store.record_decision(
        "run-deferred",
        decision="defer",
        status="deferred",
        reason="later",
        deferred_until=future,
    )

    item = store.upsert_pending(run_id="run-deferred", loop_type="intern", artifact_path="/tmp/run2")
    assert item.status == "deferred"
    assert item.deferred_until == future

    past = (date.today() - timedelta(days=1)).isoformat()
    store.record_decision(
        "run-deferred",
        decision="defer",
        status="deferred",
        reason="expired",
        deferred_until=past,
    )
    revived = store.upsert_pending(run_id="run-deferred", loop_type="intern", artifact_path="/tmp/run3")
    assert revived.status == "pending"

    store.upsert_pending(run_id="run-approved", loop_type="intern", artifact_path="/tmp/approved")
    store.record_decision("run-approved", decision="approve", status="approved", reason="ok")
    unchanged = store.upsert_pending(run_id="run-approved", loop_type="intern", artifact_path="/tmp/again")
    assert unchanged.status == "approved"
