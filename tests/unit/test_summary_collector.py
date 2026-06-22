"""Summary collector tests."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.states import RunOutcome, RunPhase
from loop_pilot.review.store import ReviewStore
from loop_pilot.storage.sqlite import SQLiteStateStore
from loop_pilot.summary.collector import SummaryCollector, report_path
from loop_pilot.summary.renderer import render_daily_summary, render_weekly_summary
from loop_pilot.tasks.inbox_service import InboxService
from loop_pilot.tasks.queue_service import QueueService
from loop_pilot.tasks.store import TaskStore
from loop_pilot.tasks.today_service import TodayService


def test_collect_daily_includes_today_and_inbox(tmp_path: Path) -> None:
    db_path = tmp_path / "loop_pilot.db"
    artifact_dir = tmp_path / "artifacts"
    lock_dir = tmp_path / "locks"
    lock_dir.mkdir()

    state = SQLiteStateStore(db_path)
    tasks = TaskStore(db_path)
    inbox = InboxService(tasks)
    queue = QueueService(tasks, inbox)
    today = TodayService(tasks, queue, timezone="UTC")

    created = inbox.add("fix login test", source="manual", loop_hint="intern", priority=2)
    queue_item = queue.promote(created.item.id, loop_type="intern")
    today.add_queue_to_today(queue_item.id)

    record = RunRecord(
        run_id="run-daily-001",
        loop_type="intern",
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.SUCCEEDED,
        started_at=datetime.now(ZoneInfo("UTC")).isoformat(),
    )
    state.save_run(record)

    today_date = today.today_date()
    collector = SummaryCollector(
        state_store=state,
        task_store=tasks,
        artifact_dir=artifact_dir,
        lock_dir=lock_dir,
        timezone="UTC",
    )
    data = collector.collect_daily(today_date)
    markdown = render_daily_summary(data)

    assert len(data.today_items) == 1
    assert any(row.run_id == "run-daily-001" for row in data.runs)
    assert "# Daily Summary" in markdown
    assert "## 2. Today" in markdown


def test_collect_weekly_builds_stats(tmp_path: Path) -> None:
    db_path = tmp_path / "loop_pilot.db"
    state = SQLiteStateStore(db_path)
    tasks = TaskStore(db_path)
    today = datetime.now(ZoneInfo("UTC")).date().isoformat()
    record = RunRecord(
        run_id="run-week-001",
        loop_type="paper",
        phase=RunPhase.TERMINATED,
        outcome=RunOutcome.PARTIAL,
        started_at=f"{today}T10:00:00+00:00",
    )
    state.save_run(record)

    collector = SummaryCollector(
        state_store=state,
        task_store=tasks,
        artifact_dir=tmp_path / "artifacts",
        lock_dir=tmp_path / "locks",
        timezone="UTC",
    )
    iso = datetime.now(ZoneInfo("UTC")).date().isocalendar()
    week_label = f"{iso.year}-W{iso.week:02d}"
    data = collector.collect_weekly(week_label)
    text = render_weekly_summary(data)

    assert "Weekly Summary" in text
    assert data.week == week_label


def test_report_path_prefers_final_report_over_diff_summary(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    run_dir = artifact_dir / "intern" / "run-report-001"
    run_dir.mkdir(parents=True)
    (run_dir / "development-report.md").write_text("# Development report\n", encoding="utf-8")
    (run_dir / "diff-summary.md").write_text("# Diff summary\n", encoding="utf-8")
    manifest = {
        "run_id": "run-report-001",
        "loop_type": "intern",
        "artifacts": [
            {"path": "diff-summary.md", "sha256": "abc", "human_readable": True, "kind": "log"},
            {"path": "development-report.md", "sha256": "def", "human_readable": True, "kind": "report"},
        ],
    }
    (run_dir / "artifact-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    resolved = report_path(artifact_dir, "intern", "run-report-001")
    assert resolved is not None
    assert resolved.endswith("development-report.md")
    assert not resolved.endswith("diff-summary.md")


def _seed_review_run(
    state: SQLiteStateStore,
    *,
    run_id: str,
    today: str,
    review_status: str = "needs_review",
    outcome: RunOutcome = RunOutcome.PARTIAL,
) -> RunRecord:
    record = RunRecord(
        run_id=run_id,
        loop_type="intern",
        phase=RunPhase.TERMINATED,
        outcome=outcome,
        review_status=review_status,
        started_at=f"{today}T10:00:00+00:00",
        finished_at=f"{today}T10:30:00+00:00",
    )
    state.save_run(record)
    return record


def test_deferred_review_item_hidden_from_summary_until_due(tmp_path: Path) -> None:
    db_path = tmp_path / "loop_pilot.db"
    artifact_dir = tmp_path / "artifacts"
    lock_dir = tmp_path / "locks"
    lock_dir.mkdir()

    state = SQLiteStateStore(db_path)
    tasks = TaskStore(db_path)
    review_store = ReviewStore(db_path)
    today = datetime.now(ZoneInfo("UTC")).date().isoformat()
    run_id = "run-deferred-future"
    _seed_review_run(state, run_id=run_id, today=today)
    review_store.upsert_pending(run_id=run_id, loop_type="intern", artifact_path=str(artifact_dir))
    review_store.record_decision(
        run_id,
        decision="defer",
        status="deferred",
        reason="later",
        deferred_until="2099-01-01",
    )

    collector = SummaryCollector(
        state_store=state,
        task_store=tasks,
        artifact_dir=artifact_dir,
        lock_dir=lock_dir,
        timezone="UTC",
        review_store=review_store,
    )
    data = collector.collect_daily(today)

    assert not any(row.run_id == run_id for row in data.needs_review)


def test_deferred_review_item_reappears_after_due(tmp_path: Path) -> None:
    db_path = tmp_path / "loop_pilot.db"
    artifact_dir = tmp_path / "artifacts"
    lock_dir = tmp_path / "locks"
    lock_dir.mkdir()

    state = SQLiteStateStore(db_path)
    tasks = TaskStore(db_path)
    review_store = ReviewStore(db_path)
    today = datetime.now(ZoneInfo("UTC")).date().isoformat()
    due_date = (datetime.now(ZoneInfo("UTC")).date() - timedelta(days=1)).isoformat()
    run_id = "run-deferred-due"
    _seed_review_run(state, run_id=run_id, today=today)
    review_store.upsert_pending(run_id=run_id, loop_type="intern", artifact_path=str(artifact_dir))
    review_store.record_decision(
        run_id,
        decision="defer",
        status="deferred",
        reason="was deferred",
        deferred_until=due_date,
    )

    collector = SummaryCollector(
        state_store=state,
        task_store=tasks,
        artifact_dir=artifact_dir,
        lock_dir=lock_dir,
        timezone="UTC",
        review_store=review_store,
    )
    data = collector.collect_daily(today)

    assert any(row.run_id == run_id for row in data.needs_review)


def test_summary_needs_review_matches_review_list_for_deferred(tmp_path: Path) -> None:
    db_path = tmp_path / "loop_pilot.db"
    artifact_dir = tmp_path / "artifacts"
    lock_dir = tmp_path / "locks"
    lock_dir.mkdir()

    state = SQLiteStateStore(db_path)
    tasks = TaskStore(db_path)
    review_store = ReviewStore(db_path)
    today = datetime.now(ZoneInfo("UTC")).date().isoformat()
    run_id = "run-deferred-align"
    _seed_review_run(state, run_id=run_id, today=today)
    review_store.upsert_pending(run_id=run_id, loop_type="intern", artifact_path=str(artifact_dir))
    review_store.record_decision(
        run_id,
        decision="defer",
        status="deferred",
        reason="align",
        deferred_until="2099-06-01",
    )

    collector = SummaryCollector(
        state_store=state,
        task_store=tasks,
        artifact_dir=artifact_dir,
        lock_dir=lock_dir,
        timezone="UTC",
        review_store=review_store,
    )
    data = collector.collect_daily(today)
    pending_ids = {item.run_id for item in review_store.list_pending()}

    summary_ids = {row.run_id for row in data.needs_review}
    assert run_id not in summary_ids
    assert run_id not in pending_ids


def _seed_decided_review_run(
    tmp_path: Path,
    *,
    run_id: str,
    today: str,
    review_status: str,
    outcome: RunOutcome,
    decision_status: str,
    decision: str,
) -> tuple[SQLiteStateStore, TaskStore, ReviewStore, SummaryCollector]:
    db_path = tmp_path / "loop_pilot.db"
    artifact_dir = tmp_path / "artifacts"
    lock_dir = tmp_path / "locks"
    lock_dir.mkdir()

    state = SQLiteStateStore(db_path)
    tasks = TaskStore(db_path)
    review_store = ReviewStore(db_path)
    run_dir = artifact_dir / "intern" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "gate_result.json").write_text('{"gate":"blocked"}', encoding="utf-8")

    record = RunRecord(
        run_id=run_id,
        loop_type="intern",
        phase=RunPhase.TERMINATED,
        outcome=outcome,
        review_status=review_status,
        started_at=f"{today}T10:00:00+00:00",
        finished_at=f"{today}T10:30:00+00:00",
    )
    state.save_run(record)
    review_store.upsert_pending(run_id=run_id, loop_type="intern", artifact_path=str(run_dir))
    review_store.record_decision(
        run_id,
        decision=decision,
        status=decision_status,
        reason=f"{decision_status} in test",
    )

    collector = SummaryCollector(
        state_store=state,
        task_store=tasks,
        artifact_dir=artifact_dir,
        lock_dir=lock_dir,
        timezone="UTC",
        review_store=review_store,
    )
    return state, tasks, review_store, collector


def test_rejected_review_item_not_in_summary_needs_review(tmp_path: Path) -> None:
    today = datetime.now(ZoneInfo("UTC")).date().isoformat()
    _, _, _, collector = _seed_decided_review_run(
        tmp_path,
        run_id="run-rejected-summary",
        today=today,
        review_status="rejected",
        outcome=RunOutcome.BLOCKED,
        decision_status="rejected",
        decision="reject",
    )
    data = collector.collect_daily(today)
    assert not any(row.run_id == "run-rejected-summary" for row in data.needs_review)


def test_cancelled_review_item_not_in_summary_needs_review(tmp_path: Path) -> None:
    today = datetime.now(ZoneInfo("UTC")).date().isoformat()
    _, _, _, collector = _seed_decided_review_run(
        tmp_path,
        run_id="run-cancelled-summary",
        today=today,
        review_status="cancelled",
        outcome=RunOutcome.CANCELLED,
        decision_status="cancelled",
        decision="cancel",
    )
    data = collector.collect_daily(today)
    assert not any(row.run_id == "run-cancelled-summary" for row in data.needs_review)


def test_approved_review_item_not_in_summary_needs_review(tmp_path: Path) -> None:
    today = datetime.now(ZoneInfo("UTC")).date().isoformat()
    _, _, _, collector = _seed_decided_review_run(
        tmp_path,
        run_id="run-approved-summary",
        today=today,
        review_status="approved",
        outcome=RunOutcome.BLOCKED,
        decision_status="approved",
        decision="approve",
    )
    data = collector.collect_daily(today)
    assert not any(row.run_id == "run-approved-summary" for row in data.needs_review)
