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
